import requests
from dotenv import load_dotenv
import os
from zoom import Client

load_dotenv()

TITLE = "Card Payment App"
ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID")
CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET")


class Agent:
    def __init__(self, email: str, user_id: str, client: Client) -> None:
        self.client = client
        self.email = email
        self.user_id = user_id

    @staticmethod
    def get_by_email(email: str, client: Client) -> str:
        """Alternative constructor."""
        if not email:
            # This needs to be better, consider raising an exception
            return None
        endpoint = f"{client.base_url}/contact_center/users"
        headers = {
            "Authorization": f"Bearer {client.token}"
        }
        params = {
            "search_key": email,
            "user_access": "active"
        }
        try:
            if client.token_has_expired:
                client.get_token()
            r = requests.get(endpoint, headers=headers, params=params, timeout=3000)
            r.raise_for_status()
            response = r.json()
            if "users" in response and len(response["users"]) == 1:
                return Agent(email, response["users"][0]["user_id"], client)
        except requests.HTTPError:
            return None
        return None

    def __repr__(self) -> str:
        return f"Agent(email={self.email!r}, user_id={self.user_id!r})"


def main():
    client = Client(CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID)
    client.get_token()
    agent = Agent.get_by_email("", client)
    print(agent)


if __name__ == "__main__":
    main()
