# main.py
import os
import httpx
from fastapi import FastAPI, HTTPException, status, Query
from dotenv import load_dotenv
from models import WeatherResponse, ErrorResponse

# Çevre değişkenlerini yükle
load_dotenv()

# ------------------ Sabitler ve Ayarlar ------------------
OPENWEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
OPENWEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

# API Anahtarı kontrolü
if not OPENWEATHER_API_KEY:
    raise ValueError("API anahtarı yüklenemedi. '.env' dosyasını kontrol edin.")

# FastAPI uygulamasını başlat
app = FastAPI(title="Hava Durumu Sarıcısı", version="1.0")

# ------------------ API Uç Noktası (Endpoint) ------------------

# response_model: Başarılı durumda hangi veri modelini döndüreceğimizi belirtir
# responses: Hata durumunda ne döndüreceğimizi belirtir (dokümantasyon için)
@app.get(
    "/api/hava-durumu",
    response_model=WeatherResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}}
)
async def get_weather(
    # Query ile URL'den 'sehir' parametresini alırız ve zorunlu yaparız
    sehir: str = Query(..., description="Hava durumu bilgisini almak istediğiniz şehir.")
):

    # Harici API isteği için parametreler
    params = {
        'q': sehir,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',  # Sıcaklığı Celsius al
        'lang': 'tr'        # Türkçe açıklama al
    }

    # httpx ile asenkron istek
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPENWEATHER_URL, params=params)
            response.raise_for_status() # HTTP 4xx/5xx hatalarını yakala
            data = response.json()

        except httpx.HTTPStatusError as e:
            # 404 (Not Found) hatasını yakala
            if e.response.status_code == 404:
                # Kullanıcıya 404 hatası döndür
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"hata": f"Şehir bulunamadı: {sehir}"}
                )
            # Diğer HTTP hataları
            raise HTTPException(
                status_code=e.response.status_code,
                detail={"hata": "Harici API'den beklenmeyen hata."}
            )
        except httpx.RequestError as e:
            # Bağlantı veya timeout hataları
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"hata": "Harici API'ye ulaşılamıyor."}
            )

    # Veri Dönüştürme: Gelen karmaşık veriyi sadeleştirme
    weather_info = data['weather'][0]

    # Pydantic modelini doldurup geri döndürme
    return WeatherResponse(
        sehir=data.get('name', sehir),
        ulke=data['sys']['country'],
        sicaklik=data['main']['temp'],
        hissedilen_sicaklik=data['main']['feels_like'],
        durum_ozet=weather_info['description'].capitalize(),
        nem_oranı=data['main']['humidity'],
        ruzgar_hizi=data['wind']['speed'],
    )