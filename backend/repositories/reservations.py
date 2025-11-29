from datetime import date
from psycopg2 import Error
from backend.database import get_connection, _handle_error


def get_all_reservations():
    """
    Rezervasyonları misafir ve oda bilgisiyle birlikte döndürür.
    Örnek satır:
    (id, guest_full_name, room_number, check_in_date, check_out_date, status, total_amount)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.id,
                   g.first_name || ' ' || g.last_name AS guest_name,
                   rm.room_number,
                   r.check_in_date,
                   r.check_out_date,
                   r.status,
                   r.total_amount
            FROM reservations r
            JOIN guests g ON r.guest_id = g.id
            JOIN rooms rm ON r.room_id = rm.id
            ORDER BY r.check_in_date DESC, r.id DESC;
            """
        )
        return cursor.fetchall()
    except Error as e:
        _handle_error("⛔ Rezervasyon listesi alınırken hata oluştu:", e)
        return []
    finally:
        if conn:
            conn.close()


def room_has_conflict(room_id: int, check_in: date, check_out: date) -> bool:
    """
    Verilen oda için, verilen tarih aralığında (check_in, check_out)
    çakışan CONFIRMED veya CHECKED_IN rezervasyon var mı diye kontrol eder.

    Çakışma varsa True, yoksa False döner.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM reservations
            WHERE room_id = %s
              AND status IN ('CONFIRMED', 'CHECKED_IN')
              AND NOT (
                    check_out_date <= %s
                OR  check_in_date >= %s
              )
            LIMIT 1;
            """,
            (room_id, check_in, check_out),
        )

        row = cursor.fetchone()
        return row is not None

    except Error as e:
        _handle_error("⛔ Müsaitlik kontrolü yapılırken hata oluştu:", e)
        return True  # hata durumunda "sanki doluymuş" gibi davranmak daha güvenli
    finally:
        if conn:
            conn.close()


def insert_reservation(
    guest_id: int,
    room_id: int,
    check_in: date,
    check_out: date,
    nightly_amount: float,
    status: str = "CONFIRMED",
) -> int | None:
    """
    Yeni rezervasyon ekler.
    total_amount otomatik olarak gece sayısı * nightly_amount şeklinde hesaplanır.
    """
    conn = None
    try:
        nights = (check_out - check_in).days
        if nights <= 0:
            print("⛔ Gece sayısı 0 veya negatif olamaz.")
            return None

        total_amount = nightly_amount * nights

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO reservations
                (guest_id, room_id, check_in_date, check_out_date,
                 status, nightly_price, total_amount, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id;
            """,
            (guest_id, room_id, check_in, check_out, status, nightly_amount, total_amount),
        )

        new_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Yeni rezervasyon eklendi. ID = {new_id}")
        return new_id

    except Error as e:
        _handle_error("⛔ Rezervasyon eklenirken hata oluştu:", e)
        if conn:
            conn.rollback()
        return None

    finally:
        if conn:
            conn.close()


def update_reservation_status(reservation_id: int, new_status: str) -> bool:
    """
    Rezervasyon durumunu günceller.
    Örnek durumlar: CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE reservations
            SET status = %s
            WHERE id = %s;
            """,
            (new_status, reservation_id),
        )
        conn.commit()
        print(f"✅ Rezervasyon (id={reservation_id}) durumu '{new_status}' yapıldı.")
        return True
    except Error as e:
        _handle_error("⛔ Rezervasyon durumu güncellenirken hata oluştu:", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
