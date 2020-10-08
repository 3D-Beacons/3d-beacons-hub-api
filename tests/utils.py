import json


async def request_get_stub(url: str, stub_for: str, status_code: int = 200):
    """Returns an object with stub response.

    Args:
        url (str): A request URL.
        stub_for (str): Type of stub required.

    Returns:
        StubResponse: A StubResponse object.
    """
    return StubResponse(stub_for=stub_for, status_code=status_code)


class StubResponse:
    """A Stub response class to return a response from JSON."""

    def __init__(self, status_code: int, stub_for: str) -> None:
        self.status_code = status_code
        self.prefix = "tests/stubs/"
        self.data = {}

        with open(f"{self.prefix}/{stub_for}.json") as f:
            self.data = json.load(f)

    def json(self):
        return self.data
