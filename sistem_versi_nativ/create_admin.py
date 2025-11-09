import sqlite3
from passlib.context import CryptContext
import getpass # Untuk input password tersembunyi
from datetime import datetime # Diperlukan untuk tabel log

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Buat tabel user
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,  -- <-- PERBAIKAN DI SINI
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            organization_name TEXT,
            user_api_key TEXT
        )
    ''')
    
    # Buat tabel log
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            username TEXT,
            organization_name TEXT,
            action TEXT,
            details TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_admin():
    print("--- Pembuatan Akun Admin ---")
    try:
        username = input("Username Admin: ")
        password = getpass.getpass("Password Admin: ")
        organization = input("Nama Instansi (Admin): ")
        
        password_hash = pwd_context.hash(password)
        role = 'admin'
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, password_hash, role, organization_name) VALUES (?, ?, ?, ?)",
            (username, password_hash, role, organization)
        )
        conn.commit()
        conn.close()
        print(f"\n✅ Akun admin '{username}' untuk instansi '{organization}' berhasil dibuat.")
        
    except sqlite3.IntegrityError:
        print(f"\n❌ Gagal: Username '{username}' sudah ada.")
    except Exception as e:
        print(f"\n❌ Terjadi error: {e}")

if __name__ == "__main__":
    # 1. Pastikan tabel ada
    create_tables()
    # 2. Tambahkan admin baru
    add_admin()