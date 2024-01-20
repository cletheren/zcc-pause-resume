import os

from dotenv import load_dotenv
# from engagements import Engagement
from interface import Window
from zoom import Client

load_dotenv()


ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID")
CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET")


def main() -> None:
    """Main application loop."""
    client = Client(CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID)
    # call = Engagement("abcd", client)
    main_ui = Window()
    main_ui.window.mainloop()


if __name__ == "__main__":
    main()
