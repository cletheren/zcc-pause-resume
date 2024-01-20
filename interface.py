"""Define the user interface using tkinter"""

import tkinter as tk


def get_payment_details(window: tk.Tk) -> None:
    """In this state, the get get payment details window is drawn."""
    take_payment_frame = tk.Frame(master=window, width=400, height=350)
    take_payment_frame.pack()

    # Payment details input fields and labels
    input_frame = tk.Frame(master=take_payment_frame, width=400, height=220)
    input_frame.grid(row=0, column=0)
    lbl_card_number = tk.Label(master=input_frame, text="Card Number")
    ent_card_number = tk.Entry(master=input_frame, width=30)
    lbl_expiry_date = tk.Label(master=input_frame, text="Expiry Date")
    ent_expiry_date = tk.Entry(master=input_frame, width=13)
    lbl_cvc_number = tk.Label(master=input_frame, text="Security Number")
    ent_cvc_number = tk.Entry(master=input_frame, width=13)
    lbl_amount = tk.Label(master=input_frame, text="Payment Amount")
    ent_amount = tk.Entry(master=input_frame, width=20)
    lbl_card_number.place(x=40, y=30)
    ent_card_number.place(x=40, y=50)
    lbl_expiry_date.place(x=40, y=90)
    ent_expiry_date.place(x=40, y=110)
    lbl_cvc_number.place(x=192, y=90)
    ent_cvc_number.place(x=192, y=110)
    lbl_amount.place(x=40, y=150)
    ent_amount.place(x=40, y=170)

    # Confirm and Cancel buttons
    button_frame = tk.Frame(master=take_payment_frame, width=400, height=100)
    button_frame.grid(row=1, column=0)
    btn_confirm = tk.Button(master=button_frame, text="Confirm", width=11)
    btn_cancel = tk.Button(master=button_frame, text="Cancel", width=11)
    btn_confirm.place(x=40, y=0)
    btn_cancel.place(x=190, y=0)


def get_agent_details(window: tk.Tk):
    """In this state, the get agent details window is drawn."""
    input_frame = tk.Frame(master=window, width=400, height=350)
    input_frame.pack()
    lbl_agent_name = tk.Label(master=input_frame, text="Agent Name")
    ent_agent_name = tk.Entry(master=input_frame, width=30)
    lbl_agent_name.place(x=40, y=30)
    ent_agent_name.place(x=40, y=50)


def main():
    """Main application loop."""
    window = tk.Tk()
    window.title("Card Payment App")
    # get_payment_details(window)
    get_agent_details(window)
    window.mainloop()


if __name__ == "__main__":
    main()
