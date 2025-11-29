# ui_main.py
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as mb
from datetime import date, datetime
from backend.services import hotel_service as db
from frontend import theme
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
        frame = ctk.CTkFrame(parent, corner_radius=24, fg_color=self.color_card)

        title = ctk.CTkLabel(
            frame,
            text="Dashboard",
            font=self.font_title,
            text_color=self.color_text_main
        )
        title.pack(pady=(15, 4), anchor="w", padx=25)

        subtitle = ctk.CTkLabel(
            frame,
            text="Otelin genel durumunu buradan gorebilirsiniz.",
            font=self.font_subtitle,
            text_color="#475569"
        )
        subtitle.pack(pady=(0, 12), anchor="w", padx=25)

        cards_frame = ctk.CTkFrame(frame, fg_color=self.color_panel, corner_radius=16)
        cards_frame.pack(fill="x", padx=20, pady=(5, 10))

        self.lbl_stat_total_rooms = self._create_stat_card(cards_frame, 0, "Toplam Oda", "0")
        self.lbl_stat_month_res = self._create_stat_card(cards_frame, 1, "Bu Ayki Rezervasyon", "0")
        self.lbl_stat_active_guests = self._create_stat_card(cards_frame, 2, "Aktif Misafir", "0")
        self.lbl_stat_occupancy = self._create_stat_card(cards_frame, 3, "Doluluk Orani", "%0")

        chart_container = ctk.CTkFrame(frame, fg_color=self.color_panel, corner_radius=16)
        chart_container.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        chart_title = ctk.CTkLabel(
            chart_container,
            text="Yillik Rezervasyon Analizi",
            font=("Poppins", 14, "bold"),
            text_color="#111827"
        )
        chart_title.pack(anchor="w", padx=15, pady=(10, 0))

        self.dashboard_chart_canvas = tk.Canvas(
            chart_container,
            bg=self.color_panel,
            highlightthickness=0
        )
        self.dashboard_chart_canvas.pack(fill="both", expand=True, padx=15, pady=10)

        return frame

    def _create_stat_card(self, parent, col, title, value):
        card = ctk.CTkFrame(parent, fg_color=self.color_card, corner_radius=16)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        lbl_title = ctk.CTkLabel(
            card,
            text=title,
            font=self.font_subtitle,
            text_color="#475569"
        )
        lbl_title.pack(anchor="w", padx=12, pady=(10, 0))

        lbl_value = ctk.CTkLabel(
            card,
            text=value,
            font=("Poppins", 20, "bold"),
            text_color=self.color_text_main
        )
        lbl_value.pack(anchor="w", padx=12, pady=(4, 12))

        return lbl_value

    def refresh_dashboard(self):
        total_rooms, res_this_month, active_guests, occ_rate = db.get_dashboard_stats()

        self.lbl_stat_total_rooms.configure(text=str(total_rooms))
        self.lbl_stat_month_res.configure(text=str(res_this_month))
        self.lbl_stat_active_guests.configure(text=str(active_guests))
        self.lbl_stat_occupancy.configure(text=f"%{int(occ_rate * 100)}")

        data = db.get_yearly_reservation_stats()
        month_to_count = {m: c for (m, c) in data}

        canvas = self.dashboard_chart_canvas
        canvas.delete("all")

        width = canvas.winfo_width() or 800
        height = canvas.winfo_height() or 260
        margin = 40
        max_count = max(month_to_count.values()) if month_to_count else 1
        bar_width = (width - 2 * margin) / 12

        for i in range(12):
            month = i + 1
            x0 = margin + i * bar_width + 5
            x1 = margin + (i + 1) * bar_width - 5
            count = month_to_count.get(month, 0)
            bar_height = (height - 2 * margin) * (count / max_count) if max_count > 0 else 0
            y1 = height - margin
            y0 = y1 - bar_height
            canvas.create_rectangle(x0, y0, x1, y1, fill="#93c5fd", width=0)
            canvas.create_text((x0 + x1) / 2, height - margin + 12, text=str(month),
                               fill="#374151", font=("Poppins", 9))
        canvas.create_text(margin - 20, margin, text=str(max_count),
                           fill="#374151", font=("Poppins", 9))
        canvas.create_text(margin - 20, height - margin, text="0",
                           fill="#374151", font=("Poppins", 9))

    # ============================================================
    # ODA YONETIMI
    # ============================================================
    def create_rooms_frame(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=24, fg_color=self.color_card)

        title = ctk.CTkLabel(
            frame,
            text="Oda Yonetimi",
            font=self.font_title,
            text_color="#111827"
        )
        title.pack(pady=(15, 4), anchor="w", padx=25)

        subtitle = ctk.CTkLabel(
            frame,
            text="Oda durumlarini buradan takip edebilir, hizlica guncelleyebilirsiniz.",
            font=self.font_subtitle,
            text_color="#6b7280"
        )
        subtitle.pack(pady=(0, 12), anchor="w", padx=25)

        self.rooms_scroll = ctk.CTkScrollableFrame(
            frame,
            corner_radius=24,
            width=900,
            height=520,
            fg_color=self.color_panel
        )
        self.rooms_scroll.pack(fill="both", expand=True, padx=20, pady=10)

        self.build_room_cards()
        return frame

    def build_room_cards(self):
        for child in self.rooms_scroll.winfo_children():
            child.destroy()

        rooms = db.get_all_rooms()
        if not rooms:
            empty_label = ctk.CTkLabel(
                self.rooms_scroll,
                text="Hic oda bulunamadi.",
                font=self.font_normal,
                text_color="#111827"
            )
            empty_label.pack(pady=20)
            return

        floors = {}
        for r in rooms:
            room_id, room_no, room_type, floor, status = r
            floors.setdefault(floor, []).append(r)

        for floor in sorted(floors.keys()):
            floor_label = ctk.CTkLabel(
                self.rooms_scroll,
                text=f"{floor}. KAT",
                font=self.font_floor,
                text_color="#111827"
            )
            floor_label.pack(anchor="w", padx=18, pady=(18, 6))

            floor_frame = ctk.CTkFrame(self.rooms_scroll, fg_color="transparent")
            floor_frame.pack(fill="x", padx=10, pady=(0, 8))

            for idx, r in enumerate(floors[floor]):
                room_id, room_no, room_type, f, status = r
                bg_color = self.get_room_type_color(room_type)
                status_text = self.get_status_text(status)

                def bind_card_click(widget, rid=room_id):
                    widget.bind("<Button-1>", lambda e, rid=rid: self.open_status_menu(e, rid))

                card = ctk.CTkFrame(
                    floor_frame,
                    width=220,
                    height=130,
                    corner_radius=24,
                    fg_color=bg_color
                )
                card.grid(row=0, column=idx, padx=10, pady=5, sticky="nsew")
                bind_card_click(card)

                type_label = ctk.CTkLabel(
                    card,
                    text=room_type.upper(),
                    font=self.font_card_type,
                    text_color="#111827"
                )
                type_label.pack(anchor="w", padx=15, pady=(10, 0))
                bind_card_click(type_label)

                number_label = ctk.CTkLabel(
                    card,
                    text=f"#{room_no}",
                    font=self.font_card_number,
                    text_color="#111827"
                )
                number_label.pack(anchor="w", padx=15, pady=(2, 0))
                bind_card_click(number_label)

                status_badge = ctk.CTkLabel(
                    card,
                    text=status_text,
                    font=self.font_badge,
                    corner_radius=999,
                    fg_color="white",
                    text_color="#111827",
                    padx=10,
                    pady=4
                )
                status_badge.pack(anchor="w", padx=15, pady=(4, 0))
                bind_card_click(status_badge)

                btn_res = ctk.CTkButton(
                    card,
                    text="Rezervasyon",
                    font=("Poppins", 11),
                    fg_color="#60a5fa",
                    hover_color="#3b82f6",
                    text_color="#0b1120",
                    height=26,
                    command=lambda rid=room_id: self.open_reservation_for_room(rid)
                )
                btn_res.pack(anchor="w", padx=15, pady=(6, 6))

    def open_status_menu(self, event, room_id: int):
        # Eski popup'u kapat
        if self.status_popup is not None:
            try:
                self.status_popup.destroy()
            except Exception:
                pass
            self.status_popup = None

        # Modal pencere (oda ayrıntı)
        modal = tk.Toplevel(self)
        modal.grab_set()
        modal.title("Oda Ayrıntı")
        modal.geometry("360x420+{}+{}".format(event.x_root, event.y_root))
        modal.configure(bg="#000000")
        modal.wm_attributes("-topmost", True)

        card = ctk.CTkFrame(modal, corner_radius=16, fg_color="white")
        card.pack(fill="both", expand=True, padx=10, pady=10)

        # Oda bilgisi
        try:
            # oda detayini tekrar cek
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT r.id, r.room_number, rt.name, r.status
                FROM rooms r
                JOIN room_types rt ON r.room_type_id = rt.id
                WHERE r.id = %s
            """, (room_id,))
            row = cur.fetchone()
            if row:
                _, room_no, room_type, status = row
        except Exception:
            room_no = "?"
            room_type = ""
            status = "UNKNOWN"
        finally:
            try:
                if conn:
                    conn.close()
            except Exception:
                pass

        status_text = self.get_status_text(status)
        status_color = "#22c55e" if status_text == "MUSAIT" else "#f59e0b" if status_text == "TEMIZLIK GEREKIYOR" else "#ef4444" if status_text == "DOLU" else "#d1d5db"

        header = ctk.CTkFrame(card, fg_color="#22c55e" if status_text == "MUSAIT" else "#f59e0b" if status_text == "TEMIZLIK GEREKIYOR" else "#ef4444" if status_text == "DOLU" else "#38bdf8", corner_radius=12)
        header.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkLabel(header, text=str(room_type).upper(), font=("Poppins", 14, "bold"), text_color="white").pack(pady=(8, 0))
        ctk.CTkLabel(header, text=f"#{room_no}", font=("Poppins", 26, "bold"), text_color="white").pack(pady=(4, 8))
        status_badge = ctk.CTkLabel(header, text=status_text, font=("Poppins", 12, "bold"),
                                    fg_color="white", text_color="#0f172a", corner_radius=20, padx=12, pady=4)
        status_badge.pack(pady=(0, 12))

        btn_res = ctk.CTkButton(
            card,
            text="Yeni Rezervasyon Ekle",
            font=("Poppins", 13, "bold"),
            fg_color="#1e90ff",
            hover_color="#1878d6",
            text_color="white",
            height=36,
            command=lambda rid=room_id: self.open_reservation_for_room(rid, modal)
        )
        btn_res.pack(pady=(8, 4), padx=16, fill="x")

        # Hızlı durum değiştir
        ctk.CTkLabel(card, text="HIZLI DURUM DEGISTIR", font=("Poppins", 12),
                     text_color="#6b7280").pack(pady=(12, 4))
        btn_container = ctk.CTkFrame(card, fg_color="transparent")
        btn_container.pack(pady=(0, 12))

        def set_status(new_status):
            ok = db.update_room_status(room_id, new_status)
            if ok:
                self.build_room_cards()
                self.refresh_reservation_choices()
                modal.destroy()

        btn_clean = ctk.CTkButton(btn_container, text="TEMIZ", width=80, fg_color="transparent",
                                  border_width=2, border_color="#22c55e", text_color="#22c55e",
                                  hover_color="#e6f8ee", command=lambda: set_status("CLEAN"))
        btn_clean.grid(row=0, column=0, padx=6, pady=6)
        btn_dirty = ctk.CTkButton(btn_container, text="KIRLI", width=80, fg_color="transparent",
                                  border_width=2, border_color="#f59e0b", text_color="#f59e0b",
                                  hover_color="#fff4e5", command=lambda: set_status("DIRTY"))
        btn_dirty.grid(row=0, column=1, padx=6, pady=6)
        btn_maint = ctk.CTkButton(btn_container, text="BAKIM", width=80, fg_color="transparent",
                                  border_width=2, border_color="#ef4444", text_color="#ef4444",
                                  hover_color="#ffecec", command=lambda: set_status("MAINTENANCE"))
        btn_maint.grid(row=0, column=2, padx=6, pady=6)

        self.status_popup = modal

    def open_reservation_for_room(self, room_id: int, modal_to_close=None):
        self.show_reservations_view()
        self.refresh_reservation_choices()
        for label, rid in self.room_choice_map.items():
            if rid == room_id:
                self.combo_res_room.set(label)
                break
        self.label_res_message.configure(
            text=f"Oda icin rezervasyon olusturuyorsunuz (ID={room_id}).",
            text_color="#6b7280"
        )
        if modal_to_close:
            try:
                modal_to_close.destroy()
            except Exception:
                pass

    # ============================================================
    # ODA TIPLERI YONETIMI
    # ============================================================
    def create_room_types_frame(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=24, fg_color=self.color_card)

        title = ctk.CTkLabel(
            frame,
            text="Oda Tipleri",
            font=self.font_title,
            text_color="#111827"
        )
        title.pack(pady=(15, 4), anchor="w", padx=25)

        subtitle = ctk.CTkLabel(
            frame,
            text="Oda tiplerinin adini, aciklamasini, taban fiyatini ve kapasitesini yonetebilirsiniz.",
            font=self.font_subtitle,
            text_color="#6b7280"
        )
        subtitle.pack(pady=(0, 12), anchor="w", padx=25)

        form_frame = ctk.CTkFrame(frame, corner_radius=16, fg_color=self.color_panel)
        form_frame.pack(fill="x", padx=20, pady=(5, 10))

        lbl_name = ctk.CTkLabel(form_frame, text="Tip Adi:", font=self.font_normal, text_color="#111827")
        lbl_name.grid(row=0, column=0, padx=15, pady=4, sticky="e")

        self.entry_rt_name = ctk.CTkEntry(form_frame, width=180, font=self.font_normal, placeholder_text="Standart Oda")
        self.entry_rt_name.grid(row=0, column=1, padx=15, pady=4, sticky="w")

        lbl_desc = ctk.CTkLabel(form_frame, text="Aciklama:", font=self.font_normal, text_color="#111827")
        lbl_desc.grid(row=1, column=0, padx=15, pady=4, sticky="e")

        self.entry_rt_desc = ctk.CTkEntry(form_frame, width=280, font=self.font_normal, placeholder_text="Kisa aciklama")
        self.entry_rt_desc.grid(row=1, column=1, columnspan=2, padx=15, pady=4, sticky="w")

        lbl_price = ctk.CTkLabel(form_frame, text="Taban Fiyat:", font=self.font_normal, text_color="#111827")
        lbl_price.grid(row=0, column=2, padx=15, pady=4, sticky="e")

        self.entry_rt_price = ctk.CTkEntry(form_frame, width=120, font=self.font_normal, placeholder_text="1500")
        self.entry_rt_price.grid(row=0, column=3, padx=15, pady=4, sticky="w")

        lbl_cap = ctk.CTkLabel(form_frame, text="Kapasite:", font=self.font_normal, text_color="#111827")
        lbl_cap.grid(row=0, column=4, padx=15, pady=4, sticky="e")

        self.entry_rt_capacity = ctk.CTkEntry(form_frame, width=80, font=self.font_normal, placeholder_text="2")
        self.entry_rt_capacity.grid(row=0, column=5, padx=15, pady=4, sticky="w")

        self.label_rt_message = ctk.CTkLabel(form_frame, text="", font=("Poppins", 11), text_color="#dc2626")
        self.label_rt_message.grid(row=2, column=0, columnspan=4, padx=15, pady=(4, 4), sticky="w")

        self.btn_rt_save = ctk.CTkButton(
            form_frame, text="Ekle", font=self.font_normal,
            fg_color="#4ade80", hover_color="#22c55e", text_color="#064e3b",
            command=self.save_room_type
        )
        self.btn_rt_save.grid(row=1, column=4, padx=15, pady=8, sticky="e")

        self.btn_rt_delete = ctk.CTkButton(
            form_frame, text="Sil", font=self.font_normal,
            fg_color="#fecaca", hover_color="#fca5a5", text_color="#b91c1c",
            command=self.delete_room_type
        )
        self.btn_rt_delete.grid(row=1, column=5, padx=15, pady=8, sticky="e")

        self.room_types_scroll = ctk.CTkScrollableFrame(
            frame, corner_radius=24, width=900, height=400, fg_color=self.color_panel
        )
        self.room_types_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        self.build_room_type_list()
        return frame

    def build_room_type_list(self):
        for child in self.room_types_scroll.winfo_children():
            child.destroy()

        room_types = db.get_all_room_types()
        if not room_types:
            lbl = ctk.CTkLabel(
                self.room_types_scroll,
                text="Tanimli oda tipi yok.",
                font=self.font_normal,
                text_color="#111827"
            )
            lbl.pack(pady=20)
            return

        header = ctk.CTkFrame(self.room_types_scroll, fg_color="#e5e7eb", corner_radius=12)
        header.pack(fill="x", padx=10, pady=(8, 4))

        cols = ["ID", "Ad", "Aciklama", "Taban Fiyat", "Kapasite", ""]
        widths = [40, 160, 260, 100, 80, 80]

        for i, (col, w) in enumerate(zip(cols, widths)):
            lbl = ctk.CTkLabel(
                header,
                text=col,
                font=("Poppins", 11, "bold"),
                text_color="#111827",
                width=w,
                anchor="w"
            )
            lbl.grid(row=0, column=i, padx=8, pady=6, sticky="w")

        for rt in room_types:
            rt_id, name, desc, price, cap = rt
            row = ctk.CTkFrame(self.room_types_scroll, fg_color=self.color_card, corner_radius=12)
            row.pack(fill="x", padx=10, pady=3)

            values = [
                str(rt_id),
                name or "-",
                desc or "-",
                f"{price:.2f}" if price is not None else "-",
                str(cap) if cap is not None else "-"
            ]

            for i, (val, w) in enumerate(zip(values, widths[:-1])):
                lbl = ctk.CTkLabel(
                    row,
                    text=val,
                    font=self.font_normal,
                    text_color="#111827",
                    width=w,
                    anchor="w"
                )
                lbl.grid(row=0, column=i, padx=8, pady=6, sticky="w")

            btn_edit = ctk.CTkButton(
                row,
                text="Duzenle",
                width=widths[-1],
                font=("Poppins", 11),
                fg_color="#e5e7eb",
                hover_color="#d1d5db",
                text_color="#111827",
                command=lambda rid=rt_id, n=name, d=desc, p=price, c=cap:
                    self.load_room_type_into_form(rid, n, d, p, c)
            )
            btn_edit.grid(row=0, column=len(values), padx=8, pady=6, sticky="e")

    def load_room_type_into_form(self, rt_id, name, desc, price, cap):
        self.selected_room_type_id = rt_id
        self.entry_rt_name.delete(0, "end")
        self.entry_rt_name.insert(0, name or "")
        self.entry_rt_desc.delete(0, "end")
        self.entry_rt_desc.insert(0, desc or "")
        self.entry_rt_price.delete(0, "end")
        if price is not None:
            self.entry_rt_price.insert(0, str(price))
        self.entry_rt_capacity.delete(0, "end")
        if cap is not None:
            self.entry_rt_capacity.insert(0, str(cap))
        self.label_rt_message.configure(
            text=f"🔁 Oda tipi duzenleniyor (ID={rt_id}).",
            text_color="#6b7280"
        )
        self.btn_rt_save.configure(text="Guncelle")

    def save_room_type(self):
        name = self.entry_rt_name.get().strip()
        desc = self.entry_rt_desc.get().strip() or None
        price_str = self.entry_rt_price.get().strip()
        cap_str = self.entry_rt_capacity.get().strip()

        if not name:
            self.label_rt_message.configure(text="Tip adi zorunludur.", text_color="#dc2626")
            return

        try:
            price = float(price_str)
            cap = int(cap_str)
        except ValueError:
            self.label_rt_message.configure(text="Fiyat ve kapasite sayisal olmalidir.", text_color="#dc2626")
            return

        if self.selected_room_type_id is None:
            new_id = db.insert_room_type(name, desc, price, cap)
            if new_id is not None:
                self.label_rt_message.configure(
                    text=f"✅ Oda tipi eklendi (ID={new_id}).",
                    text_color="#16a34a"
                )
        else:
            ok = db.update_room_type(self.selected_room_type_id, name, desc, price, cap)
            if ok:
                self.label_rt_message.configure(
                    text=f"✅ Oda tipi guncellendi (ID={self.selected_room_type_id}).",
                    text_color="#16a34a"
                )

        self.selected_room_type_id = None
        self.btn_rt_save.configure(text="Ekle")
        self.entry_rt_name.delete(0, "end")
        self.entry_rt_desc.delete(0, "end")
        self.entry_rt_price.delete(0, "end")
        self.entry_rt_capacity.delete(0, "end")

        self.build_room_type_list()
        self.build_room_cards()

    def delete_room_type(self):
        if self.selected_room_type_id is None:
            self.label_rt_message.configure(
                text="Silmek icin once listeden bir oda tipi secin.",
                text_color="#dc2626"
            )
            return

        ok = db.delete_room_type(self.selected_room_type_id)
        if ok:
            self.label_rt_message.configure(
                text=f"✅ Oda tipi silindi (ID={self.selected_room_type_id}).",
                text_color="#16a34a"
            )
            self.selected_room_type_id = None
            self.btn_rt_save.configure(text="Ekle")
            self.entry_rt_name.delete(0, "end")
            self.entry_rt_desc.delete(0, "end")
            self.entry_rt_price.delete(0, "end")
            self.entry_rt_capacity.delete(0, "end")
            self.build_room_type_list()
            self.build_room_cards()

    # ============================================================
    # MISAFIR YONETIMI
    # ============================================================
    def create_guests_frame(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=24, fg_color=self.color_card)

        title = ctk.CTkLabel(frame, text="Misafir Yonetimi", font=self.font_title, text_color="#111827")
        title.pack(pady=(15, 4), anchor="w", padx=25)

        subtitle = ctk.CTkLabel(
            frame,
            text="Yeni misafir ekleyebilir, duzenleyebilir veya silebilirsiniz.",
            font=self.font_subtitle,
            text_color="#6b7280"
        )
        subtitle.pack(pady=(0, 12), anchor="w", padx=25)

        form_frame = ctk.CTkFrame(frame, corner_radius=16, fg_color=self.color_panel)
        form_frame.pack(fill="x", padx=20, pady=(5, 10))

        form_title = ctk.CTkLabel(
            form_frame,
            text="Yeni Misafir Ekle / Guncelle",
            font=("Poppins", 14, "bold"),
            text_color="#111827"
        )
        form_title.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        label_first = ctk.CTkLabel(form_frame, text="Ad:", font=self.font_normal, text_color="#111827")
        label_first.grid(row=1, column=0, padx=15, pady=4, sticky="e")
        self.entry_guest_first_name = ctk.CTkEntry(form_frame, width=180, font=self.font_normal, placeholder_text="Ad")
        self.entry_guest_first_name.grid(row=1, column=1, padx=15, pady=4, sticky="w")

        label_last = ctk.CTkLabel(form_frame, text="Soyad:", font=self.font_normal, text_color="#111827")
        label_last.grid(row=2, column=0, padx=15, pady=4, sticky="e")
        self.entry_guest_last_name = ctk.CTkEntry(form_frame, width=180, font=self.font_normal, placeholder_text="Soyad")
        self.entry_guest_last_name.grid(row=2, column=1, padx=15, pady=4, sticky="w")

        label_email = ctk.CTkLabel(form_frame, text="E-posta:", font=self.font_normal, text_color="#111827")
        label_email.grid(row=1, column=2, padx=15, pady=4, sticky="e")
        self.entry_guest_email = ctk.CTkEntry(form_frame, width=200, font=self.font_normal, placeholder_text="ornek@mail.com")
        self.entry_guest_email.grid(row=1, column=3, padx=15, pady=4, sticky="w")

        label_phone = ctk.CTkLabel(form_frame, text="Telefon:", font=self.font_normal, text_color="#111827")
        label_phone.grid(row=2, column=2, padx=15, pady=4, sticky="e")
        self.entry_guest_phone = ctk.CTkEntry(form_frame, width=200, font=self.font_normal, placeholder_text="+90...")
        self.entry_guest_phone.grid(row=2, column=3, padx=15, pady=4, sticky="w")

        label_tc = ctk.CTkLabel(form_frame, text="T.C. Kimlik No:", font=self.font_normal, text_color="#111827")
        label_tc.grid(row=3, column=0, padx=15, pady=4, sticky="e")
        self.entry_guest_tc = ctk.CTkEntry(form_frame, width=180, font=self.font_normal, placeholder_text="11 haneli")
        self.entry_guest_tc.grid(row=3, column=1, padx=15, pady=4, sticky="w")

        self.label_guest_message = ctk.CTkLabel(form_frame, text="", font=("Poppins", 11), text_color="#dc2626")
        self.label_guest_message.grid(row=4, column=0, columnspan=4, padx=15, pady=(4, 4), sticky="w")

        self.btn_save_guest = ctk.CTkButton(
            form_frame,
            text="Kaydet",
            font=self.font_normal,
            fg_color="#4ade80",
            hover_color="#22c55e",
            text_color="#064e3b",
            command=self.save_guest
        )
        self.btn_save_guest.grid(row=3, column=3, padx=15, pady=8, sticky="e")

        self.guests_scroll = ctk.CTkScrollableFrame(
            frame,
            corner_radius=24,
            width=900,
            height=350,
            fg_color=self.color_panel
        )
        self.guests_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        self.build_guest_list()
        return frame

    def build_guest_list(self):
        for child in self.guests_scroll.winfo_children():
            child.destroy()

        guests = db.get_all_guests()
        if not guests:
            empty_label = ctk.CTkLabel(
                self.guests_scroll,
                text="Henuz misafir kaydi yok.",
                font=self.font_normal,
                text_color="#111827"
            )
            empty_label.pack(pady=20)
            return

        header_frame = ctk.CTkFrame(self.guests_scroll, fg_color="#e5e7eb", corner_radius=12)
        header_frame.pack(fill="x", padx=10, pady=(8, 4))

        cols = ["ID", "Ad Soyad", "Telefon", "E-posta", "T.C. No", ""]
        widths = [40, 220, 140, 220, 120, 120]

        for i, (col, w) in enumerate(zip(cols, widths)):
            lbl = ctk.CTkLabel(
                header_frame,
                text=col,
                font=("Poppins", 11, "bold"),
                text_color="#111827",
                width=w,
                anchor="w"
            )
            lbl.grid(row=0, column=i, padx=8, pady=6, sticky="w")

        for g in guests:
            guest_id, first_name, last_name, email, phone, tc_no, is_blacklisted = g
            row_frame = ctk.CTkFrame(self.guests_scroll, fg_color=self.color_card, corner_radius=12)
            row_frame.pack(fill="x", padx=10, pady=3)

            full_name = f"{first_name} {last_name}"
            values = [str(guest_id), full_name, phone or "-", email or "-", tc_no or "-"]

            for i, (val, w) in enumerate(zip(values, widths[:-1])):
                lbl = ctk.CTkLabel(
                    row_frame,
                    text=val,
                    font=self.font_normal,
                    text_color="#111827",
                    width=w,
                    anchor="w"
                )
                lbl.grid(row=0, column=i, padx=8, pady=6, sticky="w")

            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=len(values), padx=8, pady=6, sticky="e")

            btn_edit = ctk.CTkButton(
                action_frame,
                text="Duzenle",
                width=60,
                font=("Poppins", 10),
                fg_color="#e5e7eb",
                hover_color="#d1d5db",
                text_color="#111827",
                command=lambda gid=guest_id, fn=first_name, ln=last_name, em=email, ph=phone, tc=tc_no:
                    self.load_guest_into_form(gid, fn, ln, em, ph, tc)
            )
            btn_edit.pack(side="left", padx=2)

            btn_del = ctk.CTkButton(
                action_frame,
                text="Sil",
                width=40,
                font=("Poppins", 10),
                fg_color="#fecaca",
                hover_color="#fca5a5",
                text_color="#b91c1c",
                command=lambda gid=guest_id: self.delete_guest(gid)
            )
            btn_del.pack(side="left", padx=2)

    def load_guest_into_form(self, guest_id, first_name, last_name, email, phone, tc_no):
        self.selected_guest_id = guest_id
        self.entry_guest_first_name.delete(0, "end")
        self.entry_guest_first_name.insert(0, first_name or "")
        self.entry_guest_last_name.delete(0, "end")
        self.entry_guest_last_name.insert(0, last_name or "")
        self.entry_guest_email.delete(0, "end")
        self.entry_guest_email.insert(0, email or "")
        self.entry_guest_phone.delete(0, "end")
        self.entry_guest_phone.insert(0, phone or "")
        self.entry_guest_tc.delete(0, "end")
        self.entry_guest_tc.insert(0, tc_no or "")
        self.label_guest_message.configure(
            text=f"🔁 ID {guest_id} misafirini duzenliyorsunuz.",
            text_color="#6b7280"
        )
        self.btn_save_guest.configure(text="Guncelle")

    def save_guest(self):
        first_name = self.entry_guest_first_name.get().strip()
        last_name = self.entry_guest_last_name.get().strip()
        email = self.entry_guest_email.get().strip() or None
        phone = self.entry_guest_phone.get().strip() or None
        tc_no = self.entry_guest_tc.get().strip() or None

        if not first_name or not last_name:
            self.label_guest_message.configure(text="Ad ve Soyad zorunludur.", text_color="#dc2626")
            return

        if self.selected_guest_id is not None:
            ok = db.update_guest(self.selected_guest_id, first_name, last_name, email, phone, tc_no)
            if ok:
                self.label_guest_message.configure(
                    text=f"✅ Misafir basariyla guncellendi (ID: {self.selected_guest_id})",
                    text_color="#16a34a"
                )
                self.selected_guest_id = None
                self.btn_save_guest.configure(text="Kaydet")
                self.entry_guest_first_name.delete(0, "end")
                self.entry_guest_last_name.delete(0, "end")
                self.entry_guest_email.delete(0, "end")
                self.entry_guest_phone.delete(0, "end")
                self.entry_guest_tc.delete(0, "end")
                self.build_guest_list()
                self.refresh_reservation_choices()
            else:
                self.label_guest_message.configure(
                    text="❌ Misafir guncellenirken hata olustu.",
                    text_color="#dc2626"
                )
            return

        new_id = db.insert_guest(first_name, last_name, email, phone, tc_no)
        if new_id is not None:
            self.label_guest_message.configure(
                text=f"✅ Misafir basariyla eklendi (ID: {new_id})",
                text_color="#16a34a"
            )
            self.entry_guest_first_name.delete(0, "end")
            self.entry_guest_last_name.delete(0, "end")
            self.entry_guest_email.delete(0, "end")
            self.entry_guest_phone.delete(0, "end")
            self.entry_guest_tc.delete(0, "end")
            self.build_guest_list()
            self.refresh_reservation_choices()
        else:
            self.label_guest_message.configure(
                text="❌ Misafir eklenirken bir hata olustu.",
                text_color="#dc2626"
            )

    def delete_guest(self, guest_id: int):
        ok = db.delete_guest(guest_id)
        if ok:
            self.label_guest_message.configure(
                text=f"✅ Misafir silindi (ID: {guest_id}).",
                text_color="#16a34a"
            )
            self.build_guest_list()
            self.refresh_reservation_choices()
        else:
            self.label_guest_message.configure(
                text="❌ Misafir silinemedi. (Muhtemelen aktif rezervasyonu var.)",
                text_color="#dc2626"
            )

    # ============================================================
    # REZERVASYON YONETIMI
    # ============================================================
    def create_reservations_frame(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=24, fg_color=self.color_card)

        title = ctk.CTkLabel(frame, text="Rezervasyon Yonetimi", font=self.font_title, text_color="#111827")
        title.pack(pady=(15, 4), anchor="w", padx=25)

        subtitle = ctk.CTkLabel(
            frame,
            text="Misafir ve oda secerek yeni rezervasyon olusturabilirsiniz.",
            font=self.font_subtitle,
            text_color="#6b7280"
        )
        subtitle.pack(pady=(0, 12), anchor="w", padx=25)

        form_frame = ctk.CTkFrame(frame, corner_radius=16, fg_color=self.color_panel)
        form_frame.pack(fill="x", padx=20, pady=(5, 10))

        lbl_guest = ctk.CTkLabel(form_frame, text="Misafir:", font=self.font_normal, text_color="#111827")
        lbl_guest.grid(row=0, column=0, padx=15, pady=4, sticky="e")

        self.combo_res_guest = ctk.CTkComboBox(form_frame, width=220, font=self.font_normal, values=[], state="readonly")
        self.combo_res_guest.grid(row=0, column=1, padx=15, pady=4, sticky="w")

        lbl_room = ctk.CTkLabel(form_frame, text="Oda:", font=self.font_normal, text_color="#111827")
        lbl_room.grid(row=1, column=0, padx=15, pady=4, sticky="e")

        self.combo_res_room = ctk.CTkComboBox(
            form_frame, width=220, font=self.font_normal, values=[], state="readonly", command=self.on_room_change
        )
        self.combo_res_room.grid(row=1, column=1, padx=15, pady=4, sticky="w")

        lbl_ci = ctk.CTkLabel(form_frame, text="Giris Tarihi:", font=self.font_normal, text_color="#111827")
        lbl_ci.grid(row=0, column=2, padx=(25, 5), pady=4, sticky="e")

        current_year = datetime.now().year
        years = [str(y) for y in range(current_year, current_year + 6)]
        months = [f"{m:02d}" for m in range(1, 13)]
        days = [f"{d:02d}" for d in range(1, 32)]

        self.cb_ci_year = ctk.CTkComboBox(form_frame, width=70, values=years, state="readonly", font=self.font_normal)
        self.cb_ci_year.grid(row=0, column=3, padx=2, pady=4)
        self.cb_ci_year.set(str(datetime.now().year))

        self.cb_ci_month = ctk.CTkComboBox(form_frame, width=60, values=months, state="readonly", font=self.font_normal)
        self.cb_ci_month.grid(row=0, column=4, padx=2, pady=4)
        self.cb_ci_month.set(f"{datetime.now().month:02d}")

        self.cb_ci_day = ctk.CTkComboBox(form_frame, width=60, values=days, state="readonly", font=self.font_normal)
        self.cb_ci_day.grid(row=0, column=5, padx=2, pady=4)
        self.cb_ci_day.set(f"{datetime.now().day:02d}")

        lbl_co = ctk.CTkLabel(form_frame, text="Cikis Tarihi:", font=self.font_normal, text_color="#111827")
        lbl_co.grid(row=1, column=2, padx=(25, 5), pady=4, sticky="e")

        self.cb_co_year = ctk.CTkComboBox(form_frame, width=70, values=years, state="readonly", font=self.font_normal)
        self.cb_co_year.grid(row=1, column=3, padx=2, pady=4)
        self.cb_co_year.set(str(datetime.now().year))

        self.cb_co_month = ctk.CTkComboBox(form_frame, width=60, values=months, state="readonly", font=self.font_normal)
        self.cb_co_month.grid(row=1, column=4, padx=2, pady=4)
        self.cb_co_month.set(f"{datetime.now().month:02d}")

        self.cb_co_day = ctk.CTkComboBox(form_frame, width=60, values=days, state="readonly", font=self.font_normal)
        self.cb_co_day.grid(row=1, column=5, padx=2, pady=4)
        self.cb_co_day.set(f"{datetime.now().day + 1:02d}" if datetime.now().day <= 30 else "01")

        lbl_price = ctk.CTkLabel(form_frame, text="Gecelik Ucret:", font=self.font_normal, text_color="#111827")
        lbl_price.grid(row=0, column=6, padx=(25, 5), pady=4, sticky="e")

        self.entry_res_price = ctk.CTkEntry(form_frame, width=100, font=self.font_normal, placeholder_text="0")
        self.entry_res_price.grid(row=0, column=7, padx=5, pady=4, sticky="w")

        self.label_res_message = ctk.CTkLabel(form_frame, text="", font=("Poppins", 11), text_color="#dc2626")
        self.label_res_message.grid(row=2, column=0, columnspan=6, padx=15, pady=(4, 4), sticky="w")

        btn_save_res = ctk.CTkButton(
            form_frame,
            text="Rezervasyon Olustur",
            font=self.font_normal,
            fg_color="#60a5fa",
            hover_color="#3b82f6",
            text_color="#0b1120",
            command=self.save_reservation
        )
        btn_save_res.grid(row=1, column=7, padx=15, pady=8, sticky="e")

        self.reservations_scroll = ctk.CTkScrollableFrame(
            frame,
            corner_radius=24,
            width=900,
            height=320,
            fg_color=self.color_panel
        )
        self.reservations_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 5))

        self.label_total_revenue = ctk.CTkLabel(
            frame,
            text="Toplam Odeme: 0",
            font=self.font_normal,
            text_color="#111827"
        )
        self.label_total_revenue.pack(anchor="e", padx=30, pady=(0, 10))

        self.build_reservations_list()
        self.refresh_reservation_choices()
        return frame

    def refresh_reservation_choices(self):
        self.guest_choice_map = {}
        guests = db.get_guests_without_reservation()
        guest_display_list = []
        for gid, first_name, last_name in guests:
            label = f"{gid} - {first_name} {last_name}"
            guest_display_list.append(label)
            self.guest_choice_map[label] = gid
        if guest_display_list:
            self.combo_res_guest.configure(values=guest_display_list)
            self.combo_res_guest.set(guest_display_list[0])
        else:
            self.combo_res_guest.configure(values=["Misafir yok"])
            self.combo_res_guest.set("Misafir yok")

        self.room_choice_map = {}
        rooms = db.get_free_rooms()
        room_display_list = []
        for rid, room_no, room_type in rooms:
            label = f"{room_no} ({room_type})"
            room_display_list.append(label)
            self.room_choice_map[label] = rid
        if room_display_list:
            self.combo_res_room.configure(values=room_display_list)
            self.combo_res_room.set(room_display_list[0])
            self.on_room_change(room_display_list[0])
        else:
            self.combo_res_room.configure(values=["Bos oda yok"])
            self.combo_res_room.set("Bos oda yok")
            self.entry_res_price.delete(0, "end")

    def on_room_change(self, selected_label: str):
        room_id = self.room_choice_map.get(selected_label)
        if not room_id:
            return
        price = db.get_nightly_price_for_room(room_id)
        if price is not None:
            self.entry_res_price.delete(0, "end")
            self.entry_res_price.insert(0, str(price))

    def build_reservations_list(self):
        for child in self.reservations_scroll.winfo_children():
            child.destroy()

        reservations = db.get_all_reservations()
        if not reservations:
            lbl = ctk.CTkLabel(
                self.reservations_scroll,
                text="Henuz rezervasyon kaydi yok.",
                font=self.font_normal,
                text_color="#111827"
            )
            lbl.pack(pady=40)
            self.label_total_revenue.configure(text="Toplam Odeme: 0")
            return

        header = ctk.CTkFrame(self.reservations_scroll, fg_color="#e5e7eb", corner_radius=12)
        header.pack(fill="x", padx=10, pady=(8, 4))

        cols = ["ID", "Misafir", "Oda", "Giris", "Cikis", "Durum", "Toplam Odeme", ""]
        widths = [40, 220, 80, 100, 100, 100, 120, 110]

        for i, (col, w) in enumerate(zip(cols, widths)):
            lbl = ctk.CTkLabel(
                header,
                text=col,
                font=("Poppins", 11, "bold"),
                text_color="#111827",
                width=w,
                anchor="w"
            )
            lbl.grid(row=0, column=i, padx=8, pady=6, sticky="w")

        total_sum = 0.0
        for r in reservations:
            res_id, guest_name, room_number, ci, co, status, total_amount = r
            row_frame = ctk.CTkFrame(self.reservations_scroll, fg_color=self.color_card, corner_radius=12)
            row_frame.pack(fill="x", padx=10, pady=3)

            if total_amount is not None:
                total_sum += float(total_amount)

            values = [
                str(res_id),
                guest_name,
                str(room_number),
                ci.strftime("%Y-%m-%d"),
                co.strftime("%Y-%m-%d"),
                status,
                f"{float(total_amount):.2f}" if total_amount is not None else "-"
            ]

            for i, (val, w) in enumerate(zip(values, widths[:-1])):
                lbl = ctk.CTkLabel(
                    row_frame,
                    text=val,
                    font=self.font_normal,
                    text_color="#111827",
                    width=w,
                    anchor="w"
                )
                lbl.grid(row=0, column=i, padx=8, pady=6, sticky="w")

            btn_cancel = ctk.CTkButton(
                row_frame,
                text="Iptal",
                width=widths[-1],
                font=("Poppins", 11),
                fg_color="#fecaca",
                hover_color="#fca5a5",
                text_color="#b91c1c",
                state="disabled" if status.upper() == "CANCELLED" else "normal",
                command=lambda rid=res_id: self.cancel_reservation(rid)
            )
            btn_cancel.grid(row=0, column=len(values), padx=8, pady=6, sticky="e")

        self.label_total_revenue.configure(text=f"Toplam Odeme: {total_sum:.2f}")

    def save_reservation(self):
        guest_label = self.combo_res_guest.get()
        room_label = self.combo_res_room.get()

        if guest_label == "Misafir yok" or not guest_label:
            self.label_res_message.configure(text="Once misafir eklemelisiniz.", text_color="#dc2626")
            return
        if room_label == "Bos oda yok" or not room_label:
            self.label_res_message.configure(text="Musait oda bulunamadi.", text_color="#dc2626")
            return

        guest_id = self.guest_choice_map.get(guest_label)
        room_id = self.room_choice_map.get(room_label)

        try:
            ci_year = int(self.cb_ci_year.get())
            ci_month = int(self.cb_ci_month.get())
            ci_day = int(self.cb_ci_day.get())
            co_year = int(self.cb_co_year.get())
            co_month = int(self.cb_co_month.get())
            co_day = int(self.cb_co_day.get())
            check_in_date = date(ci_year, ci_month, ci_day)
            check_out_date = date(co_year, co_month, co_day)
        except Exception:
            self.label_res_message.configure(text="Tarih formati hatali.", text_color="#dc2626")
            return

        if check_out_date <= check_in_date:
            self.label_res_message.configure(text="Cikis tarihi, giris tarihinden sonra olmali.", text_color="#dc2626")
            return

        price_str = self.entry_res_price.get().strip()
        try:
            nightly_price = float(price_str)
        except ValueError:
            self.label_res_message.configure(text="Gecelik ucret gecerli bir sayi olmali.", text_color="#dc2626")
            return

        if db.room_has_conflict(room_id, check_in_date, check_out_date):
            self.label_res_message.configure(text="Secilen tarihlerde bu oda zaten dolu.", text_color="#dc2626")
            return

        new_id = db.insert_reservation(guest_id, room_id, check_in_date, check_out_date, nightly_price)
        if new_id is None:
            self.label_res_message.configure(text="Rezervasyon eklenirken hata olustu.", text_color="#dc2626")
            return

        self.label_res_message.configure(text=f"✅ Rezervasyon olusturuldu (ID: {new_id})", text_color="#16a34a")
        self.build_reservations_list()
        self.refresh_reservation_choices()
        self.build_room_cards()
        self.refresh_dashboard()

    def cancel_reservation(self, reservation_id: int):
        ok = db.update_reservation_status(reservation_id, "CANCELLED")
        if ok:
            self.label_res_message.configure(
                text=f"Rezervasyon iptal edildi (ID: {reservation_id}).",
                text_color="#16a34a"
            )
            self.build_reservations_list()
            self.refresh_reservation_choices()
            self.build_room_cards()
            self.refresh_dashboard()
        else:
            self.label_res_message.configure(
                text="Rezervasyon iptal edilirken hata olustu.",
                text_color="#dc2626"
            )

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

