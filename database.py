# database.py
import sqlite3
from datetime import datetime

DATABASE = "budget.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (date TEXT, category TEXT, amount REAL, 
                  type TEXT, note TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS budget_limits
                 (category TEXT PRIMARY KEY, monthly_limit REAL)''')
    conn.commit()
    conn.close()

def execute_query(query, params=()):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    result = c.fetchall()
    conn.close()
    return result

# Transaction operations
def save_transaction(category, amount, entry_type, note):
    return execute_query(
        '''INSERT INTO transactions (date, category, amount, type, note)
           VALUES (?, ?, ?, ?, ?)''',
        (datetime.now().strftime("%Y-%m-%d %H:%M"), category, amount, entry_type, note)
    )

def update_transaction(transaction_id, category, amount, entry_type, note):
    return execute_query(
        '''UPDATE transactions SET
           category=?, amount=?, type=?, note=?
           WHERE rowid=?''',
        (category, amount, entry_type, note, transaction_id)
    )

def delete_transaction(transaction_id):
    return execute_query("DELETE FROM transactions WHERE rowid=?", (transaction_id,))

def get_transactions():
    return execute_query("SELECT rowid, date, category, amount, type, note FROM transactions")

# Budget operations
def set_budget_limit(category, limit):
    return execute_query(
        '''INSERT OR REPLACE INTO budget_limits (category, monthly_limit)
           VALUES (?, ?)''', (category, limit))

def delete_budget_limit(category):
    return execute_query("DELETE FROM budget_limits WHERE category=?", (category,))

def get_budget_limits():
    return execute_query("SELECT category, monthly_limit FROM budget_limits")

# Reporting functions
def get_balance():
    result = execute_query('''SELECT 
        SUM(CASE WHEN type="Revenue" THEN amount ELSE 0 END),
        SUM(CASE WHEN type="Expense" THEN amount ELSE 0 END)
        FROM transactions''')
    return result[0] if result else (0, 0)

def get_monthly_summary(month=None):
    query = '''SELECT strftime('%Y-%m', date) as month,
               SUM(CASE WHEN type="Revenue" THEN amount ELSE 0 END),
               SUM(CASE WHEN type="Expense" THEN amount ELSE 0 END)
               FROM transactions'''
    params = ()
    
    if month:
        query += " WHERE strftime('%Y-%m', date) = ?"
        params = (month,)
    
    query += " GROUP BY month ORDER BY month DESC"
    return execute_query(query, params)

def get_category_expenses(month):
    return execute_query('''SELECT category, SUM(amount) 
                            FROM transactions 
                            WHERE type="Expense" 
                            AND strftime('%Y-%m', date) = ?
                            GROUP BY category''', (month,))

def get_categories():
    result = execute_query("SELECT DISTINCT category FROM transactions")
    return [row[0] for row in result]