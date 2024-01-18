"""Classes and methods relating to Contact Centre engagements"""

from abc import ABC, abstractmethod
import requests
from zoom import Client


class Engagement:
    """Class to represent a Contact Centre engagement object"""
    _state = None

    def __init__(self, engagement_id: str, client: Client) -> None:
        self.client = client
        self.engagement_id = engagement_id
        self.set_state(Recording())

    @property
    def state(self) -> str:
        return self._state.__class__.__name__

    def set_state(self, state):
        print(f"Engagement {self.engagement_id!r}: Transitioning to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def change(self):
        self._state.toggle()


class State(ABC):
    """State design pattern, ABC to define how a state class should be defined."""
    @classmethod
    def call_api(cls, engagement_id: str, client: Client) -> None:
        """Method to call the pause/resume/status API endpoint."""
        endpoint = f"{client.base_url}/contact_center/engagements/{engagement_id}/{cls.endpoint}"  # pylint: disable="no-member"
        print(f"Calling: {endpoint}")
        if client.token_has_expired:
            client.get_token()
        headers = {
            "Authorization": f"Bearer {client.token}",
            "Content-Type": "application/json"
        }
        try:
            r = requests.get(endpoint, headers=headers, timeout=3000)
            r.raise_for_status()
        except requests.HTTPError:
            pass

    @property
    def context(self) -> Engagement:
        return self._context

    @context.setter
    def context(self, context: Engagement) -> None:
        self._context = context

    @abstractmethod
    def toggle(self) -> None:
        pass


class Stopped(State):
    """State pattern, represents an engagement where recording is stopped."""

    def toggle(self) -> None:
        print(f"Engagement {self.context.engagement_id!r} is in the state of stopped.")
        self.call_api(self.context.engagement_id, self.context.client)
        self.context.set_state(Recording())


class Paused(State):
    """State pattern, represents an engagement where recording is paused."""
    endpoint = "pause"

    def toggle(self) -> None:
        print(f"Engagement {self.context.engagement_id!r} is in the state of paused.")
        self.call_api(self.context.engagement_id, self.context.client)
        self.context.set_state(Recording())


class Recording(State):
    """State pattern, represents an engagement where recording is active/resumed."""
    endpoint = "resume"

    def toggle(self) -> None:
        print(f"Engagement {self.context.engagement_id} is in the state of recording.")
        self.call_api(self.context.engagement_id, self.context.client)
        self.context.set_state(Paused())
