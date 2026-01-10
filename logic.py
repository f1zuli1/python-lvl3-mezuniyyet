import sqlite3
import os

# =========================
# Veritabanı yolu
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "qa.db")

# Veritabanına bağlan
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# =========================
# TABLOLARI OLUŞTUR
# =========================

# Departman tablosu
cursor.execute("""
CREATE TABLE IF NOT EXISTS departman (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    departman_adi TEXT NOT NULL UNIQUE
)
""")

# QA tablosu (departman_id ile)
cursor.execute("""
CREATE TABLE IF NOT EXISTS qa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    departman_id INTEGER,
    FOREIGN KEY (departman_id) REFERENCES departman(id)
)
""")

# =========================
# DEPARTMANLAR
# =========================

# Eğer departman yoksa ekle
cursor.execute("SELECT COUNT(*) FROM departman")
if cursor.fetchone()[0] == 0:
    departman_data = [
        ("PROGRAMCILAR",),
        ("PERSONEL",)
    ]
    cursor.executemany(
        "INSERT INTO departman (departman_adi) VALUES (?)",
        departman_data
    )

# =========================
# QA VERİLERİ
# =========================

# Eğer QA tablosu boşsa ekle
cursor.execute("SELECT COUNT(*) FROM qa")
if cursor.fetchone()[0] == 0:
    qa_data = [
        ("Nasıl alışveriş yapabilirim?",
         "🛒 Alışveriş yapmak çok kolay! Ürünü sepete ekle ve satın al.", 2),
        ("Siparişimin durumunu nasıl öğrenebilirim?",
         "📦 Hesabına giriş yap ve Siparişlerim bölümünü kontrol et.", 2),
        ("Bir siparişi nasıl iptal edebilirim?",
         "❌ Müşteri hizmetleri ile hemen iletişime geç.", 2),
        ("Siparişim hasarlı gelirse ne yapmalıyım?",
         "⚠️ Hasarın fotoğrafını çekip bize gönder.", 2),
        ("Teknik destekle nasıl iletişime geçebilirim?",
         "☎️ Telefon veya chat üzerinden teknik destek alabilirsin.", 1),
        ("Ödeme sırasında teslimat yöntemini değiştirebilir miyim?",
         "💳 Ödeme ekranında teslimat yöntemini değiştirebilirsin.", 1)
    ]
    cursor.executemany(
        "INSERT INTO qa (question, answer, departman_id) VALUES (?, ?, ?)",
        qa_data
    )

# =========================
# Kaydet ve kapat
# =========================
conn.commit()
conn.close()

print("✅ Veritabanı başarıyla oluşturuldu ve dolduruldu.")
