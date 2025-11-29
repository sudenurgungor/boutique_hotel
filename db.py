"""
Geriye dönük uyumluluk için servis katmanını dışarı veren ince arayüz.
UI doğrudan backend/services/hotel_service'i kullanabilir.
"""

from backend.services.hotel_service import *  # noqa: F401,F403
