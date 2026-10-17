"""Answer extraction for free-text model responses.

Models answer in natural language, so we pull the numeric answer out of the response
before comparing it to the gold label.
"""
import re

# Original rule kept so the eval team's numbers can be reproduced (method="first_number")
_FIRST_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")

_NUM = r"-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
_NUMBER = re.compile(_NUM)

_ANSWER_PATTERNS = [
    re.compile(r"answer\s*(?:is|:)\s*\$?\s*(" + _NUM + ")", re.IGNORECASE),
    re.compile(r"^\s*\*\*\s*\$?\s*(" + _NUM + r")\s*\*\*"),
]


def _to_float(text):
    return float(text.replace(",", ""))


def extract_answer(response: str, method: str = "final"):
    """Return the numeric answer stated in `response`, or None if there isn't one.

    method="final": the explicitly stated answer ("Answer: 42", "The answer is 42",
                    a leading "**42**"). If there is none, fallback to the last number.
    method="last_number": the last number in the response.
    method="first_number": the first number, ignoring thousands separators (the original rule).
    """
    if not response:
        return None
    if method == "first_number":
        match = _FIRST_NUMBER.search(response)
        return float(match.group(0)) if match else None
    if method == "final":
        for pattern in _ANSWER_PATTERNS:
            match = pattern.search(response)
            if match:
                return _to_float(match.group(1))
    elif method != "last_number":
        raise ValueError(f"unknown extraction method: {method}")
    numbers = _NUMBER.findall(response)
    return _to_float(numbers[-1]) if numbers else None
