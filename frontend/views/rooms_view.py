import tkinter as tk
import customtkinter as ctk
from backend.services import hotel_service as db


def create_rooms_frame(app, parent):
    frame = ctk.CTkFrame(parent, corner_radius=24, fg_color=app.color_card)

    title = ctk.CTkLabel(
        frame,
        text="Oda Yonetimi",
        font=app.font_title,
        text_color="#111827"
    )
    title.pack(pady=(15, 4), anchor="w", padx=25)

    subtitle = ctk.CTkLabel(
        frame,
        text="Oda durumlarini buradan takip edebilir, hizlica guncelleyebilirsiniz.",
        font=app.font_subtitle,
        text_color="#6b7280"
    )
    subtitle.pack(pady=(0, 12), anchor="w", padx=25)

    app.rooms_scroll = ctk.CTkScrollableFrame(
        frame,
        corner_radius=24,
        width=900,
        height=520,
        fg_color=app.color_panel
    )
    app.rooms_scroll.pack(fill="both", expand=True, padx=20, pady=10)

    app.build_room_cards()
    return frame

def build_room_cards(app):
    for child in app.rooms_scroll.winfo_children():
        child.destroy()

    rooms = db.get_all_rooms()
    if not rooms:
        empty_label = ctk.CTkLabel(
            app.rooms_scroll,
            text="Hic oda bulunamadi.",
            font=app.font_normal,
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
                app.rooms_scroll,
                text=f"{floor}. KAT",
                font=app.font_floor,
                text_color="#111827"
            )
            floor_label.pack(anchor="w", padx=18, pady=(18, 6))

            floor_frame = ctk.CTkFrame(app.rooms_scroll, fg_color="transparent")
            floor_frame.pack(fill="x", padx=10, pady=(0, 8))

            for idx, r in enumerate(floors[floor]):
                room_id, room_no, room_type, f, status = r
                bg_color = app.get_room_type_color(room_type)
                status_text = app.get_status_text(status)

                def bind_card_click(widget, rid=room_id):
                    widget.bind("<Button-1>", lambda e, rid=rid: app.open_status_menu(e, rid))

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
                    font=app.font_card_type,
                    text_color="#111827"
                )
                type_label.pack(anchor="w", padx=15, pady=(10, 0))
                bind_card_click(type_label)

                number_label = ctk.CTkLabel(
                    card,
                    text=f"#{room_no}",
                    font=app.font_card_number,
                    text_color="#111827"
                )
                number_label.pack(anchor="w", padx=15, pady=(2, 0))
                bind_card_click(number_label)

                status_badge = ctk.CTkLabel(
                    card,
                    text=status_text,
                    font=app.font_badge,
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
                    command=lambda rid=room_id: app.open_reservation_for_room(rid)
                )
                btn_res.pack(anchor="w", padx=15, pady=(6, 6))

    def open_status_menu(app, event, room_id: int):
        # Eski popup'u kapat
        if app.status_popup is not None:
            try:
                app.status_popup.destroy()
            except Exception:
                pass
            app.status_popup = None

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

        status_text = app.get_status_text(status)
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
            command=lambda rid=room_id: app.open_reservation_for_room(rid, modal)
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
                app.build_room_cards()
                app.refresh_reservation_choices()
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

        app.status_popup = modal

    def open_reservation_for_room(app, room_id: int, modal_to_close=None):
        app.show_reservations_view()
        app.refresh_reservation_choices()
        for label, rid in app.room_choice_map.items():
            if rid == room_id:
                app.combo_res_room.set(label)
                break
        app.label_res_message.configure(
            text=f"Oda icin rezervasyon olusturuyorsunuz (ID={room_id}).",
            text_color="#6b7280"
        )
        if modal_to_close:
            try:
                modal_to_close.destroy()
            except Exception:
                pass
