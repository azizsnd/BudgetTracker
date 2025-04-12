# reports.py
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk
from database import get_transactions, get_monthly_summary, get_category_expenses, get_budget_limits

def show_graphs(parent):
    graph_window = tk.Toplevel(parent)
    graph_window.title("Spending Insights")
    
    frame_pie = tk.Frame(graph_window)
    frame_pie.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    frame_bar = tk.Frame(graph_window)
    frame_bar.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    data = get_transactions()
    
    # Pie Chart
    expenses = [row for row in data if row[4] == 'Expense']
    category_totals = {}
    for row in expenses:
        category_totals[row[2]] = category_totals.get(row[2], 0) + float(row[3])
    
    fig_pie = Figure(figsize=(5, 4), dpi=100)
    ax_pie = fig_pie.add_subplot(111)
    if category_totals:
        labels, sizes = zip(*category_totals.items())
        ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax_pie.set_title('Expenses by Category')
    else:
        ax_pie.text(0.5, 0.5, 'No expense data', ha='center', va='center')
    canvas_pie = FigureCanvasTkAgg(fig_pie, master=frame_pie)
    canvas_pie.draw()
    canvas_pie.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    NavigationToolbar2Tk(canvas_pie, frame_pie).update()

    # Bar Chart
    total_revenue = sum(float(row[3]) for row in data if row[4] == 'Revenue')
    total_expense = sum(float(row[3]) for row in data if row[4] == 'Expense')
    
    fig_bar = Figure(figsize=(5, 4), dpi=100)
    ax_bar = fig_bar.add_subplot(111)
    if total_revenue or total_expense:
        ax_bar.bar(['Revenue', 'Expense'], [total_revenue, total_expense], 
                  color=['green', 'red'])
        ax_bar.set_title('Total Revenue vs Expense')
        ax_bar.set_ylabel('Amount')
    else:
        ax_bar.text(0.5, 0.5, 'No data available', ha='center', va='center')
    canvas_bar = FigureCanvasTkAgg(fig_bar, master=frame_bar)
    canvas_bar.draw()
    canvas_bar.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    NavigationToolbar2Tk(canvas_bar, frame_bar).update()

def show_monthly_report(parent):
    report_window = tk.Toplevel(parent)
    report_window.title("Monthly Report")
    
    months = [row[0] for row in get_monthly_summary()]
    month_var = tk.StringVar()
    
    ttk.Label(report_window, text="Select Month:").pack(pady=5)
    month_cb = ttk.Combobox(report_window, textvariable=month_var, values=months)
    month_cb.pack(pady=5)
    
    report_frame = ttk.Frame(report_window)
    report_frame.pack(padx=10, pady=10)
    
    def generate_report():
        for widget in report_frame.winfo_children():
            widget.destroy()
        
        month = month_var.get()
        if not month:
            return
            
        summary = get_monthly_summary(month)[0]
        limits = dict(get_budget_limits())
        category_expenses = dict(get_category_expenses(month))
        
        # Report layout
        ttk.Label(report_frame, text=f"Month: {month}", 
                 font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2)
        
        row = 1
        ttk.Label(report_frame, text="Total Revenue:").grid(row=row, column=0, sticky=tk.W)
        ttk.Label(report_frame, text=f"{summary[1]:.2f}").grid(row=row, column=1, sticky=tk.E)
        row += 1
        
        ttk.Label(report_frame, text="Total Expenses:").grid(row=row, column=0, sticky=tk.W)
        ttk.Label(report_frame, text=f"{summary[2]:.2f}").grid(row=row, column=1, sticky=tk.E)
        row += 1
        
        net_balance = summary[1] - summary[2]
        ttk.Label(report_frame, text="Net Balance:").grid(row=row, column=0, sticky=tk.W)
        ttk.Label(report_frame, text=f"{net_balance:.2f}", 
                 foreground="green" if net_balance >=0 else "red").grid(row=row, column=1, sticky=tk.E)
        row += 1
        
        ttk.Separator(report_frame).grid(row=row, columnspan=2, sticky='ew', pady=5)
        row += 1
        
        ttk.Label(report_frame, text="Category Budgets", 
                 font=('Helvetica', 10, 'bold')).grid(row=row, columnspan=2)
        row += 1
        
        for category, spent in category_expenses.items():
            limit = limits.get(category, 0)
            ttk.Label(report_frame, text=category).grid(row=row, column=0, sticky=tk.W)
            ttk.Label(report_frame, text=f"Spent: {spent:.2f}").grid(row=row, column=1, sticky=tk.E)
            row += 1
            
            if limit:
                remaining = limit - spent
                ttk.Label(report_frame, text=f"Budget: {limit:.2f}").grid(row=row, column=0, sticky=tk.W)
                ttk.Label(report_frame, 
                         text=f"Remaining: {remaining:.2f}" if remaining >=0 else "Over budget!",
                         foreground="green" if remaining >=0 else "red").grid(row=row, column=1, sticky=tk.E)
                row += 1
    
    ttk.Button(report_window, text="Generate Report", command=generate_report).pack(pady=10)