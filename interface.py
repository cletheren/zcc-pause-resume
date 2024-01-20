"""Define the user interface using tkinter"""


# TODO There is a potential memory leak, consider deleting class instances when states change

from abc import ABC, abstractmethod
import os
import sys
import tkinter as tk
from dotenv import load_dotenv

from agent import Agent
from engagements import Engagement
from zoom import Client

load_dotenv()

TITLE = "Card Payment App"
ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID")
CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET")
USER_ID = os.environ.get("ZOOM_USER_ID")


class Window:
    _state = None

    def __init__(self, client: Client) -> None:
        self.window = tk.Tk()
        self.window.title(TITLE)
        self.client = client
        self.agent = None
        self.engagement = None
        self.set_state(AgentEntry())

    def set_state(self, state):
        self._state = state
        self._state.context = self
        self._state.draw_window()

    def clear_ui(self) -> None:
        for widget in self.window.winfo_children():
            widget.destroy()


class State(ABC):

    @abstractmethod
    def draw_window(self) -> None:  # pylint: disable="missing-function-docstring"
        pass

    @property
    def context(self) -> Window:  # pylint: disable="missing-function-docstring"
        return self._context

    @context.setter
    def context(self, context: Window) -> None:
        self._context = context


class AgentEntry(State):

    def __init__(self) -> None:
        # self.window = None
        self.ui_frame = None
        self.input_frame = None
        self.lbl_agent_email = None
        self.ent_agent_email = None
        self.lbl_error_message = None

    def process_input(self, email: str) -> None:
        if not email:
            self.lbl_error_message.config(text="Please specify an email address.")
            return
        self.context.agent = Agent.get_by_email(email, self.context.client)
        if not self.context.agent:
            self.lbl_error_message.config(text="No agent found!")
            return
        self.lbl_error_message.config(text="")
        self.context.engagement = Engagement.get_by_user_id(self.context.agent.user_id, self.context.client)
        if not self.context.engagement:
            self.lbl_error_message.config(text="No active voice engagement!")
            return
        self.context.set_state(TakePayment())

    def draw_window(self):
        """In this state, the get agent details window is drawn."""

        self.context.clear_ui()
        # self.window = self.context.window

        # Define the main UI Frame
        self.ui_frame = tk.Frame(master=self.context.window, width=400, height=350)
        self.ui_frame.pack()

        # Create a Frame to accommodate the input field(s)
        self.input_frame = tk.Frame(master=self.ui_frame, width=400, height=120)
        self.input_frame.grid(row=0, column=0)

        # Create the input fields and associated labels
        self.lbl_agent_email = tk.Label(master=self.input_frame, text="Agent Email")
        self.ent_agent_email = tk.Entry(master=self.input_frame, width=30, exportselection=False)

        # If we have a global USER_ID then we should auto-populate
        if USER_ID:
            self.ent_agent_email.insert(-1, USER_ID)
        # But we prefer the user id that has already been verified
        try:
            self.ent_agent_email.insert(-1, self.context.agent.email)
        except AttributeError:
            pass

        self.lbl_agent_email.place(x=40, y=30)
        self.ent_agent_email.place(x=40, y=50)

        # Create the error labels, only show them if an error occurs
        self.lbl_error_message = tk.Label(master=self.input_frame, fg="red", text="")
        self.lbl_error_message.place(x=40, y=80)

        # Create a Frame to accommodate the Confirm and Cancel buttons
        button_frame = tk.Frame(master=self.ui_frame, width=400, height=100)
        button_frame.grid(row=1, column=0)

        # Create the buttons to Continue or Cancel
        btn_confirm = tk.Button(master=button_frame, text="Confirm", width=11, command=lambda: self.process_input(self.ent_agent_email.get()))
        btn_cancel = tk.Button(master=button_frame, text="Exit", width=11, command=sys.exit)
        btn_confirm.place(x=40, y=0)
        btn_cancel.place(x=190, y=0)


class TakePayment(State):

    def __init__(self) -> None:
        self.ui_frame = None
        self.input_frame = None
        self.button_frame = None
        self.lbl_engagement_id = None
        self.lbl_card_number = None
        self.ent_card_number = None
        self.lbl_expiry_date = None
        self.ent_expiry_date = None
        self.lbl_cvc_number = None
        self.ent_cvc_number = None
        self.lbl_amount = None
        self.ent_amount = None
        self.btn_confirm = None
        self.btn_cancel = None

    def draw_window(self) -> None:
        self.context.clear_ui()
        # window = self.context.window

        # Define the main UI Frame
        self.ui_frame = tk.Frame(master=self.context.window, width=400, height=350)
        self.ui_frame.pack()

        # Create a Frame to accommodate the input field(s)
        self.input_frame = tk.Frame(master=self.ui_frame, width=400, height=220)
        self.input_frame.grid(row=0, column=0)

        # Create the input fields and associated labels
        self.lbl_engagement_id = tk.Label(master=self.input_frame, text=f"Engagement ID: {self.context.engagement.engagement_id}")
        self.lbl_card_number = tk.Label(master=self.input_frame, text="Card Number")
        self.ent_card_number = tk.Entry(master=self.input_frame, width=30)
        self.lbl_expiry_date = tk.Label(master=self.input_frame, text="Expiry Date")
        self.ent_expiry_date = tk.Entry(master=self.input_frame, width=13, exportselection=False)
        self.lbl_cvc_number = tk.Label(master=self.input_frame, text="Security Number")
        self.ent_cvc_number = tk.Entry(master=self.input_frame, width=13, exportselection=False)
        self.lbl_amount = tk.Label(master=self.input_frame, text="Payment Amount")
        self.ent_amount = tk.Entry(master=self.input_frame, width=20, exportselection=False)
        self.lbl_engagement_id.place(x=40, y=0)
        self.lbl_card_number.place(x=40, y=30)
        self.ent_card_number.place(x=40, y=50)
        self.lbl_expiry_date.place(x=40, y=90)
        self.ent_expiry_date.place(x=40, y=110)
        self.lbl_cvc_number.place(x=192, y=90)
        self.ent_cvc_number.place(x=192, y=110)
        self.lbl_amount.place(x=40, y=150)
        self.ent_amount.place(x=40, y=170)

        # Create a Frame to accommodate the Confirm and Cancel buttons
        self.button_frame = tk.Frame(master=self.ui_frame, width=400, height=100)
        self.button_frame.grid(row=1, column=0)

        # Create the buttons to Confirm or Cancel
        self.btn_confirm = tk.Button(master=self.button_frame, text="Confirm", width=11, command=lambda: self.context.set_state(AgentEntry()))
        self.btn_cancel = tk.Button(master=self.button_frame, text="Cancel", width=11, command=lambda: self.context.set_state(AgentEntry()))
        self.btn_confirm.place(x=40, y=0)
        self.btn_cancel.place(x=190, y=0)


def main() -> None:
    """Main application loop."""
    client = Client(CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID)
    client.get_token()
    main_ui = Window(client)
    main_ui.window.mainloop()


if __name__ == "__main__":
    main()
