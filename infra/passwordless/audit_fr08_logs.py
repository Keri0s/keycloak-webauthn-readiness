"""Read selected local container logs into memory; persist counts only."""
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

from audit_fr08 import ROOT, signals


def summarize(content):
    totals = {"private_named_fields": 0, "private_jwk_objects": 0, "text_markers": 0}
    lines = content.splitlines()
    for line in lines:
        # --timestamps prefixes Docker log entries with a timestamp.
        payload = line.partition(" ")[2]
        try:
            value = json.loads(payload)
        except ValueError:
            value = line
        for name, count in signals(value).items():
            totals[name] += count
    return {"lines": len(lines), "tail_limit_may_apply": len(lines) >= 10000, **totals}


def main():
    until = datetime.now(timezone.utc).isoformat()
    since = "2026-11-22T00:00:00+07:00"
    report = {"since": since, "until": until, "tail_per_container": 10000,
              "scope": "Available logs for current lab Keycloak/Caddy containers only",
              "limitations": ["Rotated/deleted container logs are not recovered",
                              "Marker detection does not cover every private key encoding",
                              "A marker needs classification: TLS/JWT keys are not passkey keys"],
              "services": []}
    for service in ("keycloak", "caddy"):
        row = {"service": service}
        command = ["docker", "compose", "-f", str(ROOT / "infra/compose.yaml"),
                   "logs", "--no-color", "--no-log-prefix", "--timestamps",
                   "--since", since, "--until", until, "--tail", "10000", service]
        try:
            result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                    timeout=30, check=False)
            row["returncode"] = result.returncode
            if result.returncode:
                row["status"] = "READ_FAILED"
            else:
                row.update(summarize(result.stdout.decode("utf-8", errors="replace")))
                row["status"] = "SCANNED_HEURISTIC" if row["lines"] else "NO_LOG_EVIDENCE"
            # stderr may contain configuration details; never echo its contents.
            row["stderr_present"] = bool(result.stderr)
        except (OSError, subprocess.TimeoutExpired) as exc:
            row.update(status="READ_FAILED", error_type=type(exc).__name__)
        report["services"].append(row)
    folder = ROOT / "docs/validation/fr08-2026-11-23"
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = folder / ("container-log-audit-" + stamp + ".json")
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
