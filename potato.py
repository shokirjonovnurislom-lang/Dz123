import sqlite3
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
DB_FILE = "orders.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_conn()
conn.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        price INTEGER,
        is_active INTEGER DEFAULT 1
    )
""")
conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        service TEXT,
        quantity INTEGER,
        status TEXT,
        created_at TEXT
    )
""")

if conn.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0:
    conn.executemany("INSERT INTO services (title, price) VALUES (?, ?)", [
        ("Pepperoni Pizza", 85000),
        ("Margarita Pizza", 65000),
        ("Combo Set", 120000)
    ])
    conn.executemany("INSERT INTO orders (name, phone, service, quantity, status, created_at) VALUES (?, ?, ?, ?, ?, ?)", [
        ("Ali", "+998901234567", "Pepperoni Pizza", 2, "new", "2026-11-23 10:00"),
        ("Madina", "+998937654321", "Combo Set", 1, "cooking", "2026-11-23 11:30")
    ])
    conn.commit()
conn.close()

class OrderIn(BaseModel):
    name: str
    phone: str
    service: str
    quantity: int = 1

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

@app.get("/api/services")
def get_services():
    with get_conn() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM services WHERE is_active = 1").fetchall()]

@app.get("/api/orders")
def get_orders():
    with get_conn() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()]

@app.post("/api/orders")
def create_order(order: OrderIn):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO orders (name, phone, service, quantity, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (order.name, order.phone, order.service, order.quantity, "new", created_at)
        )
        conn.commit()
        return {"id": cur.lastrowid, "status": "saved"}