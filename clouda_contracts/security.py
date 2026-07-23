from __future__ import annotations

import re
from typing import Any

_SENSITIVE_KEY = re.compile(
    r"(?:api[_-]?key|token|secret|password|cookie|authorization)",
    re.IGNORECASE,
)


def redact_mapping(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: (
            "[REDACTED]"
            if _SENSITIVE_KEY.search(key)
            else redact_mapping(item) if isinstance(item, dict) else item
        )
        for key, item in value.items()
    }


def may_use_user_document_for_training(
    *,
    explicit_document_consent: bool,
    approved_consent_policy: bool,
) -> bool:
    """Require two independent approvals; both default false at all call sites."""
    return explicit_document_consent and approved_consent_policy
