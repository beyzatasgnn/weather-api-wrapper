# models.py
from pydantic import BaseModel

# API'mizin dış dünyaya döndüreceği sadeleştirilmiş veri yapısı
class WeatherResponse(BaseModel):
    sehir: str
    ulke: str
    sicaklik: float
    hissedilen_sicaklik: float
    durum_ozet: str
    nem_oranı: int
    ruzgar_hizi: float

# Hata mesajı için basit bir yapı
class ErrorResponse(BaseModel):
    hata: str