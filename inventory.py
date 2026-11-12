"""Inventory CRUD, filtering, and barcode-based sale tracking."""
from database import connect_db

def add_item(barcode, name, type_, size, color, quantity, cost, supplier):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""INSERT INTO inventory_items
            (barcode,name,type,size,color,quantity,cost,supplier)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (barcode, name, type_, size, color, int(quantity), float(cost), supplier))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def update_item(sno, barcode, name, type_, size, color, quantity, cost, supplier):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""UPDATE inventory_items SET barcode=%s,name=%s,type=%s,size=%s,
            color=%s,quantity=%s,cost=%s,supplier=%s WHERE sno=%s""",
            (barcode, name, type_, size, color, int(quantity), float(cost), supplier, sno))
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def delete_item(sno):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM inventory_items WHERE sno=%s", (sno,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def clear_all_inventory():
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM inventory_items")
        conn.commit()
    finally:
        conn.close()

def get_inventory():
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""SELECT sno,barcode,name,type,size,color,quantity,cost,supplier
            FROM inventory_items ORDER BY sno""")
        return cur.fetchall()
    finally:
        conn.close()

def record_sale(barcode, quantity_sold):
    quantity_sold = int(quantity_sold)
    if quantity_sold <= 0:
        raise ValueError("Sale quantity must be greater than zero.")
    conn = connect_db()
    try:
        conn.start_transaction()
        cur = conn.cursor()
        cur.execute("""SELECT sno,barcode,name,type,size,color,quantity,cost,supplier
            FROM inventory_items WHERE barcode=%s FOR UPDATE""", (barcode,))
        item = cur.fetchone()
        if not item:
            raise ValueError("No inventory item matches that barcode.")
        if quantity_sold > int(item[6]):
            raise ValueError(f"Only {item[6]} item(s) are currently in stock.")
        cur.execute("""INSERT INTO sales
            (barcode,name,type,size,color,quantity,unit_cost,supplier)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (item[1],item[2],item[3],item[4],item[5],quantity_sold,item[7],item[8]))
        cur.execute("UPDATE inventory_items SET quantity=quantity-%s WHERE sno=%s",
                    (quantity_sold,item[0]))
        conn.commit()
        return item
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_sales_summary():
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""SELECT barcode,name,SUM(quantity) AS items_sold
            FROM sales GROUP BY barcode,name ORDER BY items_sold DESC""")
        return cur.fetchall()
    finally:
        conn.close()
