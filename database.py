"""MySQL connection and schema setup for the Fashion Inventory Management System."""
import os
import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "fashioninv"),
    )

def initialize_database():
    cfg = dict(host=os.getenv("DB_HOST", "localhost"),
               port=int(os.getenv("DB_PORT", "3306")),
               user=os.getenv("DB_USER", "root"),
               password=os.getenv("DB_PASSWORD", ""))
    database = os.getenv("DB_NAME", "fashioninv")
    conn = mysql.connector.connect(**cfg)
    try:
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
        conn.commit()
    finally:
        conn.close()

def initialize_tables():
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory_items (
                sno INT AUTO_INCREMENT PRIMARY KEY,
                barcode VARCHAR(64) NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(100) NOT NULL,
                size VARCHAR(50) NOT NULL,
                color VARCHAR(50) NOT NULL,
                quantity BIGINT NOT NULL DEFAULT 0,
                cost DECIMAL(10,2) NOT NULL DEFAULT 0,
                supplier VARCHAR(255) NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                barcode VARCHAR(64) NOT NULL,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(100) NOT NULL,
                size VARCHAR(50) NOT NULL,
                color VARCHAR(50) NOT NULL,
                quantity BIGINT NOT NULL,
                unit_cost DECIMAL(10,2) NOT NULL,
                supplier VARCHAR(255) NOT NULL,
                sold_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()
