import sqlite3
import os

# Xác định thư mục gốc project một cách đáng tin cậy, bất kể chạy từ đâu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # .../src/db
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))       # .../Movie_Recommend_System

SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')
DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'app.db')

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    schema_sql = f.read()

cursor.executescript(schema_sql)
conn.commit()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Các bảng đã tạo:", cursor.fetchall())

cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (1)")
conn.commit()

cursor.execute("SELECT * FROM users")
print("Users:", cursor.fetchall())
print("DB path:", DB_PATH)

conn.close()