# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import *
from reports import *

def setup_gui(root):
    # Variables
    global selected_id, category_var, amount_var, type_var, note_var
    global balance_var, filter_date_var, filter_category_var
    global budget_category_var, budget_limit_var
    
    selected_id = tk.IntVar(value=-1)
    category_var = tk.StringVar()
    amount_var = tk.StringVar()
    type_var = tk.StringVar(value="Expense")
    note_var = tk.StringVar()
    balance_var = tk.StringVar()
    filter_date_var = tk.StringVar()
    filter_category_var = tk.StringVar()
    budget_category_var = tk.StringVar()
    budget_limit_var = tk.StringVar()

    # Input Section
    input_frame = ttk.Frame(root, padding=(10, 5))
    input_frame.grid(row=0, column=0, sticky=tk.W)

    ttk.Label(input_frame, text="Category:").grid(row=0, column=0, sticky=tk.W)
    ttk.Entry(input_frame, textvariable=category_var).grid(row=0, column=1, pady=2)

    ttk.Label(input_frame, text="Amount:").grid(row=1, column=0, sticky=tk.W)
    ttk.Entry(input_frame, textvariable=amount_var).grid(row=1, column=1, pady=2)

    ttk.Label(input_frame, text="Type:").grid(row=2, column=0, sticky=tk.W)
    ttk.Combobox(input_frame, textvariable=type_var, 
                values=["Revenue", "Expense"]).grid(row=2, column=1, pady=2)

    ttk.Label(input_frame, text="Note:").grid(row=3, column=0, sticky=tk.W)
    ttk.Entry(input_frame, textvariable=note_var).grid(row=3, column=1, pady=2)

    btn_frame = ttk.Frame(input_frame)
    btn_frame.grid(row=4, column=0, columnspan=2, pady=5)
    global add_btn
    add_btn = ttk.Button(btn_frame, text="ADD", command=save_entry)
    add_btn.pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_frame, text="Clear", command=clear_fields).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_frame, text="Delete", command=delete_entry).pack(side=tk.LEFT, padx=2)

    # Filter Section
    filter_frame = ttk.Frame(root, padding=(10, 5))
    filter_frame.grid(row=0, column=1, sticky=tk.W)

    ttk.Label(filter_frame, text="Filter Date (YYYY-MM-DD):").grid(row=0, column=0)
    ttk.Entry(filter_frame, textvariable=filter_date_var).grid(row=0, column=1, pady=2)

    global filter_category_cb
    filter_category_cb = ttk.Combobox(filter_frame, textvariable=filter_category_var)
    ttk.Label(filter_frame, text="Filter Category:").grid(row=1, column=0)
    filter_category_cb.grid(row=1, column=1, pady=2)

    ttk.Button(filter_frame, text="Apply", command=refresh_table).grid(row=2, column=0, pady=5)
    ttk.Button(filter_frame, text="Clear", command=clear_filters).grid(row=2, column=1, pady=5)

    # Budget Section
    budget_frame = ttk.LabelFrame(root, text="Budget Limits", padding=(10, 5))
    budget_frame.grid(row=0, column=2, sticky=tk.W, padx=10)

    global budget_category_cb
    budget_category_cb = ttk.Combobox(budget_frame, textvariable=budget_category_var)
    ttk.Label(budget_frame, text="Category:").grid(row=0, column=0)
    budget_category_cb.grid(row=0, column=1, pady=2)

    ttk.Label(budget_frame, text="Monthly Limit:").grid(row=1, column=0)
    ttk.Entry(budget_frame, textvariable=budget_limit_var).grid(row=1, column=1, pady=2)

    ttk.Button(budget_frame, text="Set Limit", command=set_budget_limit).grid(row=2, column=0, pady=5)
    ttk.Button(budget_frame, text="Clear Limit", command=delete_budget_limit).grid(row=2, column=1, pady=5)

    # Table
    tree_frame = ttk.Frame(root)
    tree_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

    global tree
    columns = ("id", "Date", "Category", "Sum", "Type", "Note")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
    tree.column("id", width=0, stretch=tk.NO)

    for col in columns[1:]:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    tree.bind("<Double-1>", edit_selected)

    # Bottom controls
    bottom_frame = ttk.Frame(root)
    bottom_frame.grid(row=2, column=0, columnspan=3, pady=5)

    ttk.Label(bottom_frame, textvariable=balance_var, 
            font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT)
    ttk.Button(bottom_frame, text="Show Graphs", 
             command=lambda: show_graphs(root)).pack(side=tk.RIGHT, padx=5)
    ttk.Button(bottom_frame, text="Monthly Report", 
             command=lambda: show_monthly_report(root)).pack(side=tk.RIGHT, padx=5)

# Core application functions
def save_entry():
    if selected_id.get() == -1:
        insert_entry()
    else:
        update_entry()

def insert_entry():
    category = category_var.get()
    amount = amount_var.get()
    entry_type = type_var.get()
    note = note_var.get()

    if not category or not amount or not entry_type:
        return

    try:
        amount = float(amount)
    except ValueError:
        return

    save_transaction(category, amount, entry_type, note)
    clear_fields()
    refresh_table()

def update_entry():
    category = category_var.get()
    amount = amount_var.get()
    entry_type = type_var.get()
    note = note_var.get()

    try:
        amount = float(amount)
    except ValueError:
        return

    update_transaction(selected_id.get(), category, amount, entry_type, note)
    clear_fields()
    selected_id.set(-1)
    add_btn.config(text="ADD")
    refresh_table()

def delete_entry():
    if selected_id.get() == -1:
        return
        
    if messagebox.askyesno("Confirm Delete", "Delete this entry?"):
        delete_transaction(selected_id.get())
        clear_fields()
        selected_id.set(-1)
        add_btn.config(text="ADD")
        refresh_table()

def edit_selected(event):
    selected = tree.selection()
    if selected:
        item = tree.item(selected[0])
        values = item['values']
        selected_id.set(values[0])
        category_var.set(values[2])
        amount_var.set(values[3])
        type_var.set(values[4])
        note_var.set(values[5])
        add_btn.config(text="UPDATE")

def clear_fields():
    category_var.set("")
    amount_var.set("")
    type_var.set("Expense")
    note_var.set("")

def clear_filters():
    filter_date_var.set("")
    filter_category_var.set("")
    refresh_table()

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)

    data = get_transactions()
    revenue, expense = get_balance()
    balance_var.set(f"Current balance: {(revenue - expense):.2f}")

    filter_date = filter_date_var.get().strip()
    filter_category = filter_category_var.get().strip()
    limits = dict(get_budget_limits())
    category_expenses = {}

    for row in data:
        rowid, date_str, category, amount, entry_type, note = row
        if entry_type == 'Expense':
            category_expenses[category] = category_expenses.get(category, 0) + float(amount)
        
        if filter_date and not date_str.startswith(filter_date):
            continue
        if filter_category and category != filter_category:
            continue
            
        tags = ()
        if entry_type == 'Expense' and category in limits:
            if category_expenses.get(category, 0) > limits[category]:
                tags = ('over_budget',)
        
        tree.insert("", "end", values=(rowid, date_str, category, 
                                      f"{float(amount):.2f}", entry_type, note), tags=tags)
    
    tree.tag_configure('over_budget', background='#ffcccc')
    update_category_lists()

def update_category_lists():
    categories = get_categories()
    filter_category_cb['values'] = categories
    budget_category_cb['values'] = categories

def set_budget_limit():
    category = budget_category_var.get()
    try:
        limit = float(budget_limit_var.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid budget amount")
        return
        
    set_budget_limit(category, limit)
    budget_limit_var.set("")
    refresh_table()

def delete_budget_limit():
    category = budget_category_var.get()
    delete_budget_limit(category)
    budget_category_var.set("")
    budget_limit_var.set("")
    refresh_table()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    root.title("Personal Budgeting")
    setup_gui(root)
    refresh_table()
    root.mainloop()