import hashlib
import json
from contextlib import contextmanager

from django.db import connection, transaction


@contextmanager
def oidc_session_transaction(issuer, client_id):
    lock_data = json.dumps(
        ["oidc_session", issuer, client_id],
        separators=(",", ":"),
    ).encode("utf-8")

    lock_key = int.from_bytes(
        hashlib.sha256(lock_data).digest()[:8],
        byteorder="big",
        signed=True,
    )

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_advisory_xact_lock(%s)",
                [lock_key],
            )

        yield