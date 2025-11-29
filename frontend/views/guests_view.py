import customtkinter as ctk
from backend.services import hotel_service as db


def create_guests_frame(app, parent):
    frame = ctk.CTkFrame(parent, corner_radius=24, fg_color=app.color_card)

    title = ctk.CTkLabel(frame, text="Misafir Yonetimi", font=app.font_title, text_color="#111827")
    title.pack(pady=(15, 4), anchor="w", padx=25)

    subtitle = ctk.CTkLabel(
        frame,
        text="Yeni misafir ekleyebilir, duzenleyebilir veya silebilirsiniz.",
        font=app.font_subtitle,
        text_color="#6b7280"
    )
    subtitle.pack(pady=(0, 12), anchor="w", padx=25)

    form_frame = ctk.CTkFrame(frame, corner_radius=16, fg_color=app.color_panel)
    form_frame.pack(fill="x", padx=20, pady=(5, 10))

    form_title = ctk.CTkLabel(
        form_frame,
        text="Yeni Misafir Ekle / Guncelle",
        font=("Poppins", 14, "bold"),
        text_color="#111827"
    )
    form_title.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

    label_first = ctk.CTkLabel(form_frame, text="Ad:", font=app.font_normal, text_color="#111827")
    label_first.grid(row=1, column=0, padx=15, pady=4, sticky="e")
    app.entry_guest_first_name = ctk.CTkEntry(form_frame, width=180, font=app.font_normal, placeholder_text="Ad")
    app.entry_guest_first_name.grid(row=1, column=1, padx=15, pady=4, sticky="w")

    label_last = ctk.CTkLabel(form_frame, text="Soyad:", font=app.font_normal, text_color="#111827")
    label_last.grid(row=2, column=0, padx=15, pady=4, sticky="e")
    app.entry_guest_last_name = ctk.CTkEntry(form_frame, width=180, font=app.font_normal, placeholder_text="Soyad")
    app.entry_guest_last_name.grid(row=2, column=1, padx=15, pady=4, sticky="w")

    label_email = ctk.CTkLabel(form_frame, text="E-posta:", font=app.font_normal, text_color="#111827")
    label_email.grid(row=1, column=2, padx=15, pady=4, sticky="e")
    app.entry_guest_email = ctk.CTkEntry(form_frame, width=200, font=app.font_normal, placeholder_text="ornek@mail.com")
    app.entry_guest_email.grid(row=1, column=3, padx=15, pady=4, sticky="w")

    label_phone = ctk.CTkLabel(form_frame, text="Telefon:", font=app.font_normal, text_color="#111827")
    label_phone.grid(row=2, column=2, padx=15, pady=4, sticky="e")
    app.entry_guest_phone = ctk.CTkEntry(form_frame, width=200, font=app.font_normal, placeholder_text="+90...")
    app.entry_guest_phone.grid(row=2, column=3, padx=15, pady=4, sticky="w")

    label_tc = ctk.CTkLabel(form_frame, text="T.C. Kimlik No:", font=app.font_normal, text_color="#111827")
    label_tc.grid(row=3, column=0, padx=15, pady=4, sticky="e")
    app.entry_guest_tc = ctk.CTkEntry(form_frame, width=180, font=app.font_normal, placeholder_text="11 haneli")
    app.entry_guest_tc.grid(row=3, column=1, padx=15, pady=4, sticky="w")

    app.label_guest_message = ctk.CTkLabel(form_frame, text="", font=("Poppins", 11), text_color="#dc2626")
    app.label_guest_message.grid(row=4, column=0, columnspan=4, padx=15, pady=(4, 4), sticky="w")

    app.btn_save_guest = ctk.CTkButton(
        form_frame,
        text="Kaydet",
        font=app.font_normal,
        fg_color="#4ade80",
        hover_color="#22c55e",
        text_color="#064e3b",
        command=app.save_guest
    )
    app.btn_save_guest.grid(row=3, column=3, padx=15, pady=8, sticky="e")

    app.guests_scroll = ctk.CTkScrollableFrame(
        frame,
        corner_radius=24,
        width=900,
        height=350,
        fg_color=app.color_panel
    )
    app.guests_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 10))

    app.build_guest_list()
    return frame

def build_guest_list(app):
        for child in app.guests_scroll.winfo_children():
            child.destroy()

        guests = db.get_all_guests()
        if not guests:
            empty_label = ctk.CTkLabel(
                app.guests_scroll,
                text="Henuz misafir kaydi yok.",
                font=app.font_normal,
                text_color="#111827"
            )
            empty_label.pack(pady=20)
            return

        header_frame = ctk.CTkFrame(app.guests_scroll, fg_color="#e5e7eb", corner_radius=12)
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
            row_frame = ctk.CTkFrame(app.guests_scroll, fg_color=app.color_card, corner_radius=12)
            row_frame.pack(fill="x", padx=10, pady=3)

            full_name = f"{first_name} {last_name}"
            values = [str(guest_id), full_name, phone or "-", email or "-", tc_no or "-"]

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
                    app.load_guest_into_form(gid, fn, ln, em, ph, tc)
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
                command=lambda gid=guest_id: app.delete_guest(gid)
            )
            btn_del.pack(side="left", padx=2)


def load_guest_into_form(app, guest_id, first_name, last_name, email, phone, tc_no):
    app.selected_guest_id = guest_id
    app.entry_guest_first_name.delete(0, "end")
    app.entry_guest_first_name.insert(0, first_name or "")
    app.entry_guest_last_name.delete(0, "end")
    app.entry_guest_last_name.insert(0, last_name or "")
    app.entry_guest_email.delete(0, "end")
    app.entry_guest_email.insert(0, email or "")
    app.entry_guest_phone.delete(0, "end")
    app.entry_guest_phone.insert(0, phone or "")
    app.entry_guest_tc.delete(0, "end")
    app.entry_guest_tc.insert(0, tc_no or "")
    app.label_guest_message.configure(
        text=f"ID {guest_id} misafirini duzenliyorsunuz.",
        text_color="#6b7280"
    )
    app.btn_save_guest.configure(text="Guncelle")


def save_guest(app):
        first_name = app.entry_guest_first_name.get().strip()
        last_name = app.entry_guest_last_name.get().strip()
        email = app.entry_guest_email.get().strip() or None
        phone = app.entry_guest_phone.get().strip() or None
        tc_no = app.entry_guest_tc.get().strip() or None

        if not first_name or not last_name:
            app.label_guest_message.configure(text="Ad ve Soyad zorunludur.", text_color="#dc2626")
            return

        if app.selected_guest_id is not None:
            ok = db.update_guest(app.selected_guest_id, first_name, last_name, email, phone, tc_no)
            if ok:
                app.label_guest_message.configure(
                    text=f"✅ Misafir basariyla guncellendi (ID: {app.selected_guest_id})",
                    text_color="#16a34a"
                )
                app.selected_guest_id = None
                app.btn_save_guest.configure(text="Kaydet")
                app.entry_guest_first_name.delete(0, "end")
                app.entry_guest_last_name.delete(0, "end")
                app.entry_guest_email.delete(0, "end")
                app.entry_guest_phone.delete(0, "end")
                app.entry_guest_tc.delete(0, "end")
                app.build_guest_list()
                app.refresh_reservation_choices()
            else:
                app.label_guest_message.configure(
                    text="❌ Misafir guncellenirken hata olustu.",
                    text_color="#dc2626"
                )
            return

        new_id = db.insert_guest(first_name, last_name, email, phone, tc_no)
        if new_id is not None:
            app.label_guest_message.configure(
                text=f"✅ Misafir basariyla eklendi (ID: {new_id})",
                text_color="#16a34a"
            )
            app.entry_guest_first_name.delete(0, "end")
            app.entry_guest_last_name.delete(0, "end")
            app.entry_guest_email.delete(0, "end")
            app.entry_guest_phone.delete(0, "end")
            app.entry_guest_tc.delete(0, "end")
            app.build_guest_list()
            app.refresh_reservation_choices()
        else:
            app.label_guest_message.configure(
                text="❌ Misafir eklenirken bir hata olustu.",
                text_color="#dc2626"
            )


def delete_guest(app, guest_id: int):
        ok = db.delete_guest(guest_id)
        if ok:
            app.label_guest_message.configure(
                text=f"✅ Misafir silindi (ID: {guest_id}).",
                text_color="#16a34a"
            )
            app.build_guest_list()
            app.refresh_reservation_choices()
        else:
            app.label_guest_message.configure(
                text="❌ Misafir silinemedi. (Muhtemelen aktif rezervasyonu var.)",
                text_color="#dc2626"
            )
