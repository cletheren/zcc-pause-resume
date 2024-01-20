import requests

from zoom import Client


class Agent:
    def __init__(self, email: str, user_id: str, client: Client) -> None:
        self.client = client
        self.email = email
        self.user_id = user_id

    @staticmethod
    def get_by_email(email: str, client: Client):
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
