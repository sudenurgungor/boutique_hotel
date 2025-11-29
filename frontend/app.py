# ui_main.py
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as mb
from datetime import date, datetime
from backend.services import hotel_service as db
from frontend import theme
from frontend.views import dashboard_view, reservations_view, rooms_view, room_types_view, guests_view
import sys, traceback

# Tema: LIGHT + pastel
theme.apply_appearance()

# Hata olursa konsola ve diyaloga yaz
def _tk_excepthook(exc_type, exc_value, exc_traceback):
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    try:
        mb.showerror("Hata", f"{exc_type.__name__}: {exc_value}")
    except Exception:
        pass

sys.excepthook = _tk_excepthook


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Poppins fontlarini yukle ---
        theme.load_fonts()

        # Uygulama genelinde kullanacagimiz font setleri
        self.font_header = theme.FONT_SETS["header"]
        self.font_sidebar = theme.FONT_SETS["sidebar"]
        self.font_title = theme.FONT_SETS["title"]
        self.font_subtitle = theme.FONT_SETS["subtitle"]
        self.font_card_type = theme.FONT_SETS["card_type"]
        self.font_card_number = theme.FONT_SETS["card_number"]
        self.font_badge = theme.FONT_SETS["badge"]
        self.font_floor = theme.FONT_SETS["floor"]
        self.font_normal = theme.FONT_SETS["normal"]

        # Modern acik/lila tema
        colors = theme.COLORS
        self.color_bg = colors["bg"]
        self.color_panel = colors["panel"]
        self.color_card = colors["card"]
        self.color_sidebar = colors["sidebar"]
        self.color_sidebar_dark = colors["sidebar_dark"]
        self.color_sidebar_light = colors["sidebar_light"]
        self.color_accent = colors["accent"]
        self.color_accent_alt = colors["accent_alt"]
        self.color_text_main = colors["text_main"]
        # Misafir duzenleme icin secili ID (None ise yeni kayit modundayiz)
        self.selected_guest_id = None

        # Rezervasyon combobox map'leri
        self.guest_choice_map = {}
        self.room_choice_map = {}

        # Oda tipi duzenleme icin secili id
        self.selected_room_type_id = None
        # Oda durum menusu penceresi
        self.status_popup = None

        # Pencere basligi ve boyutu
        self.title("Boutique Hotel Management")
        self.geometry("1150x700")
        self.minsize(1150, 700)

        # Ana pencere arka plani (mint pastel)
        self.configure(fg_color=self.color_bg)

        # ===== UST BAR =====
        topbar = ctk.CTkFrame(self, fg_color=self.color_sidebar, corner_radius=18)
        topbar.pack(fill="x", padx=20, pady=(15, 10))

        top_left = ctk.CTkFrame(topbar, fg_color="transparent")
        top_left.pack(side="left", padx=12, pady=10)

        # Logo kullanmıyoruz; sadece boşluk bırak
        ctk.CTkLabel(top_left, text="", fg_color="transparent").pack(anchor="w", pady=(4, 4))

        top_right = ctk.CTkFrame(topbar, fg_color="transparent")
        top_right.pack(side="right", padx=12, pady=10)

        self.entry_search = ctk.CTkEntry(
            top_right,
            width=240,
            height=34,
            font=self.font_normal,
            placeholder_text="Ara (misafir, oda, rezervasyon)"
        )
        self.entry_search.pack(side="left", padx=(0, 10))

        quick_new_res = ctk.CTkButton(
            top_right,
            text="Yeni Rezervasyon",
            font=self.font_normal,
            fg_color=self.color_accent,
            hover_color="#f27a67",
            text_color="#0b1724",
            height=34,
            command=self.show_reservations_view
        )
        quick_new_res.pack(side="left")

        # ===== ANA FRAME (Sol menu + Sag icerik) =====
        main_frame = ctk.CTkFrame(self, corner_radius=24, fg_color=self.color_panel)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ----- SOL SIDEBAR -----
        self.sidebar = ctk.CTkFrame(
            main_frame,
            width=200,
            corner_radius=28,
            fg_color=self.color_sidebar
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 12), pady=12)

        logo_label = ctk.CTkLabel(
            self.sidebar,
            text="BS HOTEL\nAdmin Paneli",
            justify="center",
            font=("Poppins", 15, "bold"),
            text_color="#f8fafc"
        )
        logo_label.pack(pady=(16, 24))

        # Nav butonları (metin)
        nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_container.pack(fill="both", expand=True, pady=10, padx=0)

        self.nav_buttons = []
        self.btn_dashboard = self._create_nav_button(nav_container, "🏠 Dashboard", self.show_dashboard)
        self.btn_rooms = self._create_nav_button(nav_container, "🛏️ Oda Yonetimi", self.show_rooms_view)
        self.btn_room_types = self._create_nav_button(nav_container, "🏷️ Oda Tipleri", self.show_room_types_view)
        self.btn_guests = self._create_nav_button(nav_container, "👥 Misafirler", self.show_guests_view)
        self.btn_reservations = self._create_nav_button(nav_container, "🗓️ Rezervasyonlar", self.show_reservations_view)

        self.btn_logout = ctk.CTkButton(
            self.sidebar,
            text="Exit",
            anchor="w",
            fg_color="#fcd34d",
            hover_color="#fbbf24",
            text_color="#7c2d12",
            font=self.font_sidebar
        )
        self.btn_logout.pack(fill="x", padx=18, pady=(20, 15), side="bottom")

        # ----- SAG ICERIK ALANI -----
        self.content = ctk.CTkFrame(
            main_frame,
            corner_radius=24,
            fg_color=self.color_card
        )
        self.content.pack(side="left", fill="both", expand=True, pady=15, padx=(0, 15))

        # Ekranlar
        self.dashboard_frame = self.create_dashboard_frame(self.content)
        self.rooms_frame = self.create_rooms_frame(self.content)
        self.room_types_frame = self.create_room_types_frame(self.content)
        self.guests_frame = self.create_guests_frame(self.content)
        self.reservations_frame = self.create_reservations_frame(self.content)

        # Baslangicta oda ekrani
        self.show_rooms_view()
        self.set_active_nav(self.btn_rooms)

    def show_login(self) -> bool:
        # Login ekranı devre dışı: her zaman izin ver
        return True

    # ============================================================
    # DASHBOARD
    # ============================================================
    def create_dashboard_frame(self, parent):
        return dashboard_view.create_dashboard_frame(self, parent)

    def refresh_dashboard(self):
        dashboard_view.refresh_dashboard(self)

    # ============================================================
    # ODA YONETIMI
    # ============================================================
    def create_rooms_frame(self, parent):
        return rooms_view.create_rooms_frame(self, parent)

    def build_room_cards(self):
        rooms_view.build_room_cards(self)

    def open_status_menu(self, event, room_id: int):
        rooms_view.open_status_menu(self, event, room_id)

    def open_reservation_for_room(self, room_id: int, modal=None):
        rooms_view.open_reservation_for_room(self, room_id, modal)

    # ============================================================
    # ODA TIPLERI
    # ============================================================
    def create_room_types_frame(self, parent):
        return room_types_view.create_room_types_frame(self, parent)

    def build_room_type_list(self):
        room_types_view.build_room_type_list(self)

    def populate_room_type_form(self, rt_id):
        room_types_view.populate_room_type_form(self, rt_id)

    def on_room_type_select(self, event):
        room_types_view.on_room_type_select(self, event)

    def save_room_type(self):
        room_types_view.save_room_type(self)

    def delete_room_type(self):
        room_types_view.delete_room_type(self)

    # ============================================================
    # MISAFIR YONETIMI
    # ============================================================
    def create_guests_frame(self, parent):
        return guests_view.create_guests_frame(self, parent)

    def build_guest_list(self):
        guests_view.build_guest_list(self)

    def populate_guest_form(self, guest_id):
        guests_view.populate_guest_form(self, guest_id)

    def on_guest_select(self, event):
        guests_view.on_guest_select(self, event)

    def save_guest(self):
        guests_view.save_guest(self)

    def delete_guest(self, guest_id: int):
        guests_view.delete_guest(self, guest_id)

    # ============================================================
    # REZERVASYON YONETIMI
    # ============================================================
    def create_reservations_frame(self, parent):
        return reservations_view.create_reservations_frame(self, parent)

    def refresh_reservation_choices(self):
        reservations_view.refresh_reservation_choices(self)

    def on_room_change(self, selected_label: str):
        reservations_view.on_room_change(self, selected_label)

    def build_reservations_list(self):
        reservations_view.build_reservations_list(self)

    def save_reservation(self):
        reservations_view.save_reservation(self)

    def cancel_reservation(self, reservation_id: int):
        reservations_view.cancel_reservation(self, reservation_id)

    # ============================================================
    # ORTAK YARDIMCI / GORUNUM GECISLERI
    # ============================================================
    def _create_nav_button(self, parent, label: str, command):
        btn = ctk.CTkButton(
            parent,
            text=label,
            width=160,
            height=40,
            corner_radius=12,
            fg_color="transparent",
            hover_color=self.color_sidebar_dark,
            text_color="#e5e7eb",
            font=self.font_sidebar,
            command=command
        )
        btn.pack(fill="x", padx=16, pady=8)
        if not hasattr(self, "nav_buttons"):
            self.nav_buttons = []
        self.nav_buttons.append({"btn": btn, "label": label})
        return btn

    def set_active_nav(self, active_btn):
        self.active_nav_btn = active_btn
        for info in getattr(self, "nav_buttons", []):
            btn = info["btn"]
            if btn is active_btn:
                btn.configure(
                    text=info["label"],
                    fg_color=self.color_sidebar_light,
                    text_color="#0b1724",
                    hover_color=self.color_sidebar_light
                )
            else:
                btn.configure(
                    text=info["label"],
                    fg_color="transparent",
                    text_color="#e5e7eb",
                    hover_color=self.color_sidebar_dark
                )

    def get_room_type_color(self, room_type: str) -> str:
        rt = (room_type or "").upper()
        if "KRAL" in rt:
            return "#fef3c7"
        elif "KING" in rt:
            return "#fde2e4"
        elif "DELUXE" in rt:
            return "#dbeafe"
        elif "STANDART" in rt:
            return "#dcfce7"
        else:
            return "#e5e7eb"

    def get_status_text(self, status: str) -> str:
        s = (status or "").upper()
        if s in ("CLEAN", "AVAILABLE"):
            return "MUSAIT"
        elif s in ("OCCUPIED", "FULL"):
            return "DOLU"
        elif s in ("DIRTY", "NEEDS_CLEANING"):
            return "TEMIZLIK GEREKIYOR"
        elif s in ("MAINTENANCE", "OUT_OF_ORDER"):
            return "BAKIMDA"
        else:
            return s or "BILINMIYOR"

    def show_dashboard(self):
        self.rooms_frame.pack_forget()
        self.room_types_frame.pack_forget()
        self.guests_frame.pack_forget()
        self.reservations_frame.pack_forget()
        self.dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.set_active_nav(self.btn_dashboard)
        self.refresh_dashboard()

    def show_rooms_view(self):
        self.dashboard_frame.pack_forget()
        self.room_types_frame.pack_forget()
        self.guests_frame.pack_forget()
        self.reservations_frame.pack_forget()
        self.rooms_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.set_active_nav(self.btn_rooms)
        self.build_room_cards()

    def show_room_types_view(self):
        self.dashboard_frame.pack_forget()
        self.rooms_frame.pack_forget()
        self.guests_frame.pack_forget()
        self.reservations_frame.pack_forget()
        self.room_types_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.set_active_nav(self.btn_room_types)
        self.build_room_type_list()

    def show_guests_view(self):
        self.dashboard_frame.pack_forget()
        self.rooms_frame.pack_forget()
        self.room_types_frame.pack_forget()
        self.reservations_frame.pack_forget()
        self.guests_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.set_active_nav(self.btn_guests)
        self.build_guest_list()

    def show_reservations_view(self):
        self.dashboard_frame.pack_forget()
        self.rooms_frame.pack_forget()
        self.room_types_frame.pack_forget()
        self.guests_frame.pack_forget()
        self.reservations_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.set_active_nav(self.btn_reservations)
        self.build_reservations_list()
        self.refresh_reservation_choices()


if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as exc:
        import traceback
        print("Uygulama hatası:\n", traceback.format_exc())
        try:
            import tkinter.messagebox as mb
            mb.showerror("Hata", f"Uygulama kapandı:\n{exc}")
        except Exception:
            pass

