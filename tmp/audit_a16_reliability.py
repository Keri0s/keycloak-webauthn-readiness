"""Run with manage.py shell. Mutations exist only in this Python process.

Reuses the original A16 unchanged, then adds an independent positive control.
Never treats an unexpected exception or a cleanup failure as a killed mutant.
"""
import ast
import hashlib
import inspect
import json
import sys
import traceback
from contextlib import nullcontext, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import connection
from authn import services
from authn.models import OIDCSessionGroup

if not __debug__:
    raise RuntimeError("Assertions must be enabled")
root = Path(settings.BASE_DIR).parents[1]
output = root / "docs/validation/a16-reliability-2026-11-18"
output.mkdir(parents=True, exist_ok=True)
original_path = root / "tmp/check_a16.py"
original_source = original_path.read_text(encoding="utf-8")
original_revoke = services.revoke_verified_sid
files = sorted((root / "apps/lab/authn").glob("*.py")) + [
    root / "apps/lab/config/oidc.py", original_path,
    root / "tmp/audit_a16_reliability.py",
]
def hashes():
    return {str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

before_hashes = hashes()
started = datetime.now(timezone.utc).isoformat()
results = []

# Compile only this function with its owner guard removed. No file edits.
tree = ast.parse(inspect.getsource(original_revoke))
guards = [n for n in ast.walk(tree) if isinstance(n, ast.If)
          and ast.unparse(n.test) == "groups.exclude(subject=subject).exists()"]
if len(guards) != 1:
    raise RuntimeError("Owner guard shape changed; review mutation")
guards[0].body = [ast.copy_location(ast.Pass(), guards[0].body[0])]
ast.fix_missing_locations(tree)
namespace = dict(vars(services))
exec(compile(tree, "<mutant:remove-owner-guard>", "exec"), namespace)
unguarded = namespace["revoke_verified_sid"]

original_processor = services.process_verified_sid_logout
def reject_every_logout(**kwargs):
    raise PermissionDenied("Injected unconditional rejection")

# A valid token from the actual owner must revoke the target's two sessions,
# retain three control sessions, and persist a processed receipt.
positive_source = '''
claims["sub"] = subject_1
claims["jti"] = jti + "-positive"
valid_token = jwt.encode({"alg": "RS256", "kid": "a16-probe"}, claims, key, algorithms=["RS256"])
with patch.object(oauth.keycloak, "fetch_jwk_set", return_value={"keys": [key.as_dict(private=False)]}):
    positive_response = sender.post("/auth/backchannel-logout/", data=urlencode({"logout_token": valid_token}), content_type="application/x-www-form-urlencoded", secure=True)
assert positive_response.status_code == 200, "positive_owner_http"
for ref in ("D01", "D02"):
    binding = bindings[ref]
    assert not Session.objects.filter(session_key=binding.session_key).exists(), "positive_target_backend"
    browser = Client(HTTP_HOST="app.readiness.test")
    browser.cookies[settings.SESSION_COOKIE_NAME] = binding.session_key
    assert browser.get("/private/", secure=True).status_code == 403, "positive_target_access"
for ref in ("D03", "D04", "D05"):
    check_access(ref, bindings[ref])
assert probe_receipts.filter(jti=claims["jti"], processed_at__isnull=False).exists(), "positive_receipt"
assert not connection.in_atomic_block
print("Positive owner control: target sessions denied, other sessions allowed, receipt processed")
'''
positive_ast = ast.parse(positive_source, filename="<positive-control>")
# Embed exec so traceback identifies the positive control, not the original file.
extended_tree = ast.parse(original_source, filename=str(original_path))
outer_try = [n for n in extended_tree.body if isinstance(n, ast.Try)]
if len(outer_try) != 1:
    raise RuntimeError("A16 cleanup structure changed")
outer_try[0].body.append(ast.Expr(value=ast.Call(
    func=ast.Name(id="exec", ctx=ast.Load()),
    args=[ast.Name(id="positive_code", ctx=ast.Load())], keywords=[])))
ast.fix_missing_locations(extended_tree)
extended_code = compile(extended_tree, str(original_path), "exec")
base_code = compile(original_source, str(original_path), "exec")

def run(label, mutation=None, extended=False, expected_assert=None, expected_pass=False):
    scope = {"__name__": "__main__", "positive_code": compile(positive_ast, "<positive-control>", "exec")}
    stream = StringIO()
    caught = None
    frames = []
    # A16 imports the service on execution and spies on the view using that import.
    with redirect_stdout(stream):
        try:
            with mutation if mutation is not None else nullcontext():
                exec(extended_code if extended else base_code, scope)
        except Exception as exc:
            caught = type(exc).__name__
            frames = traceback.extract_tb(exc.__traceback__)
    cleanup = "A16: probe data cleaned" in stream.getvalue()
    # Independent, scoped readback after finally; never print keys/token/user rows.
    if cleanup:
        cleanup = all(not scope[name].exists() for name in ("probe_groups", "probe_markers", "probe_receipts"))
        cleanup = cleanup and not scope["Session"].objects.filter(session_key__in=scope["session_keys"]).exists()
    failure_line = frames[-1].line if frames else None
    if frames and frames[-1].filename == "<positive-control>":
        failure_line = positive_source.splitlines()[frames[-1].lineno - 1].strip()
    correct_failure = caught == "AssertionError" and expected_assert is not None and failure_line == expected_assert
    accepted = cleanup and ((expected_pass and caught is None) or correct_failure)
    result = {"label": label, "test_variant": "with_positive_control" if extended else "original",
              "observed": "PASS" if caught is None else "FAIL", "exception": caught,
              "failure_line": failure_line, "cleanup_verified": cleanup,
              "matches_experiment_expectation": accepted}
    results.append(result)
    (output / (label + ".txt")).write_text(stream.getvalue() + "\n" + json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result), flush=True)
    if not accepted:
        raise RuntimeError("Experiment failed unexpectedly: " + label)

try:
    # These are deliberately sequential, with fresh UUID fixtures each time.
    run("01-original-baseline", expected_pass=True)
    run("02-remove-owner-guard", patch.object(services, "revoke_verified_sid", unguarded),
        expected_assert="assert response.status_code == 400")
    # Preserve the expected HTTP 400 while corrupting state: snapshot must catch it.
    def corrupt_and_reject(**kwargs):
        OIDCSessionGroup.objects.filter(issuer=kwargs["issuer"], client_id=kwargs["client_id"], sid=kwargs["sid"]).update(subject=kwargs["subject"])
        raise PermissionDenied("Injected persisted corruption")
    run("03-corrupt-state-return-400", patch.object(services, "process_verified_sid_logout", corrupt_and_reject),
        expected_assert="assert snapshot() == before")
    run("04-reject-all-original-survivor", patch.object(services, "revoke_verified_sid", reject_every_logout), expected_pass=True)
    run("05-positive-control-baseline", extended=True, expected_pass=True)
    run("06-reject-all-positive-control", patch.object(services, "revoke_verified_sid", reject_every_logout), extended=True,
        expected_assert='assert positive_response.status_code == 200, "positive_owner_http"')
finally:
    unchanged = hashes() == before_hashes
    restored = services.revoke_verified_sid is original_revoke and services.process_verified_sid_logout is original_processor
    metadata = {"started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
                "python": sys.version.split()[0], "database_vendor": connection.vendor,
                "assertions_enabled": __debug__, "source_hashes": before_hashes,
                "source_files_unchanged": unchanged, "functions_restored": restored,
                "results": results, "scope": "A16 only; local PostgreSQL; Django test client; JWKS mocked; mutations in memory"}
    (output / "results.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Source files unchanged:", unchanged, "Functions restored:", restored)
    if not unchanged or not restored:
        raise RuntimeError("Source/function restoration check failed")
