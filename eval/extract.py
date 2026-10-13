"""Answer extraction for free-text model responses.

Models answer in natural language, so we pull the numeric answer out of the response
before comparing it to the gold label.
"""
import re

_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def extract_answer(response: str):
    """Return the numeric answer stated in `response`, or None if there isn't one.

    Responses usually lead with the answer ("The answer is 42. ..."), so we take the
    number that appears in the response.
    """
    if not response:
        return None
    match = _NUMBER.search(response)
    if match is None:
        return None
    return float(match.group(0))
