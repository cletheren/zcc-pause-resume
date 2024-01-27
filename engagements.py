"""Classes and methods relating to Contact Centre engagements"""

from abc import ABC, abstractmethod
import logging

import requests

from zoom import Client

logger = logging.getLogger(__name__)


class Engagement:
    """Class to represent a Contact Centre engagement object"""
    _state = None

    def __init__(self, engagement_id: str, client: Client) -> None:
        self.client = client
        self.engagement_id = engagement_id
        self.initial_state = self.check_state()
        match self.initial_state:
            case "Recording":
                self.set_state(Recording())
            case "Paused":
                self.set_state(Paused())
            case "Stopped":
                self.set_state(Stopped())

    @property
    def state(self) -> str:
        return self._state.__class__.__name__

    def set_state(self, state):
        self._state = state
        self._state.context = self

    def check_state(self) -> str:
        """
        Use the recording API to check the current engagement's recording status.
        Requires the contact_center_engagement:read:admin scope.
        """

        endpoint = f"{self.client.base_url}/contact_center/engagements/{self.engagement_id}/recordings/status"
        if self.client.token_has_expired:
            self.client.get_token()
        headers = {
            "Authorization": f"Bearer {self.client.token}"
        }
        try:
            logger.debug("Calling: %s", endpoint)
            r = requests.get(endpoint, headers=headers, timeout=3000)
            r.raise_for_status()
            response = r.json()
            if "statuses" in response:
                match response["statuses"][-1]["status"]:
                    case "start" | "resume":
                        return "Recording"
                    case "pause":
                        return "Paused"
                    case "stopped":
                        return "Stopped"
                    case _:
                        return "Stopped"
            else:
                return "Stopped"
        except requests.HTTPError:
            pass
        return "Recording"  # Just in case, we'll assume the call is being recorded

    def toggle(self):
        self._state.toggle()

    @staticmethod
    def get_by_user_id(user_id: str, client: Client):
        """Alternative constructor."""
        # Need a better way of doing this as the endpoint will be deprecated in August 2024
        endpoint = f"{client.base_url}/contact_center/tasks"
        headers = {
            "Authorization": f"Bearer {client.token}"
        }
        params = {
            "task_status": "assigned"
        }
        try:
            if client.token_has_expired:
                logger.debug("Getting new bearer token")
                client.get_token()
            logger.debug("Calling: %s", endpoint)
            r = requests.get(endpoint, headers=headers, params=params, timeout=3000)
            r.raise_for_status()
            response = r.json()
            if "tasks" in response:
                for engagement in response["tasks"]:
                    if (engagement["assigned_user_id"] == user_id and
                        engagement["task_status"] == "assigned" and
                            engagement["channel_name"] == "default"):
                        logger.debug("Found active voice enagement with engagement id %s", engagement["engagement_id"])
                        return Engagement(engagement["engagement_id"], client)
        except requests.HTTPError:
            return None
        return None

    def __repr__(self) -> str:
        return f"Engagement(engagement_id={self.engagement_id!r})"


class State(ABC):
    """State design pattern, ABC to define how a state class should be defined."""
    @classmethod
    def call_api(cls, engagement_id: str, client: Client, command: str) -> None:
        """
        Method to call the pause/resume/status API endpoint.
        Requires the contact_center_engagement:write:admin scope.
        """

        endpoint = f"{client.base_url}/contact_center/engagements/{engagement_id}/recording/{command}"  # pylint: disable="no-member"
        if client.token_has_expired:
            logger.debug("Getting new bearer token")
            client.get_token()
        headers = {
            "Authorization": f"Bearer {client.token}",
            "Content-Type": "application/json"
        }
        try:
            logger.debug("Calling: %s", endpoint)
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
    # endpoint = "pause"

    def toggle(self) -> None:
        logger.info("Engagement %s is STOPPED, transitioning to RECORDING", self.context.engagement_id)
        self.call_api(self.context.engagement_id, self.context.client, "resume")
        self.context.set_state(Recording())


class Paused(State):
    """State pattern, represents an engagement where recording is paused."""
    endpoint = "pause"

    def toggle(self) -> None:
        logger.info("Engagement %s is PAUSED, transitioning to RECORDING", self.context.engagement_id)
        self.call_api(self.context.engagement_id, self.context.client, "resume")
        self.context.set_state(Recording())


class Recording(State):
    """State pattern, represents an engagement where recording is active/resumed."""
    endpoint = "resume"

    def toggle(self) -> None:
        logger.info("Engagement %s is RECORDING, transitioning to PAUSED",  self.context.engagement_id)
        self.call_api(self.context.engagement_id, self.context.client, "pause")
        self.context.set_state(Paused())
