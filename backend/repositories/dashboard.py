from datetime import datetime
from psycopg2 import Error
from backend.database import get_connection, _handle_error


def get_dashboard_stats():
    """
    Dashboard için:
      - total_rooms
      - reservations_this_month
      - active_guests
      - occupancy_rate (0-1 arası)
    döndürür.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM rooms;")
        total_rooms = cursor.fetchone()[0] or 0

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM reservations
            WHERE date_trunc('month', check_in_date) = date_trunc('month', CURRENT_DATE);
            """
        )
        reservations_this_month = cursor.fetchone()[0] or 0

        cursor.execute(
            """
            SELECT COUNT(DISTINCT guest_id)
            FROM reservations
            WHERE status IN ('CONFIRMED', 'CHECKED_IN')
              AND check_in_date <= CURRENT_DATE
              AND check_out_date > CURRENT_DATE;
            """
        )
        active_guests = cursor.fetchone()[0] or 0

        cursor.execute(
            """
            SELECT COUNT(DISTINCT room_id)
            FROM reservations
            WHERE status IN ('CONFIRMED', 'CHECKED_IN')
              AND check_in_date <= CURRENT_DATE
              AND check_out_date > CURRENT_DATE;
            """
        )
        occupied_rooms = cursor.fetchone()[0] or 0

        occupancy_rate = float(occupied_rooms) / float(total_rooms) if total_rooms > 0 else 0.0

        return total_rooms, reservations_this_month, active_guests, occupancy_rate

    except Error as e:
        _handle_error("⛔ Dashboard istatistikleri alınırken hata oluştu:", e)
        return 0, 0, 0, 0.0
    finally:
        if conn:
            conn.close()


def get_yearly_reservation_stats(year: int | None = None):
    """
    Verilen yıl için aylık rezervasyon sayılarını döndürür.
    [(1, count), (2, count), ...] gibi.
    year None ise CURRENT_DATE yılını kullanır.
    """
    if year is None:
        year = datetime.now().year

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT EXTRACT(MONTH FROM check_in_date)::int AS m,
                   COUNT(*) AS c
            FROM reservations
            WHERE EXTRACT(YEAR FROM check_in_date) = %s
            GROUP BY m
            ORDER BY m;
            """,
            (year,),
        )
        rows = cursor.fetchall()
        return rows
    except Error as e:
        _handle_error("⛔ Yıllık rezervasyon istatistikleri alınırken hata oluştu:", e)
        return []
    finally:
        if conn:
            conn.close()
