from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# 1. Veritabanı niyetine kullanacağımız basit ürün listemiz
URUNLER = {
    "1": {"isim": "Kablosuz Kulaklık", "fiyat": 750},
    "2": {"isim": "Oyuncu Mouse", "fiyat": 450},
    "3": {"isim": "Mekanik Klavye", "fiyat": 1200}
}

# Alışveriş sepetimizi şimdilik basit bir sözlükte tutuyoruz
# Ürün ID'si -> Adet şeklinde eşleşecek
SEPET = {}

# 2. Web sunucumuzun gelen istekleri (Tıklamaları, sayfa geçişlerini) nasıl yöneteceğini tanımlıyoruz
class EticaretSunucusu(BaseHTTPRequestHandler):
    
    def do_GET(self):
        global SEPET
        # Gelen URL'i ayrıştırıyoruz (Örn: /ekle?id=1)
        parsed_url = urlparse(self.path)
        sayfa = parsed_url.path
        parametreler = parse_qs(parsed_url.query)
        
        # Tarayıcıya başarılı bir bağlantı kurduğumuzu (HTTP 200) ve HTML göndereceğimizi söylüyoruz
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        # --- SEPETE EKLEME MANTIĞI ---
        if sayfa == "/ekle":
            urun_id = parametreler.get("id", [None])[0]
            if urun_id in URUNLER:
                # Sepette varsa 1 artır, yoksa ilk defa ekle
                SEPET[urun_id] = SEPET.get(urun_id, 0) + 1
            
            # Ürünü ekledikten sonra ana sayfaya geri yönlendirmek için bir HTML çıktısı veriyoruz
            self.wfile.write(b"<script>alert('Urun sepete eklendi!'); window.location.href='/';</script>")
            return

        # --- SEPETİ TEMİZLEME MANTIĞI ---
        elif sayfa == "/temizle":
            SEPET.clear()
            self.wfile.write(b"<script>window.location.href='/';</script>")
            return

        # --- HTML ARAYÜZÜ OLUŞTURMA ---
        # Sitenin üst kısmını (Header) hazırlayalım
        html_icerik = """
        <html>
        <head>
            <title>En Sıfırdan E-Ticaret</title>
            <style>
                body { font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #fafafa; }
                .urun { background: white; padding: 15px; margin-bottom: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
                .buton { background: #007bff; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; }
                .sepet-kutusu { background: #e9ecef; padding: 20px; border-radius: 5px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <h1>Sıfır Kütüphane Teknolojik Market</h1>
            <hr>
            <h2>Ürünler</h2>
        """
        
        # Ürünleri döngüyle HTML içerisine gömüyoruz
        for u_id, detay in URUNLER.items():
            html_icerik += f"""
            <div class="urun">
                <h3>{detay['isim']} - {detay['fiyat']} TL</h3>
                <a class="buton" href="/ekle?id={u_id}">Sepete Ekle</a>
            </div>
            """
            
        # Sepet başlığını açalım
        html_icerik += '<div class="sepet-kutusu"><h2>🛒 Alışveriş Sepetiniz</h2>'
        
        # Sepette ürün var mı kontrol edelim ve hesaplayalım
        if SEPET:
            html_icerik += "<ul>"
            toplam_tutar = 0
            for u_id, adet in SEPET.items():
                urun_detay = URUNLER[u_id]
                ara_toplam = urun_detay['fiyat'] * adet
                toplam_tutar += ara_toplam
                html_icerik += f"<li>{urun_detay['isim']} x {adet} adet = {ara_toplam} TL</li>"
            
            html_icerik += f"</ul><h3>Toplam Ödenecek: <span style='color:green;'>{toplam_tutar} TL</span></h3>"
            html_icerik += '<br><a class="buton" style="background:#dc3545;" href="/temizle">Sepeti Temizle</a>'
        else:
            html_icerik += "<p>Sepetiniz şu anda boş. Yukarıdan ürün ekleyebilirsiniz.</p>"
            
        # HTML'i kapatıyoruz
        html_icerik += "</div></body></html>"
        
        # Oluşturduğumuz HTML metnini internet ağı üzerinden tarayıcıya (byte formatında) gönderiyoruz
        self.wfile.write(html_icerik.encode("utf-8"))

# 3. Sunucuyu yerel bilgisayarımızda (localhost) 8080 portunda başlatıyoruz
def calistir():
    sunucu_adresi = ("", 8080)
    httpd = HTTPServer(sunucu_adresi, EticaretSunucusu)
    print("Sıfırdan e-ticaret siteniz http://localhost:8080 adresinde çalışıyor...")
    httpd.serve_forever()

if __name__ == "__main__":
    calistir()
