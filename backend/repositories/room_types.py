from psycopg2 import Error
from backend.database import get_connection, _handle_error


def get_all_room_types():
    """
    room_types tablosundaki tüm kayıtları döndürür.
    (id, name, description, base_price, capacity)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id,
                   name,
                   description,
                   base_price,
                   (capacity_adult + capacity_child) AS capacity
            FROM room_types
            ORDER BY id;
            """
        )
        return cursor.fetchall()
    except Error as e:
        _handle_error("⛔ Oda tipleri alınırken hata oluştu:", e)
        return []
    finally:
        if conn:
            conn.close()


def insert_room_type(
    name: str,
    description: str | None,
    base_price: float,
    capacity: int,
) -> int | None:
    """
    Yeni bir oda tipi ekler. Başarılı olursa id döner.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO room_types (name, description, base_price, capacity_adult, capacity_child)
            VALUES (%s, %s, %s, %s, 0)
            RETURNING id;
            """,
            (name, description, base_price, capacity),
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Yeni oda tipi eklendi. ID={new_id}")
        return new_id
    except Error as e:
        _handle_error("⛔ Oda tipi eklenirken hata oluştu:", e)
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def update_room_type(
    rt_id: int,
    name: str,
    description: str | None,
    base_price: float,
    capacity: int,
) -> bool:
    """
    Var olan oda tipini günceller.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE room_types
            SET name = %s,
                description = %s,
                base_price = %s,
                capacity_adult = %s,
                capacity_child = 0
            WHERE id = %s;
            """,
            (name, description, base_price, capacity, rt_id),
        )
        conn.commit()
        print(f"✅ Oda tipi (id={rt_id}) güncellendi.")
        return True
    except Error as e:
        _handle_error("⛔ Oda tipi güncellenirken hata oluştu:", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def delete_room_type(rt_id: int) -> bool:
    """
    Oda tipini siler. (Bağlı oda varsa FK yüzünden hata alabilir.)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM room_types WHERE id = %s;", (rt_id,))
        conn.commit()
        print(f"✅ Oda tipi (id={rt_id}) silindi.")
        return True
    except Error as e:
        _handle_error("⛔ Oda tipi silinirken hata oluştu:", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
