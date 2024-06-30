from tkinter import *
from tkinter import messagebox
import sqlite3

window = Tk()

home_frame = Frame(window)
home_frame.grid()

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

def get_total_balance():
    cursor.execute("SELECT SUM(balance) FROM mode_of_payments")
    result = cursor.fetchone()
    if result and result[0] is not None:
        return result[0]
    else:
        return 0

# displays total balance 
total_balance = get_total_balance()

total_balance_label = Label(home_frame, text= f"Total Balance = {get_total_balance()}")
total_balance_label.grid()

#add bucket mechanism

def add_bucket_button_command():
    #setting up the frames
    home_frame.grid_forget()
    add_bucket_button_frame.grid()

    #adding back buttons to back to the homepage
    back_button = Button(add_bucket_button_frame, text="Back", command=lambda:back_button_function(add_bucket_button_frame, home_frame))
    back_button.grid(row=0, column = 0)

    #Label that asks for the name of the new bucket the user is going to add
    bucket_name_label =  Label(add_bucket_button_frame, text = "Bucket Name")
    bucket_name_label.grid(row = 1, column=0)

    #the input field where the user will enter the name of the new bucket 
    global bucket_name_entry
    bucket_name_entry = Entry(add_bucket_button_frame)
    bucket_name_entry.grid(row = 1, column=1)

    #set initial amount
    initial_amount_label = Label(add_bucket_button_frame, text = "Set Initial Amount(Optional):")
    initial_amount_label.grid(row = 2, column=0)

    #entry for initial amount
    global initial_amount_entry
    initial_amount_entry = Entry(add_bucket_button_frame)
    initial_amount_entry.grid(row=2, column=1)

    save_button = Button(add_bucket_button_frame, text = "Save", command=save_new_bucket)
    save_button.grid(row = 3, column = 0)


#save new bucket added by the user
def save_new_bucket():
    bucket_name =  bucket_name_entry.get()
    initial_amount = initial_amount_entry.get()

    if not bucket_name:
        messagebox.showerror("Error", "Bucket name cannot be empty")
        return
    
    try:
        initial_amount = float(initial_amount) if initial_amount else 0.0
    except ValueError:
        messagebox.showerror("Error", "Invalid Initial amount. Please enter a valid amount ")
        return

    cursor.execute("INSERT INTO mode_of_payments (name, balance) VALUES (?, ?)", (bucket_name, initial_amount))
    conn.commit()
    
    messagebox.showinfo("Success", f"Added new bucket: {bucket_name} with initial with initial balance {initial_amount}")

    bucket_name_entry.delete(0, END)
    initial_amount_entry.delete(0, END)

    # Navigate back to home_frame
    add_bucket_button_frame.grid_forget()
    home_frame.grid()  

#display buckets
def display_buckets(frame):
    cursor.execute("SELECT name, balance FROM mode_of_payments")
    buckets = cursor.fetchall()

    for index, (name, balance) in enumerate(buckets):
        bucket_label = Label(frame, text = f"{name}: {balance}")
        bucket_label.grid(row = index + 2, column = 0)

display_buckets(home_frame)

def edit_bucket_command():
    home_frame.grid_forget()
    edit_buckets_frame.grid()

    cursor.execute("SELECT name, balance FROM mode_of_payments")
    buckets = cursor.fetchall()

    bucket_list_frame = Frame(edit_buckets_frame)
    bucket_list_frame.grid(row = 0, column = 0)

    for index, (name, balance) in enumerate(buckets):
        bucket_label_entry = Entry(edit_buckets_frame)
        bucket_label_entry.grid(row = index, column = 0)
        bucket_label_entry.insert(0, name)

        balance_label_entry = Entry(edit_buckets_frame)
        balance_label_entry.grid(row = index, column = 1)
        balance_label_entry.insert(0, balance)
    
    save_edit_bucket_button = Button(edit_buckets_frame, text = "save")
    save_edit_bucket_button.grid(row = 5)


def back_button_function(current_frame, destination_frame):
    current_frame.grid_forget()
    destination_frame.grid()

def get_buckets():
    cursor.execute("SELECT name FROM mode_of_payments")
    buckets = cursor.fetchall()
    return [bucket[0] for bucket in buckets]

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
    buckets = get_buckets()
    if buckets:
        mode_of_payment_variable.set(buckets[0])

    mode_of_payment_dropdown = OptionMenu(add_expense_frame, mode_of_payment_variable, *buckets)
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

    cursor.execute("SELECT id, balance FROM mode_of_payments WHERE name = ?", (mode_of_payment,))
    result = cursor.fetchone()
    if result:
        mode_of_payment_id, current_balance = result
    else:
        messagebox.showerror("Error", "Select mode of payment not found.")
        return
    
    if current_balance < amount:
        messagebox.showerror("Error", "Insufficient balance in the selected mode of payment")
        return
    
    #update database
    new_balance = current_balance - amount
    cursor.execute("UPDATE mode_of_payments SET balance = ? WHERE id = ?", (new_balance, mode_of_payment_id))
    conn.commit()

    #update transaction table
    cursor.execute("INSERT INTO transactions (name, amount, date, mode_of_payment_id) VALUES (?, ?, DATE('now'), ?)",
                   (name, amount, mode_of_payment_id))
    conn.commit()

    messagebox.showinfo("Success", f"Expenses added: {name}, Amount: {amount}, mode_of_payment: {mode_of_payment}")

    total_balance_label.config(text = f"Total Balance = {get_total_balance()}")

    add_expense_frame.grid_forget()
    home_frame.grid() 

#transactions
transactions_frame = Frame(home_frame)  # Houses all the transactions 
transactions_frame.grid(columnspan=5)
transaction_number_label = Label(transactions_frame, text="Transaction Number")
transaction_number_label.grid(row=0, column=0)
transaction_name_label = Label(transactions_frame, text="Transaction Name")
transaction_name_label.grid(row=0, column=1)
amount_label = Label(transactions_frame, text="Amount")
amount_label.grid(row=0, column=2)
transaction_date_label = Label(transactions_frame, text="Date")
transaction_date_label.grid(row=0, column=3)

def display_transactions():
    cursor.execute("SELECT id, name, amount, date FROM transactions")
    transactions = cursor.fetchall()

    for index, (transaction_id, name, amount, date) in enumerate(transactions, start=1):
        transaction_number = Label(transactions_frame, text=transaction_id)
        transaction_number.grid(row=index, column=0)

        transaction_name = Label(transactions_frame, text=name)
        transaction_name.grid(row=index, column=1)

        transaction_amount = Label(transactions_frame, text=amount)
        transaction_amount.grid(row=index, column=2)

        transaction_date = Label(transactions_frame, text=date)
        transaction_date.grid(row=index, column=3)

display_transactions()

buttons_frame = Frame(home_frame)
buttons_frame.grid(row = 0, column = 2, rowspan=5)

add_expense_button = Button(buttons_frame, text = "Add", command= add_expense_command)
add_expense_button.grid(row = 2, column = 0)

add_bucket_button = Button(buttons_frame, text = "Add New Bucket", command = add_bucket_button_command)
add_bucket_button.grid(row = 0, column = 0)

edit_bucket_button = Button(buttons_frame, text = "Edit buckets", command=edit_bucket_command)
edit_bucket_button.grid(row = 1, column=0)

add_bucket_button_frame =  Frame(window)

add_expense_frame = Frame()
edit_buckets_frame = Frame()

window.mainloop()