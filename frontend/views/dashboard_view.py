import tkinter as tk
import customtkinter as ctk
from backend.services import hotel_service as db


def create_dashboard_frame(app, parent):
    frame = ctk.CTkFrame(parent, corner_radius=24, fg_color=app.color_card)

    title = ctk.CTkLabel(
        frame,
        text="Dashboard",
        font=app.font_title,
        text_color=app.color_text_main
    )
    title.pack(pady=(15, 4), anchor="w", padx=25)

    subtitle = ctk.CTkLabel(
        frame,
        text="Otelin genel durumunu buradan gorebilirsiniz.",
        font=app.font_subtitle,
        text_color="#475569"
    )
    subtitle.pack(pady=(0, 12), anchor="w", padx=25)

    cards_frame = ctk.CTkFrame(frame, fg_color=app.color_panel, corner_radius=16)
    cards_frame.pack(fill="x", padx=20, pady=(5, 10))

    app.lbl_stat_total_rooms = _create_stat_card(app, cards_frame, 0, "Toplam Oda", "0")
    app.lbl_stat_month_res = _create_stat_card(app, cards_frame, 1, "Bu Ayki Rezervasyon", "0")
    app.lbl_stat_active_guests = _create_stat_card(app, cards_frame, 2, "Aktif Misafir", "0")
    app.lbl_stat_occupancy = _create_stat_card(app, cards_frame, 3, "Doluluk Orani", "%0")

    chart_container = ctk.CTkFrame(frame, fg_color=app.color_panel, corner_radius=16)
    chart_container.pack(fill="both", expand=True, padx=20, pady=(5, 15))

    chart_title = ctk.CTkLabel(
        chart_container,
        text="Yillik Rezervasyon Analizi",
        font=("Poppins", 14, "bold"),
        text_color="#111827"
    )
    chart_title.pack(anchor="w", padx=15, pady=(10, 0))

    app.dashboard_chart_canvas = tk.Canvas(
        chart_container,
        bg=app.color_panel,
        highlightthickness=0
    )
    app.dashboard_chart_canvas.pack(fill="both", expand=True, padx=15, pady=10)

    return frame


def _create_stat_card(app, parent, col, title, value):
    card = ctk.CTkFrame(parent, fg_color=app.color_card, corner_radius=16)
    card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
    parent.grid_columnconfigure(col, weight=1)

    lbl_title = ctk.CTkLabel(
        card,
        text=title,
        font=app.font_subtitle,
        text_color="#475569"
    )
    lbl_title.pack(anchor="w", padx=12, pady=(10, 0))

    lbl_value = ctk.CTkLabel(
        card,
        text=value,
        font=("Poppins", 20, "bold"),
        text_color=app.color_text_main
    )
    lbl_value.pack(anchor="w", padx=12, pady=(4, 12))

    return lbl_value


def refresh_dashboard(app):
    total_rooms, res_this_month, active_guests, occ_rate = db.get_dashboard_stats()

    app.lbl_stat_total_rooms.configure(text=str(total_rooms))
    app.lbl_stat_month_res.configure(text=str(res_this_month))
    app.lbl_stat_active_guests.configure(text=str(active_guests))
    app.lbl_stat_occupancy.configure(text=f"%{int(occ_rate * 100)}")

    data = db.get_yearly_reservation_stats()
    month_to_count = {m: c for (m, c) in data}

    canvas = app.dashboard_chart_canvas
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
