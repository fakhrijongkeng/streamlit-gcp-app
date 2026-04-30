# Dokumentasi Pengembangan Portofolio Data & AI (Streamlit + Hugging Face + Data Pipeline)

## 1. Pengembangan Website Personal (Data Professional)
**Framework Utama:** Streamlit (Python-based)
**Tujuan:** Membangun portofolio teknis yang interaktif untuk peran Data Engineer, Analyst, atau Scientist.

### Fitur Strategis Berdasarkan Peran:
* **Data Analyst:** Dashboard interaktif (Plotly/Altair) dengan filter data dinamis.
* **Data Scientist:** Interface prediksi model ML (input form -> hasil prediksi).
* **Data Engineer:** Visualisasi arsitektur data pipeline, skema ETL, dan status metadata (Last Sync, Rows Processed).
* **Umum:** Integrasi GitHub Stats, Blog teknis (Storytelling), dan Resume interaktif.

---

## 2. Strategi Deployment: Streamlit Cloud
**Platform:** [Streamlit Community Cloud](https://streamlit.io/cloud)
**Alur Kerja:** 1. Push kode Python ke repositori **GitHub**.
2. Hubungkan repositori ke Streamlit Cloud.
3. Aplikasi akan otomatis mengudara dengan URL publik (contoh: `nama-user.streamlit.app`).

**Batasan Penting (Free Tier):**
* **RAM:** Terbatas pada ~1GB - 3GB.
* **Resource:** CPU-only (Tidak ada GPU gratis).
* **Karakteristik:** Ephemeral (Server "tidur" jika tidak ada pengunjung).

---

## 3. Integrasi AI Playground (Stable Diffusion)
Untuk menghindari *crash* akibat keterbatasan RAM dan ketiadaan GPU di Streamlit Cloud, gunakan metode **API Inference**.

### Implementasi Hugging Face Inference API:
1. **Model:** Gunakan model seperti `runwayml/stable-diffusion-v1-5`.
2. **Metode:** Kirim permintaan POST ke endpoint Hugging Face menggunakan library `requests`.
3. **Keuntungan:** Komputasi GPU dilakukan di server Hugging Face, Streamlit hanya berfungsi sebagai UI.

**Contoh Struktur Kode Singkat:**
```python
import requests
import streamlit as st

API_URL = "[https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5](https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5)"
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

prompt = st.text_input("Masukkan Prompt:")
if st.button("Generate"):
    image_bytes = query({"inputs": prompt})
    st.image(image_bytes)