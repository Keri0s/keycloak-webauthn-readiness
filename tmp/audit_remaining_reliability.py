import ast, hashlib, inspect, json, traceback
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch
from datetime import datetime, timezone
from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied
from django.utils import timezone as tz
from authn import services as s
from authn import views as v
from authn.models import SessionBinding, SIDRevocationMarker
assert __debug__
root=Path(settings.BASE_DIR).parents[1]
out=root/'docs/validation/remaining-reliability-2026-11-18'
out.mkdir(parents=True,exist_ok=True)
files=list((root/'apps/lab/authn').glob('*.py'))+[root/'apps/lab/config/oidc.py']+list((root/'tmp').glob('check_a*.py'))+[root/'tmp/audit_remaining_reliability.py']
def hashes(): return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
before=hashes(); results=[]; started=datetime.now(timezone.utc).isoformat()
revoke=s.revoke_verified_sid; create=s.create_verified_session

def mutated_create():
    tree=ast.parse(inspect.getsource(create))
    nodes=[n for n in ast.walk(tree) if isinstance(n,ast.If) and ast.unparse(n.test)=='group.subject != subject']
    assert len(nodes)==1
    nodes[0].body=[ast.copy_location(ast.Pass(),nodes[0].body[0])]
    ast.fix_missing_locations(tree); ns=dict(vars(s))
    exec(compile(tree,'<removed-owner-guard>','exec'),ns)
    return ns['create_verified_session']

def run(case,kind):
    filename='check_a3_a5.py' if case in ('A3','A4','A5') else 'check_'+case.lower()+'.py'
    path=root/'tmp'/filename; source=path.read_text(encoding='utf-8')
    if case in ('A3','A4','A5'):
        source=source.replace('for case_id in ("A3", "A4", "A5"):',f'for case_id in ("{case}",):')
    calls=0; revoke_calls=0
    def bad_revoke(**kw):
        nonlocal revoke_calls
        revoke_calls+=1
        target=list(SessionBinding.objects.filter(group__issuer=kw['issuer'],group__client_id=kw['client_id'],group__sid=kw['sid']).values('session_key'))
        saved=list(Session.objects.filter(session_key__in=[x['session_key'] for x in target]).values())
        result=revoke(**kw)
        if case=='A3':
            # Wrongly delete another SID of the same subject, preserving counts.
            keys=SessionBinding.objects.filter(group__issuer=kw['issuer'],group__client_id=kw['client_id'],group__subject=kw['subject']).exclude(group__sid=kw['sid']).values_list('session_key',flat=True)
            Session.objects.filter(session_key__in=keys).delete()
        elif case=='A4':
            Session.objects.create(**saved[0]) # resurrect one revoked backend
        elif case=='A5':
            keys=SessionBinding.objects.filter(group__sid=kw['sid'],group__client_id=kw['client_id']).exclude(group__issuer=kw['issuer']).values_list('session_key',flat=True)
            Session.objects.filter(session_key__in=keys).delete()
        elif case=='A7' and revoke_calls==2:
            SIDRevocationMarker.objects.filter(issuer=kw['issuer'],client_id=kw['client_id'],sid=kw['sid']).update(revoked_at=tz.now())
        return result
    unguarded=mutated_create()
    def bad_create(*args,**kw):
        nonlocal calls
        calls+=1
        if case=='A14': raise PermissionDenied('Injected reject-all')
        if case=='A15' and calls>5:
            if kind=='reject-all': raise PermissionDenied('Injected reject-all')
            return unguarded(*args,**kw)
        binding=create(*args,**kw)
        if case=='A11' and calls==6:
            keys=SessionBinding.objects.filter(group=binding.group).exclude(pk=binding.pk).values_list('session_key',flat=True)
            Session.objects.filter(session_key__in=keys).delete()
        return binding
    stream=StringIO(); error=None; line=None
    with redirect_stdout(stream):
        try:
            with patch.object(s,'revoke_verified_sid',revoke if kind=='baseline' else bad_revoke), patch.object(s,'create_verified_session',create if kind=='baseline' else bad_create), patch.object(v,'create_verified_session',create if kind=='baseline' else bad_create):
                exec(compile(source,str(path),'exec'),{'__name__':'__main__'})
        except Exception as exc:
            error=type(exc).__name__; line=traceback.extract_tb(exc.__traceback__)[-1].line
    cleaned=f'{case}: probe data cleaned' in stream.getvalue()
    # Validate a specific behavioral assertion, never count setup/cleanup errors.
    allowed={'A3':['assert control_snapshot() == before_controls'],
             'A4':['assert not Session.objects.filter('],
             'A5':['assert control_snapshot() == before_controls'],
             'A7':['assert revocation_snapshot() == after_first'],
             'A11':['assert original_snapshot() == before'],
             'A14':['assert response.status_code == 302'],
             'A15':['assert response.status_code == 403']}
    expected_pass=kind=='baseline' or (case=='A15' and kind=='reject-all')
    ok=cleaned and ((expected_pass and error is None) or (not expected_pass and error=='AssertionError' and line in allowed[case]))
    row=dict(case=case,variant=kind,observed='PASS' if error is None else 'FAIL',exception=error,failure_line=line,cleanup_assertions_completed=cleaned,experiment_expected=ok)
    results.append(row)
    (out/f'{case}-{kind}.txt').write_text(stream.getvalue()+'\n'+json.dumps(row,indent=2),encoding='utf-8')
    print(json.dumps(row),flush=True)
    if not ok: raise RuntimeError('Unexpected experiment result; inspect '+case+' '+kind)
try:
    for case in ('A3','A4','A5','A7','A11','A14','A15'):
        run(case,'baseline'); run(case,'mutant')
    run('A15','reject-all')
finally:
    meta=dict(started_at=started,finished_at=datetime.now(timezone.utc).isoformat(),source_hashes=before,source_unchanged=before==hashes(),functions_restored=s.revoke_verified_sid is revoke and s.create_verified_session is create,results=results)
    (out/'results.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')

