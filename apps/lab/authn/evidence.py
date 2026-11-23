"""Non-authorizing correlation metadata for the authenticated local lab page."""
import hashlib
from datetime import timezone


def reference(*parts):
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def attach_binding_evidence(response, binding):
    # Called only after require_active_binding. These hashes confer no access.
    group = binding.group
    response["X-Lab-Session-Ref"] = reference(group.issuer, group.client_id, group.sid)
    response["X-Lab-Subject-Ref"] = reference(group.issuer, group.subject)
    response["X-Lab-Binding-Created"] = binding.created_at.astimezone(timezone.utc).isoformat()
    return response
