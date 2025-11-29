"""
UI katmanının çağıracağı servis/facade.
Repository fonksiyonlarını toplayıp aynı isimlerle dışarı verir.
"""

from datetime import date
from backend import database
from backend.repositories import (
    rooms as rooms_repo,
    room_types as room_types_repo,
    guests as guests_repo,
    reservations as reservations_repo,
    dashboard as dashboard_repo,
)

# Bağlantı/doğrudan erişmesi gereken noktalar için dışarı açıyoruz
get_connection = database.get_connection
last_error = database.last_error


# ROOMS
def get_all_rooms():
    return rooms_repo.get_all_rooms()


def update_room_status(room_id: int, new_status: str) -> bool:
    return rooms_repo.update_room_status(room_id, new_status)


def get_free_rooms():
    return rooms_repo.get_free_rooms()


def get_nightly_price_for_room(room_id: int) -> float | None:
    return rooms_repo.get_nightly_price_for_room(room_id)


# ROOM TYPES
def get_all_room_types():
    return room_types_repo.get_all_room_types()


def insert_room_type(name: str, description: str | None, base_price: float, capacity: int) -> int | None:
    return room_types_repo.insert_room_type(name, description, base_price, capacity)


def update_room_type(rt_id: int, name: str, description: str | None, base_price: float, capacity: int) -> bool:
    return room_types_repo.update_room_type(rt_id, name, description, base_price, capacity)


def delete_room_type(rt_id: int) -> bool:
    return room_types_repo.delete_room_type(rt_id)


# GUESTS
def get_all_guests():
    return guests_repo.get_all_guests()


def insert_guest(first_name: str, last_name: str, email: str = None, phone: str = None, tc_no: str = None) -> int | None:
    return guests_repo.insert_guest(first_name, last_name, email, phone, tc_no)


def update_guest(guest_id: int, first_name: str, last_name: str, email: str = None, phone: str = None, tc_no: str = None) -> bool:
    return guests_repo.update_guest(guest_id, first_name, last_name, email, phone, tc_no)


def delete_guest(guest_id: int) -> bool:
    return guests_repo.delete_guest(guest_id)


def get_guests_without_reservation():
    return guests_repo.get_guests_without_reservation()


# RESERVATIONS
def get_all_reservations():
    return reservations_repo.get_all_reservations()


def room_has_conflict(room_id: int, check_in: date, check_out: date) -> bool:
    return reservations_repo.room_has_conflict(room_id, check_in, check_out)


def insert_reservation(
    guest_id: int,
    room_id: int,
    check_in: date,
    check_out: date,
    nightly_amount: float,
    status: str = "CONFIRMED",
) -> int | None:
    return reservations_repo.insert_reservation(guest_id, room_id, check_in, check_out, nightly_amount, status)


def update_reservation_status(reservation_id: int, new_status: str) -> bool:
    return reservations_repo.update_reservation_status(reservation_id, new_status)


# DASHBOARD
def get_dashboard_stats():
    return dashboard_repo.get_dashboard_stats()


def get_yearly_reservation_stats(year: int | None = None):
    return dashboard_repo.get_yearly_reservation_stats(year)


# TEST
def test_connection():
    conn = None
    try:
        conn = database.get_connection()
        print("Veritabanına bağlantı BAŞARILI!")
    except Exception as e:
        print("Bağlantı sırasında hata oluştu:")
        print(e)
    finally:
        if conn is not None:
            conn.close()
            print("Bağlantı kapatıldı.")
