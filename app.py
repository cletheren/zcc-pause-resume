import os

from dotenv import load_dotenv
from engagements import Engagement
from zoom import Client

load_dotenv()

ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID")
CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET")

# sample application


def main() -> None:
    """Main application loop."""
    client = Client(CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID)
    call = Engagement("abcd", client)
    call.change()
    call.change()
    call.change()
    print(call.state)


if __name__ == "__main__":
    main()
