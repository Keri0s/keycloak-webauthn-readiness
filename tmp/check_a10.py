"""A10 with positive control and two in-memory fault injections."""
import hashlib,json,sys
from pathlib import Path
from uuid import uuid4
from types import SimpleNamespace
from unittest.mock import patch
from contextlib import nullcontext
import django
from django.conf import settings
from django.contrib.auth import get_user_model,get_user
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied
from django.db import connection,transaction
from django.test import Client,RequestFactory,override_settings
from django.utils import timezone
from authn.models import ExternalIdentity,OIDCSessionGroup,SessionBinding,SIDRevocationMarker
from authn.services import create_verified_session
from authn import views
assert __debug__ and connection.vendor=='postgresql' and connection.get_autocommit()
root=Path(settings.BASE_DIR).parents[1]
out=root/'docs/validation/a10-2026-11-18';out.mkdir(parents=True,exist_ok=True)
files=list((root/'apps/lab/authn').glob('*.py'))+[root/'tmp/check_a10.py']
def hashes():return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
before=hashes();results=[]; started=timezone.now().isoformat(); original=views.require_active_binding

def run(mode):
 prefix='probe-a10-'+uuid4().hex;keys=set();User=get_user_model();error=None;point=None;observed={}
 try:
  with transaction.atomic():
   user=User.objects.create_user(username=prefix,password=None)
   ExternalIdentity.objects.create(issuer=settings.OIDC_ISSUER,subject=prefix,user=user)
   req=RequestFactory().get('/');req.session=SessionStore();req.user=AnonymousUser()
   bound=create_verified_session(req,issuer=settings.OIDC_ISSUER,client_id=settings.OIDC_CLIENT_ID,sid=prefix,subject=prefix)
   keys.add(bound.session_key)
  orphan=Client(HTTP_HOST='app.readiness.test');orphan.force_login(user,backend='django.contrib.auth.backends.ModelBackend')
  orphan_key=orphan.cookies[settings.SESSION_COOKIE_NAME].value;keys.add(orphan_key)
  assert not connection.in_atomic_block
  req=RequestFactory().get('/');req.session=SessionStore(session_key=orphan_key)
  assert get_user(req).pk==user.pk
  assert not SessionBinding.objects.filter(session_key=orphan_key).exists()
  assert not user.has_usable_password()
  observed.update(input_authenticated=True,input_binding_exists=False,local_password_available=False)
  valid=Client(HTTP_HOST='app.readiness.test');valid.cookies[settings.SESSION_COOKIE_NAME]=bound.session_key
  def bypass(request): return SimpleNamespace(user=request.user)
  def deny(request):raise PermissionDenied('Injected deny-all')
  context=nullcontext() if mode=='baseline' else patch.object(views,'require_active_binding',bypass if mode=='bypass-binding' else deny)
  try:
   with context,override_settings(DEBUG=False),patch('django.contrib.auth.authenticate',side_effect=AssertionError('unexpected local authentication')) as auth:
    response=orphan.get('/private/',secure=True);observed['orphan_http']=response.status_code
    assert response.status_code==403,'orphan_denied'
    assert response.wsgi_request.user.pk==user.pk,'backend_identity_preserved'
    assert not SessionBinding.objects.filter(session_key=orphan_key).exists(),'no_binding_created'
    control=valid.get('/private/',secure=True);observed['valid_http']=control.status_code
    assert control.status_code==200,'valid_allowed'
    assert control.wsgi_request.user.pk==user.pk,'valid_identity'
    auth.assert_not_called();observed['local_password_fallback_used']=False
  except AssertionError as exc:
   error='AssertionError';point=str(exc)
 finally:
  with transaction.atomic():
   scoped=SessionBinding.objects.filter(user__username=prefix);keys.update(scoped.values_list('session_key',flat=True))
   Session.objects.filter(session_key__in=keys).delete();scoped.delete()
   OIDCSessionGroup.objects.filter(sid=prefix).delete();SIDRevocationMarker.objects.filter(sid=prefix).delete()
   User.objects.filter(username=prefix).delete()
  assert not Session.objects.filter(session_key__in=keys).exists()
  assert not SessionBinding.objects.filter(session_key__in=keys).exists()
  assert not OIDCSessionGroup.objects.filter(sid=prefix).exists()
  assert not SIDRevocationMarker.objects.filter(sid=prefix).exists()
  assert not User.objects.filter(username=prefix).exists()
  assert not ExternalIdentity.objects.filter(subject=prefix).exists()
 expected={'baseline':None,'bypass-binding':'orphan_denied','deny-all':'valid_allowed'}[mode]
 assert point==expected,(mode,point)
 row=dict(mode=mode,observed=observed,outcome='PASS' if error is None else 'EXPECTED_ASSERTION_FAILURE',assertion=point,cleanup_verified=True)
 results.append(row);print(json.dumps(row),flush=True)
try:
 for mode in ('baseline','bypass-binding','deny-all'):run(mode)
finally:
 meta=dict(case='A10',started_at=started,finished_at=timezone.now().isoformat(),python=sys.version.split()[0],django=django.get_version(),database=connection.vendor,source_hashes=before,source_unchanged=before==hashes(),guard_restored=views.require_active_binding is original,results=results)
 (out/'results.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
assert len(results)==3 and meta['source_unchanged'] and meta['guard_restored']
print('A10 baseline PASS; both selected faults detected; cleanup verified.')
