# Guideline — Data & AI Portfolio (Streamlit)

Dokumen ini menjelaskan **alur website**, **komponen utama**, dan **fungsi masing-masing bagian** pada project Streamlit ini.

## 1) Cara kerja aplikasi secara umum

- Entry point aplikasi adalah `app.py` (halaman Home).
- Navigasi halaman menggunakan mekanisme **Streamlit multipage** lewat folder `pages/`.
- Beberapa fitur menggunakan **cache** agar ringan di Streamlit Cloud (free tier):
  - `st.cache_data`: caching data (mis. dataset dashboard)
  - `st.cache_resource`: caching resource berat (mis. model ML, koneksi DB)

## 2) Struktur folder & fungsinya

### `app.py` (Home)
- Fungsi: halaman landing untuk ringkasan portofolio dan navigasi cepat ke halaman-halaman utama.

### `pages/` (halaman aplikasi)
Urutan halaman mengikuti nama file:

- `pages/1_Dashboard.py`
  - Fungsi: **Dashboard TikTok** (upload CSV, filter, dan visualisasi performa).
  - Sumber data:
    - Jika `USE_DB=true` → data disimpan & dibaca dari **SQLite** (`data/app.db`).
    - Jika `USE_DB=false` → data hanya dari upload (in-memory), hilang ketika restart.

- `pages/2_ML_Predictor.py`
  - Fungsi: demo prediksi ML yang ringan (CPU-friendly) menggunakan data sintetis.
  - Tujuan: contoh UI *form → prediksi → probabilitas* (bisa diganti model asli).

- `pages/3_Data_Pipeline.py`
  - Fungsi: visualisasi arsitektur pipeline + kartu metadata ETL.
  - Mode storage metadata:
    - Jika `USE_DB=true` → metadata ETL disimpan ke SQLite table `etl_metadata`.
    - Jika `USE_DB=false` → metadata ETL dibaca/ditulis ke `data/metadata.json`.

- `pages/4_AI_Playground.py`
  - Fungsi: text-to-image via **Hugging Face Inference API** (Stable Diffusion).
  - Token diambil dari `st.secrets["HF_TOKEN"]`.
  - Kenapa API: Streamlit Cloud free tier tidak menyediakan GPU, jadi komputasi dilakukan di server Hugging Face.

- `pages/5_Blog.py`
  - Fungsi: render tulisan teknis dari file markdown di folder `posts/`.

- `pages/6_Resume.py`
  - Fungsi: resume ringkas + tombol download PDF dari `assets/resume.pdf`.

### `src/` (logic/shared utilities)
- `src/ui.py`
  - Fungsi: helper UI (page config, header, section).

- `src/data.py`
  - Fungsi: dataset demo sales (masih dipakai sebagai contoh data project, walaupun grafik sales di dashboard sudah dihapus).

- `src/ml.py`
  - Fungsi: model ML ringan (Logistic Regression) + fungsi prediksi untuk halaman ML.

- `src/hf_inference.py`
  - Fungsi: wrapper request ke Hugging Face Inference API + error handling.

- `src/db.py`
  - Fungsi: service database **SQLite**:
    - Table `etl_metadata`: menyimpan snapshot metadata ETL.
    - Table `tiktok_clips`: menyimpan dataset TikTok untuk dashboard.

### `data/`
- `data/metadata.json`: metadata pipeline mode JSON (dipakai kalau `USE_DB=false`).
- `data/sample_tiktok_clips.csv`: contoh dataset TikTok untuk uji cepat.
- `data/sample_sales.csv`: dataset demo sales (dibuat otomatis untuk demo).
- `data/app.db`: file SQLite (akan muncul setelah DB pertama kali dipakai).

### `posts/`
- Berisi markdown blog, contoh: `posts/welcome.md`.

### `assets/`
- Tempat simpan file statis (gambar, icon, dan `resume.pdf`).

### `.streamlit/`
- `config.toml`: tema dan konfigurasi UI Streamlit.
- `secrets.toml` (lokal): tempat menyimpan secret untuk development (jangan commit).
- `secrets.toml.example`: template.

## 3) Konfigurasi secrets (penting)

### File yang benar
Streamlit membaca secrets dari:
- `.streamlit/secrets.toml` (lokal), atau
- Secrets di Streamlit Cloud (App → Settings → Secrets)

Pastikan nama file **`secrets.toml`** (pakai huruf **s**) — bukan `secret.toml`.

### Contoh konfigurasi

```toml
# Database mode (SQLite)
USE_DB = true
DB_PATH = "data/app.db"

# Hugging Face token (untuk AI Playground)
HF_TOKEN = "hf_..."
```

## 4) Alur data TikTok (Dashboard)

### Format CSV yang didukung
Kolom wajib:
- `clip_date`, `views`, `likes`, `comments`, `shares`, `saves`

Kolom opsional:
- `creator`, `topic`, `caption`, `url`

### Flow (jika USE_DB=true)
- User upload CSV / klik “Load sample dataset”
- `pages/1_Dashboard.py` melakukan parsing + normalisasi
- Data disimpan ke SQLite melalui `src/db.py` table `tiktok_clips`
- Dashboard membaca kembali data dari DB untuk ditampilkan

### Flow (jika USE_DB=false)
- User upload CSV
- Data hanya disimpan di memori session Streamlit (akan hilang saat restart)

## 5) Alur metadata pipeline (Data Pipeline page)

- `pages/3_Data_Pipeline.py` menampilkan arsitektur (diagram Mermaid) + metadata cards
- Tombol “Refresh metadata” membuat snapshot metadata baru
  - Jika `USE_DB=true`: snapshot masuk ke table `etl_metadata`
  - Jika `USE_DB=false`: snapshot ditulis ke `data/metadata.json`

## 6) Alur AI Playground (Hugging Face)

- User mengisi prompt
- `pages/4_AI_Playground.py` memanggil `src/hf_inference.py`
- Request dikirim ke endpoint Hugging Face:
  - `https://api-inference.huggingface.co/models/<model>`
- Gambar yang diterima akan ditampilkan di Streamlit

Catatan: Jika token belum diset, halaman akan menampilkan warning.

## 7) Cara menjalankan & troubleshooting singkat

### Run lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Kenapa `data/app.db` belum ada?
File SQLite baru dibuat saat pertama kali diakses. Contoh cara memicu:
- buka halaman **Data Pipeline**, atau
- di **Dashboard TikTok** klik “Load sample dataset” / upload CSV (dengan `USE_DB=true`)

### Cara melihat isi database
- Pakai DB Browser for SQLite / extension SQLite di editor
- Open file `data/app.db`
- Cek tables: `tiktok_clips`, `etl_metadata`
