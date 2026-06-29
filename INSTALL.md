# AlterLife Kurulum ve Calistirma Kilavuzu

Bu belge, AlterLife projesini yerel bilgisayarinizda veya Docker uzerinde sorunsuz bir sekilde calistirabilmeniz icin gerekli adimlari icermektedir.

---

## 1. Ortam Degiskenleri (Environment Variables)

Projenin calismasi icin oncelikle gerekli olan `.env` dosyalarini olusturmalisiniz:

### Backend
`backend` klasorune gidin ve `.env.example` dosyasini `.env` olarak kopyalayin:
```bash
cd backend
cp .env.example .env
```

### Frontend
`frontend` klasorune gidin ve `.env.local.example` dosyasini `.env.local` olarak kopyalayin:
```bash
cd frontend
cp .env.local.example .env.local
```

---

## 2. Docker Uzerinde Calistirma (En Kolay Yol)

Eger bilgisayarinizda Docker kurulursa, Python veya Node.js bagimliliklarini manuel kurmaniza gerek kalmadan tum projeyi tek bir komutla baslatabilirsiniz.

Ana dizindeyken (AlterLife) su komutu calistirin:
```bash
docker compose up --build
```

Bu komut:
*   Frontend servisini derler ve **http://localhost:3000** portunda baslatir.
*   Backend servisini derler ve **http://localhost:8000** portunda baslatir.

*Not: Yerel bilgisayarinizda port 3000 veya 8000 baska bir uygulama tarafindan kullaniliyorsa Docker baslatilirken port hatasi alabilirsiniz. Bu durumda yerel calistırma yontemini tercih edebilirsiniz.*

---

## 3. Yerel Bilgisayarda Calistirma

Eger degisiklikleri anlik gormek ve Docker kullanmadan hizli gelistirme yapmak istiyorsaniz asagidaki adimlari takip edin.

### A. Backend Kurulumu (FastAPI)

1. Python 3.12 sürümünün yuklu oldugundan emin olun.
2. `backend` klasorune girip bir sanal ortam (venv) olusturun ve aktif edin:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Bagimliliklari yukleyin:
   ```bash
   pip install -r requirements.txt
   ```
4. Sunucuyu port **8001** uzerinden baslatin:
   ```bash
   uvicorn main:app --reload --port 8001
   ```
   *   Backend API adresi: **http://localhost:8001**
   *   API Dokümantasyonu (Swagger UI): **http://localhost:8001/docs**

---

### B. Frontend Kurulumu (Next.js 15)

1. Node.js (v20+) yuklu oldugundan emin olun.
2. `frontend` klasorune gidin ve bagimliliklari yukleyin:
   ```bash
   cd frontend
   npm install
   ```
3. `.env.local` dosyasindaki backend API adresinin port **8001** olarak ayarlandigini dogrulayin:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8001
   ```
4. Uygulamayi port **3001** uzerinden baslatin:
   ```bash
   npm run dev -- --port 3001
   ```
   *   Frontend Arayuz adresi: **http://localhost:3001**

---

## Proje Sayfalari ve Rotalari

Uygulama calistiktan sonra tarayicinizdan asagidaki rotalara erisebilirsiniz:

| Sayfa | Rota | Aciklama |
|-------|------|----------|
| Giris Ekranı | `/login` | Giris ve kayit paneli |
| Onboarding | `/onboarding` | 5 adimli profil/karakter olusturma akisi |
| Dashboard | `/dashboard` | Karakter durumu, gorevler ve entegrasyonlar |
| Simulasyon | `/simulations` | Karar agaclari ve What-If senaryolari |
| Yetenekler | `/skills` | Yetenek agaci ve seviye takibi |
| Kutuphane | `/library` | Kaydedilen makaleler ve ogrenme kaynaklari |
| Analitik | `/analytics` | Haftalik ritim isi haritasi ve hedefe ulasim grafigi |
| Topluluk | `/community` | Diger kullanicilarin anonim basari hikayeleri |
| Ayarlar | `/settings` | API entegrasyonlari ve profil yonetimi |
