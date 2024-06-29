from tkinter import *
import sqlite3

window = Tk()

home_frame = Frame(window)
home_frame.grid()

expense_list_frame = Frame(home_frame)
expense_list_frame.grid(row = 0,column=0)

add_expense_frame = Frame()

#database setup
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                name TEXT,
                amount REAL,
                date TEXT,
                mode_of_payment_id,
                FOREIGN KEY(mode_of_payment_id) REFERENCES mode_of_payment(id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS mode_of_payments(
                id INTEGER PRIMARY KEY,
                name TEXT,
                balance REAL,
                total spent REAL DEFAULT 0
               )'''
)

conn.commit()



def back_button_function(current_frame, destination_frame):
    current_frame.grid_forget()
    destination_frame.grid()

def add_expense_command():
    back_button = Button(add_expense_frame, text="Back", command=lambda:back_button_function(add_expense_frame, home_frame))
    back_button.grid(row=0, column = 0)
    home_frame.grid_forget()
    add_expense_frame.grid()

    name_label = Label(add_expense_frame, text = "Name: ")
    name_label.grid(row = 1, column = 0)

    global expense_entry
    expense_entry = Entry(add_expense_frame)
    expense_entry.grid(row=1, column=1)

    amount_label = Label(add_expense_frame, text = "Amount")
    amount_label.grid(row = 2, column=0)

    global amount_entry
    amount_entry = Entry(add_expense_frame)
    amount_entry.grid(row = 2, column = 1)

    mode_of_payment_label = Label(add_expense_frame, text = "Mode of Payment")
    mode_of_payment_label.grid(row = 3, column = 0)

    global mode_of_payment_variable
    mode_of_payment_variable = StringVar(add_expense_frame)
    mode_of_payment_variable.set(list(money.keys())[0])

    mode_of_payment_dropdown = OptionMenu(add_expense_frame, mode_of_payment_variable, *money.keys())
    mode_of_payment_dropdown.grid(row = 3, column = 1)

    save_expense_button = Button(add_expense_frame, text = "Add Expense", command = save_expense)
    save_expense_button.grid(row = 4, column = 0)

def save_expense():
    name = expense_entry.get()
    try:
        amount = float(amount_entry.get())
    except ValueError:
        print("Please enter a valid amount.")
        return

    mode_of_payment = mode_of_payment_variable.get()

    cursor.execute("INSERT INTO expenses(name, amount, mode_of_payment) VALUES (?, ?, ?)", (name, amount, mode_of_payment))
    conn.commit()

    money[mode_of_payment] -= amount
    print(f"{mode_of_payment} balance: {money[mode_of_payment]}")

    add_expense_frame.grid_forget()
    home_frame.grid()

add_expense_button = Button(home_frame, text = "Add", command= add_expense_command)
add_expense_button.grid()

window.mainloop()