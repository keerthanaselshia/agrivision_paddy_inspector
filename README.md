# 🌿 AgriVision Paddy Inspector

> **Scan. Detect. Protect your paddy.**  
> An edge-first, offline-capable smart agriculture inspection system for automated paddy foliar disease detection, lesion severity quantification, and field diagnostics.

---

## 📌 Key Highlights

- **Edge AI Classifier:** Fully INT8-quantized MobileNetV2 (`paddy_int8.tflite`) capable of sub-50ms inference on Raspberry Pi and laptops without GPU or internet.
- **Lesion Severity Quantification:** Classical OpenCV HSV color-space segmentation calculating exact diseased leaf area (%), benchmarked against the **IRRI Standard Evaluation System (SES 0–9)**.
- **Bilingual Interface:** Instant toggle between **English** and **Tamil (தமிழ்)** across all primary workflows.
- **In-Field Dataset Collection Mode:** Standardized camera & uploader pipeline generating `F<field>_P<plant>_<class>_<number>.jpg` with persistent metadata tracking.
- **Severity Validation Helper:** Visual scatter plots with 1:1 concordance lines, regression trends, Pearson $r$, Spearman $\rho$, MAE, RMSE, and systematic bias metrics.
- **Offline Telegram Dispatcher:** SQLite-backed queue storing inspection alerts during offline field walks, automatically syncing via `Sync now` once cellular service is restored.
- **Geospatial & Historical Mapping:** Interactive dark-mode Folium map with severity-proportional markers, disease heatmap layers, and scans-per-week trend charts.

---

## 🗂️ System Architecture & Directory Structure

```
paddy_dataset/
├── app/
│   ├── app.py                     # Main Streamlit UI entry point
│   ├── history_db.py              # Thread-safe SQLite singleton (Schema v3)
│   ├── history_dashboard.py       # Full history log, thumbnail grid, and HTML report export
│   ├── disease_library.py         # Comprehensive symptoms, conditions, and management guide
│   ├── map_page.py                # Geospatial Folium disease map & timeline charts
│   ├── field_collection.py        # In-field dataset logger with auto-naming & counters
│   ├── severity_validation.py     # IRRI SES benchmarking & statistical correlation helper
│   ├── validation_db.py           # SQLite persistence for severity benchmark pairs
│   ├── telegram_queue.py          # Resilient Telegram client with SQLite offline queue
│   ├── about_page.py              # Architecture, hardware guide, and diagnostics
│   ├── paddy_int8.tflite          # Quantized INT8 deep learning model
│   ├── labels.txt                 # Class labels: blast, blb, brown_spot, healthy, other
│   ├── core/
│   │   ├── classifier.py          # TFLite interpreter wrapper and inference logic
│   │   ├── severity.py            # HSV mask and severity grading logic
│   │   ├── advisory.py            # TNAU advisory loader
│   │   ├── quality.py             # Blur, brightness, overexposure, and leaf area checks
│   │   ├── scan_effect.py         # Pure HTML/CSS green laser scanning animation
│   │   ├── strings.py             # Bilingual localization dictionary (EN & TA)
│   │   ├── theme.py               # Dark "smart agriculture" theme styling
│   │   └── reports.py             # Formatted inspection summary builder
│   └── data/
│       └── advisory.json          # Curated disease management data (EN + TA)
├── collected_data/                # Field collection storage (images & metadata.csv)
├── history/images/                # Full-resolution saved inspection photos
├── tests/
│   └── test_pipeline.py           # Comprehensive automated unit & pipeline tests
├── requirements_pi.txt            # ARM64/Raspberry Pi optimized dependencies
└── README.md                      # Complete system documentation
```

---

## 🚀 Getting Started (Windows / PC)

### 1. Prerequisites
- Python 3.10 – 3.12
- Virtual environment (e.g. `venv2`)

### 2. Launch the Application
```powershell
cd C:\Users\keert\paddy_dataset
venv2\Scripts\python.exe -m streamlit run app\app.py
```

Open your browser to `http://localhost:8501`.

---

## 🍓 Edge Deployment on Raspberry Pi (Pi 4 / Pi 5)

### 1. OS Setup
Install **Raspberry Pi OS (64-bit)** on a Class 10 / UHS-I microSD card or NVMe SSD.

### 2. Install System Packages & Virtual Environment
```bash
sudo apt update && sudo apt install -y python3-venv python3-pip libgl1 libglib2.0-0
python3 -m venv ~/agrivision_env
source ~/agrivision_env/bin/activate
```

### 3. Install Optimized Requirements
```bash
pip install -r requirements_pi.txt
```

### 4. Run Headless or with Field Display
```bash
streamlit run app/app.py --server.port 8501 --server.headless true
```
Connect via any smartphone or tablet on the same Wi-Fi hotspot by opening `http://<pi-ip-address>:8501`.

---

## 🧪 Running Automated Tests

Run the full automated test suite verifying classification, severity calculation, database operations, localization, and quality checks:

```powershell
venv2\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

---

## 📜 Scientific Citation & Agricultural Disclaimer

- **Evaluation Standard:** Visual scores benchmarked against the *IRRI Standard Evaluation System for Rice (SES)*, 5th Edition.
- **Disease Management:** Management guidelines are structured in alignment with Tamil Nadu Agricultural University (TNAU) Agritech Portal and ICAR-NRRI protocols.
- **Disclaimer:** AgriVision is a decision-support and preliminary screening tool. Chemical dosages and intervention thresholds must be verified by local government agricultural officers or university extension specialists.
