import customtkinter as ctk
from backend.services import hotel_service as db


def create_room_types_frame(app, parent):
    frame = ctk.CTkFrame(parent, corner_radius=24, fg_color=app.color_card)

    title = ctk.CTkLabel(
        frame,
        text="Oda Tipleri",
        font=app.font_title,
        text_color="#111827"
    )
    title.pack(pady=(15, 4), anchor="w", padx=25)

    subtitle = ctk.CTkLabel(
        frame,
        text="Oda tiplerinin adini, aciklamasini, taban fiyatini ve kapasitesini yonetebilirsiniz.",
        font=app.font_subtitle,
        text_color="#6b7280"
    )
    subtitle.pack(pady=(0, 12), anchor="w", padx=25)

    form_frame = ctk.CTkFrame(frame, corner_radius=16, fg_color=app.color_panel)
    form_frame.pack(fill="x", padx=20, pady=(5, 10))

    lbl_name = ctk.CTkLabel(form_frame, text="Tip Adi:", font=app.font_normal, text_color="#111827")
    lbl_name.grid(row=0, column=0, padx=15, pady=4, sticky="e")

    app.entry_rt_name = ctk.CTkEntry(form_frame, width=180, font=app.font_normal, placeholder_text="Standart Oda")
    app.entry_rt_name.grid(row=0, column=1, padx=15, pady=4, sticky="w")

    lbl_desc = ctk.CTkLabel(form_frame, text="Aciklama:", font=app.font_normal, text_color="#111827")
    lbl_desc.grid(row=1, column=0, padx=15, pady=4, sticky="e")

    app.entry_rt_desc = ctk.CTkEntry(form_frame, width=280, font=app.font_normal, placeholder_text="Kisa aciklama")
    app.entry_rt_desc.grid(row=1, column=1, columnspan=2, padx=15, pady=4, sticky="w")

    lbl_price = ctk.CTkLabel(form_frame, text="Taban Fiyat:", font=app.font_normal, text_color="#111827")
    lbl_price.grid(row=0, column=2, padx=15, pady=4, sticky="e")

    app.entry_rt_price = ctk.CTkEntry(form_frame, width=120, font=app.font_normal, placeholder_text="1500")
    app.entry_rt_price.grid(row=0, column=3, padx=15, pady=4, sticky="w")

    lbl_cap = ctk.CTkLabel(form_frame, text="Kapasite:", font=app.font_normal, text_color="#111827")
    lbl_cap.grid(row=0, column=4, padx=15, pady=4, sticky="e")

    app.entry_rt_capacity = ctk.CTkEntry(form_frame, width=80, font=app.font_normal, placeholder_text="2")
    app.entry_rt_capacity.grid(row=0, column=5, padx=15, pady=4, sticky="w")

    app.label_rt_message = ctk.CTkLabel(form_frame, text="", font=("Poppins", 11), text_color="#dc2626")
    app.label_rt_message.grid(row=2, column=0, columnspan=4, padx=15, pady=(4, 4), sticky="w")

    app.btn_rt_save = ctk.CTkButton(
        form_frame, text="Ekle", font=app.font_normal,
        fg_color="#4ade80", hover_color="#22c55e", text_color="#064e3b",
        command=app.save_room_type
    )
    app.btn_rt_save.grid(row=1, column=4, padx=15, pady=8, sticky="e")

    app.btn_rt_delete = ctk.CTkButton(
        form_frame, text="Sil", font=app.font_normal,
        fg_color="#fecaca", hover_color="#fca5a5", text_color="#b91c1c",
        command=app.delete_room_type
    )
    app.btn_rt_delete.grid(row=1, column=5, padx=15, pady=8, sticky="e")

    app.room_types_scroll = ctk.CTkScrollableFrame(
        frame, corner_radius=24, width=900, height=400, fg_color=app.color_panel
    )
    app.room_types_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 10))

    app.build_room_type_list()
    return frame

def build_room_type_list(app):
        for child in app.room_types_scroll.winfo_children():
            child.destroy()

        room_types = db.get_all_room_types()
        if not room_types:
            lbl = ctk.CTkLabel(
                app.room_types_scroll,
                text="Tanimli oda tipi yok.",
                font=app.font_normal,
                text_color="#111827"
            )
            lbl.pack(pady=20)
            return

        header = ctk.CTkFrame(app.room_types_scroll, fg_color="#e5e7eb", corner_radius=12)
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
            row = ctk.CTkFrame(app.room_types_scroll, fg_color=app.color_card, corner_radius=12)
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
                    font=app.font_normal,
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
                    app.load_room_type_into_form(rid, n, d, p, c)
            )
            btn_edit.grid(row=0, column=len(values), padx=8, pady=6, sticky="e")


def load_room_type_into_form(app, rt_id, name, desc, price, cap):
    app.selected_room_type_id = rt_id
    app.entry_rt_name.delete(0, "end")
    app.entry_rt_name.insert(0, name or "")
    app.entry_rt_desc.delete(0, "end")
    app.entry_rt_desc.insert(0, desc or "")
    app.entry_rt_price.delete(0, "end")
    if price is not None:
        app.entry_rt_price.insert(0, str(price))
    app.entry_rt_capacity.delete(0, "end")
    if cap is not None:
        app.entry_rt_capacity.insert(0, str(cap))
    app.label_rt_message.configure(
        text=f"Oda tipi duzenleniyor (ID={rt_id}).",
        text_color="#6b7280"
    )
    app.btn_rt_save.configure(text="Guncelle")


def save_room_type(app):
    name = app.entry_rt_name.get().strip()
    desc = app.entry_rt_desc.get().strip() or None
    price_str = app.entry_rt_price.get().strip()
    cap_str = app.entry_rt_capacity.get().strip()

    if not name:
        app.label_rt_message.configure(text="Tip adi zorunludur.", text_color="#dc2626")
        return

    try:
        price = float(price_str)
        cap = int(cap_str)
    except ValueError:
        app.label_rt_message.configure(text="Fiyat ve kapasite sayisal olmalidir.", text_color="#dc2626")
        return

    if app.selected_room_type_id is None:
        new_id = db.insert_room_type(name, desc, price, cap)
        if new_id is not None:
            app.label_rt_message.configure(
                text=f"Oda tipi eklendi (ID={new_id}).",
                text_color="#16a34a"
            )
    else:
        ok = db.update_room_type(app.selected_room_type_id, name, desc, price, cap)
        if ok:
            app.label_rt_message.configure(
                text=f"Oda tipi guncellendi (ID={app.selected_room_type_id}).",
                text_color="#16a34a"
            )

    app.selected_room_type_id = None
    app.btn_rt_save.configure(text="Ekle")
    app.entry_rt_name.delete(0, "end")
    app.entry_rt_desc.delete(0, "end")
    app.entry_rt_price.delete(0, "end")
    app.entry_rt_capacity.delete(0, "end")

    app.build_room_type_list()
    app.build_room_cards()


def delete_room_type(app):
    if app.selected_room_type_id is None:
        app.label_rt_message.configure(
            text="Silmek icin once listeden bir oda tipi secin.",
            text_color="#dc2626"
        )
        return

    ok = db.delete_room_type(app.selected_room_type_id)
    if ok:
        app.label_rt_message.configure(
            text=f"Oda tipi silindi (ID={app.selected_room_type_id}).",
            text_color="#16a34a"
        )
        app.selected_room_type_id = None
        app.btn_rt_save.configure(text="Ekle")
        app.entry_rt_name.delete(0, "end")
        app.entry_rt_desc.delete(0, "end")
        app.entry_rt_price.delete(0, "end")
        app.entry_rt_capacity.delete(0, "end")
        app.build_room_type_list()
        app.build_room_cards()
