import customtkinter as ctk
from datetime import date, datetime
from backend.services import hotel_service as db


def create_reservations_frame(app, parent):
    frame = ctk.CTkFrame(parent, corner_radius=24, fg_color=app.color_card)

    title = ctk.CTkLabel(frame, text="Rezervasyon Yonetimi", font=app.font_title, text_color="#111827")
    title.pack(pady=(15, 4), anchor="w", padx=25)

    subtitle = ctk.CTkLabel(
        frame,
        text="Misafir ve oda secerek yeni rezervasyon olusturabilirsiniz.",
        font=app.font_subtitle,
        text_color="#6b7280"
    )
    subtitle.pack(pady=(0, 12), anchor="w", padx=25)

    form_frame = ctk.CTkFrame(frame, corner_radius=16, fg_color=app.color_panel)
    form_frame.pack(fill="x", padx=20, pady=(5, 10))

    lbl_guest = ctk.CTkLabel(form_frame, text="Misafir:", font=app.font_normal, text_color="#111827")
    lbl_guest.grid(row=0, column=0, padx=15, pady=4, sticky="e")

    app.combo_res_guest = ctk.CTkComboBox(form_frame, width=220, font=app.font_normal, values=[], state="readonly")
    app.combo_res_guest.grid(row=0, column=1, padx=15, pady=4, sticky="w")

    lbl_room = ctk.CTkLabel(form_frame, text="Oda:", font=app.font_normal, text_color="#111827")
    lbl_room.grid(row=1, column=0, padx=15, pady=4, sticky="e")

    app.combo_res_room = ctk.CTkComboBox(
        form_frame, width=220, font=app.font_normal, values=[], state="readonly", command=app.on_room_change
    )
    app.combo_res_room.grid(row=1, column=1, padx=15, pady=4, sticky="w")

    lbl_ci = ctk.CTkLabel(form_frame, text="Giris Tarihi:", font=app.font_normal, text_color="#111827")
    lbl_ci.grid(row=0, column=2, padx=(25, 5), pady=4, sticky="e")

    current_year = datetime.now().year
    years = [str(y) for y in range(current_year, current_year + 6)]
    months = [f"{m:02d}" for m in range(1, 13)]
    days = [f"{d:02d}" for d in range(1, 32)]

    app.cb_ci_year = ctk.CTkComboBox(form_frame, width=70, values=years, state="readonly", font=app.font_normal)
    app.cb_ci_year.grid(row=0, column=3, padx=2, pady=4)
    app.cb_ci_year.set(str(datetime.now().year))

    app.cb_ci_month = ctk.CTkComboBox(form_frame, width=60, values=months, state="readonly", font=app.font_normal)
    app.cb_ci_month.grid(row=0, column=4, padx=2, pady=4)
    app.cb_ci_month.set(f"{datetime.now().month:02d}")

    app.cb_ci_day = ctk.CTkComboBox(form_frame, width=60, values=days, state="readonly", font=app.font_normal)
    app.cb_ci_day.grid(row=0, column=5, padx=2, pady=4)
    app.cb_ci_day.set(f"{datetime.now().day:02d}")

    lbl_co = ctk.CTkLabel(form_frame, text="Cikis Tarihi:", font=app.font_normal, text_color="#111827")
    lbl_co.grid(row=1, column=2, padx=(25, 5), pady=4, sticky="e")

    app.cb_co_year = ctk.CTkComboBox(form_frame, width=70, values=years, state="readonly", font=app.font_normal)
    app.cb_co_year.grid(row=1, column=3, padx=2, pady=4)
    app.cb_co_year.set(str(datetime.now().year))

    app.cb_co_month = ctk.CTkComboBox(form_frame, width=60, values=months, state="readonly", font=app.font_normal)
    app.cb_co_month.grid(row=1, column=4, padx=2, pady=4)
    app.cb_co_month.set(f"{datetime.now().month:02d}")

    app.cb_co_day = ctk.CTkComboBox(form_frame, width=60, values=days, state="readonly", font=app.font_normal)
    app.cb_co_day.grid(row=1, column=5, padx=2, pady=4)
    app.cb_co_day.set(f"{datetime.now().day + 1:02d}" if datetime.now().day <= 30 else "01")

    lbl_price = ctk.CTkLabel(form_frame, text="Gecelik Ucret:", font=app.font_normal, text_color="#111827")
    lbl_price.grid(row=0, column=6, padx=(25, 5), pady=4, sticky="e")

    app.entry_res_price = ctk.CTkEntry(form_frame, width=100, font=app.font_normal, placeholder_text="0")
    app.entry_res_price.grid(row=0, column=7, padx=5, pady=4, sticky="w")

    app.label_res_message = ctk.CTkLabel(form_frame, text="", font=("Poppins", 11), text_color="#dc2626")
    app.label_res_message.grid(row=2, column=0, columnspan=6, padx=15, pady=(4, 4), sticky="w")

    btn_save_res = ctk.CTkButton(
        form_frame,
        text="Rezervasyon Olustur",
        font=app.font_normal,
        fg_color="#60a5fa",
        hover_color="#3b82f6",
        text_color="#0b1120",
        command=app.save_reservation
    )
    btn_save_res.grid(row=1, column=7, padx=15, pady=8, sticky="e")

    app.reservations_scroll = ctk.CTkScrollableFrame(
        frame,
        corner_radius=24,
        width=900,
        height=320,
        fg_color=app.color_panel
    )
    app.reservations_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 5))

    app.label_total_revenue = ctk.CTkLabel(
        frame,
        text="Toplam Odeme: 0",
        font=app.font_normal,
        text_color="#111827"
    )
    app.label_total_revenue.pack(anchor="e", padx=30, pady=(0, 10))

    app.build_reservations_list()
    app.refresh_reservation_choices()
    return frame


def refresh_reservation_choices(app):
    app.guest_choice_map = {}
    guests = db.get_guests_without_reservation()
    guest_display_list = []
    for gid, first_name, last_name in guests:
        label = f"{gid} - {first_name} {last_name}"
        guest_display_list.append(label)
        app.guest_choice_map[label] = gid
    if guest_display_list:
        app.combo_res_guest.configure(values=guest_display_list)
        app.combo_res_guest.set(guest_display_list[0])
    else:
        app.combo_res_guest.configure(values=["Misafir yok"])
        app.combo_res_guest.set("Misafir yok")

    app.room_choice_map = {}
    rooms = db.get_free_rooms()
    room_display_list = []
    for rid, room_no, room_type in rooms:
        label = f"{room_no} ({room_type})"
        room_display_list.append(label)
        app.room_choice_map[label] = rid
    if room_display_list:
        app.combo_res_room.configure(values=room_display_list)
        app.combo_res_room.set(room_display_list[0])
        app.on_room_change(room_display_list[0])
    else:
        app.combo_res_room.configure(values=["Bos oda yok"])
        app.combo_res_room.set("Bos oda yok")
        app.entry_res_price.delete(0, "end")


def on_room_change(app, selected_label: str):
    room_id = app.room_choice_map.get(selected_label)
    if not room_id:
        return
    price = db.get_nightly_price_for_room(room_id)
    if price is not None:
        app.entry_res_price.delete(0, "end")
        app.entry_res_price.insert(0, str(price))


def build_reservations_list(app):
    for child in app.reservations_scroll.winfo_children():
        child.destroy()

    reservations = db.get_all_reservations()
    if not reservations:
        lbl = ctk.CTkLabel(
            app.reservations_scroll,
            text="Henuz rezervasyon kaydi yok.",
            font=app.font_normal,
            text_color="#111827"
        )
        lbl.pack(pady=40)
        app.label_total_revenue.configure(text="Toplam Odeme: 0")
        return

    header = ctk.CTkFrame(app.reservations_scroll, fg_color="#e5e7eb", corner_radius=12)
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
        row_frame = ctk.CTkFrame(app.reservations_scroll, fg_color=app.color_card, corner_radius=12)
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
                font=app.font_normal,
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
            command=lambda rid=res_id: app.cancel_reservation(rid)
        )
        btn_cancel.grid(row=0, column=len(values), padx=8, pady=6, sticky="e")

    app.label_total_revenue.configure(text=f"Toplam Odeme: {total_sum:.2f}")


def save_reservation(app):
    guest_label = app.combo_res_guest.get()
    room_label = app.combo_res_room.get()

    if guest_label == "Misafir yok" or not guest_label:
        app.label_res_message.configure(text="Once misafir eklemelisiniz.", text_color="#dc2626")
        return
    if room_label == "Bos oda yok" or not room_label:
        app.label_res_message.configure(text="Musait oda bulunamadi.", text_color="#dc2626")
        return

    guest_id = app.guest_choice_map.get(guest_label)
    room_id = app.room_choice_map.get(room_label)

    try:
        ci_year = int(app.cb_ci_year.get())
        ci_month = int(app.cb_ci_month.get())
        ci_day = int(app.cb_ci_day.get())
        co_year = int(app.cb_co_year.get())
        co_month = int(app.cb_co_month.get())
        co_day = int(app.cb_co_day.get())
        check_in_date = date(ci_year, ci_month, ci_day)
        check_out_date = date(co_year, co_month, co_day)
    except Exception:
        app.label_res_message.configure(text="Tarih formati hatali.", text_color="#dc2626")
        return

    if check_out_date <= check_in_date:
        app.label_res_message.configure(text="Cikis tarihi, giris tarihinden sonra olmali.", text_color="#dc2626")
        return

    price_str = app.entry_res_price.get().strip()
    try:
        nightly_price = float(price_str)
    except ValueError:
        app.label_res_message.configure(text="Gecelik ucret gecerli bir sayi olmali.", text_color="#dc2626")
        return

    if db.room_has_conflict(room_id, check_in_date, check_out_date):
        app.label_res_message.configure(text="Secilen tarihlerde bu oda zaten dolu.", text_color="#dc2626")
        return

    new_id = db.insert_reservation(guest_id, room_id, check_in_date, check_out_date, nightly_price)
    if new_id is None:
        app.label_res_message.configure(text="Rezervasyon eklenirken hata olustu.", text_color="#dc2626")
        return

    app.label_res_message.configure(text=f"Rezervasyon olusturuldu (ID: {new_id})", text_color="#16a34a")
    app.build_reservations_list()
    app.refresh_reservation_choices()
    app.build_room_cards()
    app.refresh_dashboard()


def cancel_reservation(app, reservation_id: int):
    ok = db.update_reservation_status(reservation_id, "CANCELLED")
    if ok:
        app.label_res_message.configure(
            text=f"Rezervasyon iptal edildi (ID: {reservation_id}).",
            text_color="#16a34a"
        )
        app.build_reservations_list()
        app.refresh_reservation_choices()
        app.build_room_cards()
        app.refresh_dashboard()
    else:
        app.label_res_message.configure(
            text="Rezervasyon iptal edilirken hata olustu.",
            text_color="#dc2626"
        )
