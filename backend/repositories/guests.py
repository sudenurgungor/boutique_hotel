from psycopg2 import Error
from backend.database import get_connection, _handle_error


def get_all_guests():
    """
    guests tablosundaki tüm misafirleri döndürür.
    Örnek dönen satır: (id, first_name, last_name, email, phone, tc_no, is_blacklisted)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id,
                   first_name,
                   last_name,
                   email,
                   phone,
                   identity_number AS tc_no,
                   is_blacklisted
            FROM guests
            ORDER BY id;
            """
        )
        rows = cursor.fetchall()
        return rows
    except Error as e:
        _handle_error("⛔ Misafir listesi alınırken hata oluştu:", e)
        return []
    finally:
        if conn:
            conn.close()


def insert_guest(
    first_name: str,
    last_name: str,
    email: str = None,
    phone: str = None,
    tc_no: str = None,
) -> int | None:
    """
    Yeni bir misafir ekler. Başarılı olursa eklenen misafirin id'sini döner.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO guests (first_name, last_name, email, phone, identity_number, is_blacklisted, created_at)
            VALUES (%s, %s, %s, %s, %s, FALSE, NOW())
            RETURNING id;
            """,
            (first_name, last_name, email, phone, tc_no),
        )

        new_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Yeni misafir eklendi. ID = {new_id}")
        return new_id

    except Error as e:
        _handle_error("⛔ Misafir eklenirken hata oluştu:", e)
        if conn:
            conn.rollback()
        return None

    finally:
        if conn:
            conn.close()


def update_guest(
    guest_id: int,
    first_name: str,
    last_name: str,
    email: str = None,
    phone: str = None,
    tc_no: str = None,
) -> bool:
    """
    Var olan bir misafirin bilgilerini günceller.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE guests
            SET first_name = %s,
                last_name  = %s,
                email      = %s,
                phone      = %s,
                identity_number = %s
            WHERE id = %s;
            """,
            (first_name, last_name, email, phone, tc_no, guest_id),
        )

        conn.commit()
        print(f"✅ Misafir (id={guest_id}) güncellendi.")
        return True

    except Error as e:
        _handle_error("⛔ Misafir güncellenirken hata oluştu:", e)
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()


def delete_guest(guest_id: int) -> bool:
    """
    Misafiri siler. (Rezervasyonu varsa FK yüzünden hata alabilir.)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM guests WHERE id = %s;", (guest_id,))
        conn.commit()
        print(f"✅ Misafir (id={guest_id}) silindi.")
        return True
    except Error as e:
        _handle_error("⛔ Misafir silinirken hata oluştu:", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def get_guests_without_reservation():
    """
    Hiç rezervasyonu olmayan misafirleri döndürür.
    (id, first_name, last_name)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT g.id, g.first_name, g.last_name
            FROM guests g
            WHERE NOT EXISTS (
                SELECT 1 FROM reservations r
                WHERE r.guest_id = g.id
            )
            ORDER BY g.id;
            """
        )
        return cursor.fetchall()
    except Error as e:
        _handle_error("⛔ Rezervasyonu olmayan misafirler alınırken hata:", e)
        return []
    finally:
        if conn:
            conn.close()
