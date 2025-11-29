import customtkinter as ctk

# Tema: LIGHT + pastel
APPEARANCE_MODE = "light"
DEFAULT_COLOR_THEME = "blue"

# Font yolları
FONT_FILES = [
    "Poppins/Poppins-Regular.ttf",
    "Poppins/Poppins-Medium.ttf",
    "Poppins/Poppins-Bold.ttf",
]

# Uygulama genelinde kullanacağımız font setleri
FONT_SETS = {
    "header": ("Poppins", 26, "bold"),
    "sidebar": ("Poppins", 14, "bold"),
    "title": ("Poppins", 20, "bold"),
    "subtitle": ("Poppins", 13),
    "card_type": ("Poppins", 12),
    "card_number": ("Poppins", 26, "bold"),
    "badge": ("Poppins", 11, "bold"),
    "floor": ("Poppins", 18, "bold"),
    "normal": ("Poppins", 12),
}

# Modern açık/lila tema renkleri
COLORS = {
    "bg": "#edf1ff",  # ana arka plan
    "panel": "#ffffff",  # içerik paneli / kart zemini
    "card": "#ffffff",  # kart zemini
    "sidebar": "#5f62f3",  # sidebar / üst bar (koyu mor-mavi)
    "sidebar_dark": "#4d53d9",  # sidebar hover
    "sidebar_light": "#6f7dfb",  # aktif nav vurgu
    "accent": "#5f62f3",  # ana vurgu (butonlar)
    "accent_alt": "#ffdd94",  # ikincil vurgu
    "text_main": "#1f2430",
}


def apply_appearance():
    ctk.set_appearance_mode(APPEARANCE_MODE)
    ctk.set_default_color_theme(DEFAULT_COLOR_THEME)


def load_fonts():
    for font_file in FONT_FILES:
        try:
            ctk.FontManager.load_font(font_file)
        except Exception:
            # Font yüklenemezse default'a düşsün
            pass
