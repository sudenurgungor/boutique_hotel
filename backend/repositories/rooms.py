from psycopg2 import Error
from backend.database import get_connection, _handle_error


def get_all_rooms():
    """
    rooms tablosundaki tüm odaları döndürür.
    Her bir oda için: (id, room_number, room_type_name, floor, status) gelir.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.id,
                   r.room_number,
                   rt.name AS room_type_name,
                   r.floor,
                   r.status
            FROM rooms r
            JOIN room_types rt ON r.room_type_id = rt.id
            ORDER BY r.id;
            """
        )
        return cursor.fetchall()
    except Error as e:
        _handle_error("⛔ Oda listesi alınırken hata oluştu:", e)
        return []
    finally:
        if conn is not None:
            conn.close()


def update_room_status(room_id: int, new_status: str) -> bool:
    """
    Verilen oda ID'sinin durumunu günceller.
    Örnek status: CLEAN, OCCUPIED, DIRTY, MAINTENANCE
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE rooms
            SET status = %s
            WHERE id = %s
            """,
            (new_status, room_id),
        )

        conn.commit()
        print(f"✅ Oda (id={room_id}) durumu '{new_status}' olarak güncellendi.")
        return True

    except Error as e:
        _handle_error("⛔ Oda durumu güncellenirken hata oluştu:", e)
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()


def get_free_rooms():
    """
    Müsait odaları döndürür.
    Basit versiyon: sadece status CLEAN/AVAILABLE olan odalar.
    (id, room_number, room_type_name)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.id, r.room_number, rt.name
            FROM rooms r
            JOIN room_types rt ON r.room_type_id = rt.id
            WHERE r.status IN ('CLEAN', 'AVAILABLE')
            ORDER BY r.room_number;
            """
        )
        return cursor.fetchall()
    except Error as e:
        _handle_error("⛔ Müsait odalar alınırken hata oluştu:", e)
        return []
    finally:
        if conn:
            conn.close()


def get_nightly_price_for_room(room_id: int) -> float | None:
    """
    Verilen oda için room_types.base_price değerini döndürür.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT rt.base_price
            FROM rooms r
            JOIN room_types rt ON r.room_type_id = rt.id
            WHERE r.id = %s;
            """,
            (room_id,),
        )
        row = cursor.fetchone()
        return float(row[0]) if row and row[0] is not None else None
    except Error as e:
        _handle_error("⛔ Gecelik ücret alınırken hata oluştu:", e)
        return None
    finally:
        if conn:
            conn.close()
