import csv
import os
from datetime import datetime
import customtkinter as ctk
from tkinter import ttk

EXPENSE_FILE = ('expenses.csv')
BUDGET_FILE = 'budgets.csv'
CATEGORIES = ["Food", "Transport", "Bills", "Entertainment", "Shopping", "Health", "Other"]


def initialize_csv():
    if not os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Date', 'Amount', 'Category', 'Description'])

    if not os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Month', 'Amount'])


def get_next_id():
    try:
        with open(EXPENSE_FILE, 'r') as f:
            reader = list(csv.reader(f))
            if len(reader) <= 1:
                return 1
            return int(reader[-1][0]) + 1
    except (IOError, IndexError):
        return 1


def add_expense(amount, category, description):
    new_id = get_next_id()
    date = datetime.now().strftime("%Y-%m-%d")
    with open(EXPENSE_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([new_id, date, amount, category, description])


def get_all_expenses():
    try:
        with open(EXPENSE_FILE, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            return [row for row in reader]
    except (IOError, StopIteration):
        return []


def delete_expense(expense_id_to_delete):
    rows = []
    with open(EXPENSE_FILE, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    updated_rows = [row for row in rows if int(row[0]) != int(expense_id_to_delete)]
    with open(EXPENSE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_rows)


def get_category_summary():
    summary = {category: 0 for category in CATEGORIES}
    total_spending = 0
    expenses = get_all_expenses()
    for expense in expenses:
        try:
            amount = float(expense[2])
            category = expense[3]
            if category in summary:
                summary[category] += amount
                total_spending += amount
        except (ValueError, IndexError):
            continue
    return summary, total_spending


def set_budget(month, amount):
    rows = []
    header = ['Month', 'Amount']
    month_exists = False
    try:
        with open(BUDGET_FILE, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
    except (IOError, StopIteration):
        pass

    for row in rows:
        if row[0] == month:
            row[1] = amount
            month_exists = True
            break

    if not month_exists:
        rows.append([month, amount])

    with open(BUDGET_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def get_budget_status(month):
    budget_amount = 0.0
    try:
        with open(BUDGET_FILE, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == month:
                    budget_amount = float(row[1])
                    break
    except (IOError, ValueError):
        pass

    spent_amount = 0.0
    expenses = get_all_expenses()
    for expense in expenses:
        if expense[1].startswith(month):
            spent_amount += float(expense[2])

    remaining = budget_amount - spent_amount
    return budget_amount, spent_amount, remaining

def submit_expense_callback():
    amount = amount_entry.get()
    category = category_combobox.get()
    description = description_entry.get()
    if not amount or not description:
        status_label.configure(text="Amount and Description are required.", text_color="red")
        return
    try:
        float(amount)
    except ValueError:
        status_label.configure(text="Amount must be a number.", text_color="red")
        return
    add_expense(amount, category, description)
    amount_entry.delete(0, 'end')
    description_entry.delete(0, 'end')
    status_label.configure(text="Expense Added Successfully!", text_color="green")


def populate_expense_table():
    for item in expense_table.get_children():
        expense_table.delete(item)
    expenses = get_all_expenses()
    for expense in expenses:
        expense_table.insert("", "end", values=expense)


def delete_selected_expense_callback():
    selected_items = expense_table.selection()
    if not selected_items:
        return
    expense_id = expense_table.item(selected_items[0])['values'][0]
    delete_expense(expense_id)
    populate_expense_table()


def update_analysis_view():
    for widget in analysis_content_frame.winfo_children():
        widget.destroy()
    summary, total_spending = get_category_summary()
    if total_spending == 0:
        ctk.CTkLabel(analysis_content_frame, text="No spending data to analyze.", font=("Calibri", 14)).pack(pady=10)
        return
    row_num = 0
    for category, amount in summary.items():
        percentage = amount / total_spending if total_spending > 0 else 0
        label_text = f"{category}: ₹{amount:.2f}"
        label = ctk.CTkLabel(analysis_content_frame, text=label_text, anchor="w")
        label.grid(row=row_num, column=0, sticky="ew", padx=10, pady=5)
        progress_bar = ctk.CTkProgressBar(analysis_content_frame)
        progress_bar.set(percentage)
        progress_bar.grid(row=row_num, column=1, sticky="ew", padx=10, pady=5)
        row_num += 1
    analysis_content_frame.grid_columnconfigure(1, weight=1)


def set_budget_callback():
    month = budget_month_entry.get()
    amount = budget_amount_entry.get()
    if len(month) != 7 or month[4] != '-':
        budget_status_label.configure(text="Error: Month format must be YYYY-MM.", text_color="red")
        return
    try:
        float(amount)
    except ValueError:
        budget_status_label.configure(text="Error: Amount must be a number.", text_color="red")
        return
    set_budget(month, amount)
    budget_status_label.configure(text=f"Budget for {month} set to ₹{amount}.", text_color="green")
    budget_amount_entry.delete(0, 'end')


def check_budget_status_callback():
    month = check_month_entry.get()
    if len(month) != 7 or month[4] != '-':
        budget_result_label.configure(text="Error: Month format must be YYYY-MM.", text_color="red")
        budget_progress_bar.set(0)
        return

    budget, spent, remaining = get_budget_status(month)

    if budget == 0:
        budget_result_label.configure(text=f"No budget set for {month}.\nSpent: ₹{spent:.2f}", text_color="gray")
        budget_progress_bar.set(0)
    else:
        result_text = f"Budget for {month}: ₹{budget:.2f}\n"
        result_text += f"Spent this month: ₹{spent:.2f}\n"
        result_text += f"Remaining: ₹{remaining:.2f}"

        text_color = "green" if remaining >= 0 else "red"
        budget_result_label.configure(text=result_text, text_color=text_color)

        if budget > 0:
            progress = spent / budget
            budget_progress_bar.set(progress if progress <= 1.0 else 1.0)

            progress_color = "green" if remaining >= 0 else "red"
            budget_progress_bar.configure(progress_color=progress_color)
        else:
            budget_progress_bar.set(0)


def on_tab_change():
    selected_tab = tabview.get()
    if selected_tab == "View Expenses":
        populate_expense_table()
    elif selected_tab == "Analysis":
        update_analysis_view()


initialize_csv()

app = ctk.CTk()
app.title("Simple Expense Tracker")
app.geometry("800x550")
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

tabview = ctk.CTkTabview(app, width=780, height=530, command=on_tab_change)
tabview.pack(padx=10, pady=10)

add_tab = tabview.add("Add Expense")
view_tab = tabview.add("View Expenses")
analysis_tab = tabview.add("Analysis")
budget_tab = tabview.add("Budget")

add_tab.grid_columnconfigure(0, weight=1)
title_label = ctk.CTkLabel(add_tab, text="Add a New Expense", font=("Calibri", 20, "bold"))
title_label.grid(row=0, column=0, pady=20, sticky="ew")
amount_entry = ctk.CTkEntry(add_tab, placeholder_text="Amount", width=300)
amount_entry.grid(row=1, column=0, pady=10)
category_combobox = ctk.CTkComboBox(add_tab, values=CATEGORIES, width=300)
category_combobox.set(CATEGORIES[0])
category_combobox.grid(row=2, column=0, pady=10)
description_entry = ctk.CTkEntry(add_tab, placeholder_text="Description", width=300)
description_entry.grid(row=3, column=0, pady=10)
submit_button = ctk.CTkButton(add_tab, text="Submit Expense", command=submit_expense_callback)
submit_button.grid(row=4, column=0, pady=20)
status_label = ctk.CTkLabel(add_tab, text="")
status_label.grid(row=5, column=0, pady=10)

view_tab.grid_rowconfigure(0, weight=1)
view_tab.grid_columnconfigure(0, weight=1)
columns = ("ID", "Date", "Amount", "Category", "Description")
expense_table = ttk.Treeview(view_tab, columns=columns, show="headings")
for col in columns:
    expense_table.heading(col, text=col)
    expense_table.column(col, width=120, anchor="center")
expense_table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
delete_button = ctk.CTkButton(view_tab, text="Delete Selected Expense", command=delete_selected_expense_callback)
delete_button.grid(row=1, column=0, pady=10)

analysis_tab.grid_columnconfigure(0, weight=1)
analysis_title = ctk.CTkLabel(analysis_tab, text="Spending Analysis", font=("Calibri", 20, "bold"))
analysis_title.grid(row=0, column=0, sticky="ew", pady=(10, 20))
analysis_content_frame = ctk.CTkFrame(analysis_tab, fg_color="transparent")
analysis_content_frame.grid(row=1, column=0, sticky="nsew", padx=20)

budget_tab.grid_columnconfigure(0, weight=1)
budget_tab.grid_columnconfigure(1, weight=1)

set_budget_frame = ctk.CTkFrame(budget_tab)
set_budget_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
set_budget_frame.grid_columnconfigure(0, weight=1)
set_budget_title = ctk.CTkLabel(set_budget_frame, text="Set Monthly Budget", font=("Calibri", 16, "bold"))
set_budget_title.grid(row=0, column=0, padx=20, pady=(10, 5))
budget_month_entry = ctk.CTkEntry(set_budget_frame, placeholder_text="Month (YYYY-MM)")
budget_month_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
budget_amount_entry = ctk.CTkEntry(set_budget_frame, placeholder_text="Budget Amount")
budget_amount_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
set_budget_button = ctk.CTkButton(set_budget_frame, text="Set Budget", command=set_budget_callback)
set_budget_button.grid(row=3, column=0, padx=20, pady=10)
budget_status_label = ctk.CTkLabel(set_budget_frame, text="")
budget_status_label.grid(row=4, column=0, padx=20, pady=10)

check_status_frame = ctk.CTkFrame(budget_tab)
check_status_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
check_status_frame.grid_columnconfigure(0, weight=1)
check_status_title = ctk.CTkLabel(check_status_frame, text="Check Budget Status", font=("Calibri", 16, "bold"))
check_status_title.grid(row=0, column=0, padx=20, pady=(10, 5))
check_month_entry = ctk.CTkEntry(check_status_frame, placeholder_text="Month (YYYY-MM)")
check_month_entry.insert(0, datetime.now().strftime("%Y-%m"))
check_month_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
check_status_button = ctk.CTkButton(check_status_frame, text="Check Status", command=check_budget_status_callback)
check_status_button.grid(row=2, column=0, padx=20, pady=10)
budget_result_label = ctk.CTkLabel(check_status_frame, text="", justify="left", font=("Calibri", 14))
budget_result_label.grid(row=3, column=0, padx=20, pady=10)

budget_progress_bar = ctk.CTkProgressBar(check_status_frame, orientation="horizontal")
budget_progress_bar.set(0)
budget_progress_bar.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

app.mainloop()