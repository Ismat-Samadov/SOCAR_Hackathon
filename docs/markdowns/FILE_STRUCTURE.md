# SOCAR Hackathon - Project File Structure

**Complete directory tree of the SOCAR Historical Documents AI System**

> **Last Updated**: December 14, 2025
> **Total Files**: 153
> **Total Directories**: 30

---

## Directory Tree

```
SOCAR_Hackathon/
├── app/                                    # FastAPI Application
│   ├── static/                            # Frontend Static Assets
│   │   ├── css/
│   │   │   └── style.css                  # Main stylesheet
│   │   ├── favicon/                       # App icons (PWA ready)
│   │   │   ├── README.txt
│   │   │   ├── apple-touch-icon.png
│   │   │   ├── favicon.ico
│   │   │   ├── icon-192-maskable.png
│   │   │   ├── icon-192.png
│   │   │   ├── icon-512-maskable.png
│   │   │   └── icon-512.png
│   │   └── js/
│   │       └── app.js                     # Frontend JavaScript
│   ├── templates/
│   │   └── index.html                     # Web UI template
│   ├── __init__.py                        # Package marker
│   ├── main.py                            # FastAPI app & endpoints
│   └── requirements.txt                   # Python dependencies

├── certbot/                               # SSL certificate automation (Let's Encrypt)
│   └── www/

├── charts/                                # Generated benchmark visualizations
│   ├── llm_metrics_breakdown.png         # LLM performance breakdown
│   ├── llm_overview_dashboard.png        # 4-panel dashboard
│   ├── llm_quality_comparison.png        # Quality score comparison
│   ├── llm_radar_profile.png             # Multi-dimensional profile
│   └── llm_response_time.png             # Response time analysis

├── data/                                  # Data storage & processing
│   ├── ai_track_data/                    # HuggingFace dataset (SOCARAI/ai_track_data)
│   │   ├── train/
│   │   │   ├── data-00000-of-00001.arrow
│   │   │   ├── dataset_info.json
│   │   │   └── state.json
│   │   └── dataset_dict.json
│   ├── hackathon_data/                   # 28 SOCAR Historical PDFs (Azerbaijani)
│   │   ├── AKÇ və Bakı Arxipelaqında Sıxılma Tektonikası və Neft-Qaz Sistemləri.pdf
│   │   ├── Abşeron-Kür MQ Alt Horizontları AYMT və Seysmik-Geofizika.pdf
│   │   ├── Abşeronda Torpaq Çirklənməsi Ağır Metallar və Geotermal İnteqrasiya Ramanı Suraxan.pdf
│   │   ├── Abşeron və Şimal-Şərq Azərbaycanda hidrokarbon miqrasiyası inteqrativ model.pdf
│   │   ├── Alp-Himalay çərçivəsində Azərbaycan neft-qaz geodinamikası.pdf
│   │   ├── Azərbaycan Neft-Qaz Sektorunda Ekoloji Risklər və YQA Təhlükəsizliyi.pdf
│   │   ├── Azərbaycanda bitumlu qumlar mineralogiya geokimya və ekoloji idarəetmə.pdf
│   │   ├── Azərbaycanda dağ-mədən metallurgiyası dərin emal və ekoloji optimallaşdırma.pdf
│   │   ├── Azərbaycanın karbohidrogen resursları tarixi və müasir mənimsənmə strategiyaları.pdf
│   │   ├── Cənubi Xəzər Hövzəsi Neo-geologiya və Dərin Kəşfiyyat Paradigması.pdf
│   │   ├── Günəşli və Nizami geofiziki-hidrodinamik nəzarət, petrofizika, urban hidrogeologiya.pdf
│   │   ├── Horizontal Çoxtərəfli və ERD Qazmada Avtomatlaşdırma Təsirləri.pdf
│   │   ├── Həmdəm–Qarabağ İnteqral Geologiya-Geofizika Risklər və Seysmik-Qazma Strategiyası.pdf
│   │   ├── Kür və Cənubi Xəzər Mezokaynozoy litofasial modeli.pdf
│   │   ├── Maykop litofasiyaları və kollektor xüsusiyyətləri Orta Kür, Şamaxı-Qobustan.pdf
│   │   ├── NQR Orta Kürdə Orta Eosen Neft-Qaz Sisteminin Qiymətləndirilməsi.pdf
│   │   ├── Novxanı-Əşrəfi Məhsuldar Qat Rezervuar Potensialı və Sənaye Perspektivləri.pdf
│   │   ├── Orta Kür çökəkliyində Mezozoy Modelləşdirilməsi və Muradxanlı Üst Təbaşir Neftliliyi.pdf
│   │   ├── Palçıq Pilpiləsi Gala layı ehtiyatlarının yenilənmiş qiymətləndirilməsi.pdf
│   │   ├── Pirallahı Tektonostratigrafiyası Kollektorlar və CO2 Saxlanması Perspektivləri.pdf
│   │   ├── Qarabağlıda inteqrasiyalı petrofizik seysmoloji qiymətləndirmə və seysmik dayanıqlıq.pdf
│   │   ├── Qərbi Abşeron Yatağı Geoloji-Geofiziki Modelləşdirmə və İnkişaf Strategiyası.pdf
│   │   ├── Qərbi Abşeron geoloji-tektonika kollektor xüsusiyyətləri və istismar dinamikası.pdf
│   │   ├── Qərbi Abşeronda Pliosen–Miosen seysmo-stratigrafiyası və karbohidrogen sistemi.pdf
│   │   ├── Saatlı‑Göyçay‑Muğan zonasında neft‑qaz miqrasiyası və tələ‑kollektorlar.pdf
│   │   ├── Saatlı–Göyçay–Muğan Mezozoy sonu geodinamikləri və neft-qaz sistemi.pdf
│   │   ├── Şimali Abşeron 1951–1998 seysmik-qravimetrik tədqiqat tektonik model və neft-qaz sistemi.pdf
│   │   └── Yan Sırt rifləri, karbonat platforması və Naxçıvan yeraltı suları.pdf
│   ├── pdfs/                             # Original 28 PDFs (document_00 to document_27)
│   │   ├── document_00.pdf
│   │   ├── document_01.pdf
│   │   ├── document_02.pdf
│   │   ├── ... (25 more files)
│   │   └── document_27.pdf
│   ├── vector_db/                        # ChromaDB local storage (backup)
│   │   ├── 338e7490-2688-4352-90da-5ffd5f57ecc8/
│   │   │   ├── data_level0.bin
│   │   │   ├── header.bin
│   │   │   ├── length.bin
│   │   │   └── link_lists.bin
│   │   └── chroma.sqlite3
│   ├── dataset_info.json                 # HuggingFace dataset metadata
│   └── document_00.md                    # Sample OCR output (markdown)

├── docs/                                  # Comprehensive Documentation
│   ├── markdowns/                        # Technical Documentation
│   │   ├── BENCHMARK_ANALYSIS.md         # OCR & LLM benchmark results
│   │   ├── DEPLOYMENT.md                 # Deployment guide
│   │   ├── HACKATHON_ANALYSIS.md         # Hackathon scoring analysis
│   │   ├── IMPLEMENTATION_SUMMARY.md     # Technical implementation details
│   │   ├── PROJECT_KNOWLEDGE.md          # Project context & decisions
│   │   ├── RAG_OPTIMIZATION_README.md    # RAG pipeline optimization
│   │   ├── SSL_CAA_SETUP.md              # SSL/TLS setup guide
│   │   ├── VLM_OCR_README.md             # OCR benchmark documentation
│   │   └── scripts.md                    # Scripts usage guide
│   ├── Presentation.pdf                  # Hackathon presentation
│   ├── SOCAR Historical Document Processing Challenge_final.pdf
│   ├── Screenshot 2025-12-13 at 09.29.10.png
│   ├── beatbyteai_id_rsa                 # SSH key for VM access
│   ├── context.txt                       # Project context notes
│   ├── sample_answers.json               # Ground truth for evaluation
│   └── sample_questions.json             # Test questions (Azerbaijani)

├── favicon/                               # Root-level favicon (for deployment)
│   ├── README.txt
│   ├── apple-touch-icon.png
│   ├── favicon.ico
│   ├── icon-192-maskable.png
│   ├── icon-192.png
│   ├── icon-512-maskable.png
│   └── icon-512.png

├── nginx/                                 # Nginx reverse proxy config
│   ├── ssl/                              # SSL certificates directory
│   └── nginx.conf                        # Nginx configuration

├── notebooks/                             # Jupyter Notebooks (Benchmarking)
│   ├── llm_benchmark.ipynb               # LLM model comparison (GPT-4.1, Llama, DeepSeek)
│   ├── rag_optimization_benchmark.ipynb  # RAG pipeline optimization
│   ├── requirements.txt                  # Notebook dependencies
│   └── vlm_ocr_benchmark.ipynb           # OCR VLM comparison (87.75% CSR)

├── output/                                # Generated Output & Results
│   ├── ingestion/                        # PDF ingestion logs
│   │   ├── ingestion.log
│   │   ├── parallel_ingestion.log
│   │   └── parallel_ingestion_results.json
│   ├── llm_benchmark/                    # LLM evaluation results
│   │   ├── detailed_results.csv
│   │   └── summary.csv
│   ├── rag_optimization_benchmark/       # RAG optimization results
│   │   ├── component_impacts.csv
│   │   ├── detailed_results.csv
│   │   ├── results.png
│   │   └── summary.csv
│   ├── vlm_ocr_benchmark/                # OCR benchmark results
│   │   ├── detailed_results.csv
│   │   ├── results.png
│   │   ├── results_presentation.png
│   │   ├── slide_1_accuracy.png
│   │   ├── slide_2_speed_vs_accuracy.png
│   │   ├── slide_3_error_rates.png
│   │   ├── slide_4_summary_table.png
│   │   └── slide_5_success_rates.png
│   ├── Screenshot 2025-12-14 at 12.23.09.png
│   ├── Screenshot 2025-12-14 at 12.23.26.png
│   ├── Screenshot 2025-12-14 at 12.23.33.png
│   ├── Screenshot 2025-12-14 at 12.23.38.png
│   ├── Screenshot 2025-12-14 at 12.23.43.png
│   ├── Screenshot 2025-12-14 at 12.23.48.png
│   └── llm-benchmark-charts.jsx          # React chart components (source)

├── presentation/                          # Pitch Deck & Presentation
│   ├── PITCH_DECK.md                     # Markdown source
│   ├── pitch_deck.html                   # HTML presentation
│   ├── pitch_deck.pdf                    # PDF export
│   └── pitch_deck_print.html             # Print-friendly version

├── scripts/                               # Utility Scripts
│   ├── __init__.py                       # Package marker
│   ├── check_pinecone.py                 # Pinecone DB inspection
│   ├── clear_pinecone.py                 # Reset vector database
│   ├── generate_llm_charts.py            # Chart generation (matplotlib)
│   ├── ingest_hackathon_data.py          # Parallel PDF ingestion (4 workers)
│   └── list_azure_models.py              # List available Azure models

├── Dockerfile                             # Multi-stage Docker build
├── README.md                              # Main project documentation
├── docker-compose.prod.yml                # Production Docker Compose
├── docker-compose.yml                     # Development Docker Compose
├── render.yaml                            # Render.com deployment config
└── test_api.py                            # API testing script
```

---

## Key Directories Explained

### `/app` - FastAPI Application
The core API server with OCR and LLM endpoints.

**Key Files**:
- `main.py` (610 lines) - Main application logic
  - OCR endpoint: VLM-based text extraction
  - LLM endpoint: RAG-based Q&A
  - Health monitoring
  - CORS & security middleware
- `requirements.txt` - Production dependencies (FastAPI, PyMuPDF, Pinecone, etc.)

### `/data` - Document Storage
**28 SOCAR Historical PDFs** across two directories:
- `pdfs/` - Original files (document_00 to document_27)
- `hackathon_data/` - Named files (Azerbaijani titles)

**Topics**: Oil & gas exploration, geological surveys, seismic analysis, reservoir engineering, environmental studies.

**Vector Database**:
- **Pinecone Cloud**: 606 vectors @ 1024 dimensions (primary)
- **ChromaDB Local**: Backup storage in `vector_db/`

### `/docs` - Comprehensive Documentation
- **9 markdown files** covering architecture, benchmarks, deployment
- **sample_questions.json**: 5 test questions in Azerbaijani
- **sample_answers.json**: Ground truth for LLM Judge evaluation

### `/notebooks` - Jupyter Benchmarks
**3 comprehensive benchmarks**:
1. `vlm_ocr_benchmark.ipynb` - OCR accuracy (87.75% CSR winner)
2. `llm_benchmark.ipynb` - LLM comparison (Llama-4-Maverick selected)
3. `rag_optimization_benchmark.ipynb` - RAG pipeline tuning (55.67% score)

### `/scripts` - Automation Tools
- `ingest_hackathon_data.py` - Parallel ingestion (4 workers, ThreadPoolExecutor)
- `generate_llm_charts.py` - Matplotlib chart generation (5 charts)
- `check_pinecone.py` - Database inspection & stats

### `/charts` - Visualizations
**5 high-quality PNG charts** (300 DPI):
1. Quality Score Comparison
2. Comprehensive Metrics Breakdown
3. Multi-Dimensional Performance Profile (Radar)
4. Response Time Analysis
5. Complete Overview Dashboard

### `/output` - Benchmark Results
All experimental results in CSV format:
- OCR benchmarks: 3 VLM models tested
- LLM benchmarks: 3 LLM models × 4 configurations
- RAG optimization: 7 different strategies

---

## File Statistics

| Category | Count | Description |
|----------|-------|-------------|
| **Python Files** | 15 | Application code, scripts, notebooks |
| **PDFs** | 56 | 28 original + 28 hackathon_data |
| **PNG Images** | 17 | Charts, screenshots, benchmark results |
| **Markdown Docs** | 11 | Technical documentation |
| **CSV Results** | 8 | Benchmark output data |
| **JSON Files** | 6 | Config, dataset metadata, test data |
| **HTML/CSS/JS** | 5 | Web UI frontend |
| **Docker Files** | 4 | Dockerfile, compose configs |

**Total**: 153 files across 30 directories

---

## Excluded Directories

The following directories are excluded from this tree (development/build artifacts):

- `.venv/` - Python virtual environment
- `.vscode/` - VS Code settings
- `.claude/` - Claude Code configuration
- `__pycache__/` - Python bytecode cache
- `.git/` - Git version control
- `node_modules/` - Node.js dependencies (if any)
- `.DS_Store` - macOS metadata files

---

## Technology Stack by Directory

### `/app` - Backend
- FastAPI 0.109.0
- Uvicorn 0.27.0
- PyMuPDF 1.23.8
- Pillow 10.1.0
- Sentence-Transformers 3.3.1
- Pinecone Client 5.4.2
- Azure OpenAI SDK

### `/notebooks` - Data Science
- Jupyter Lab
- Pandas, NumPy
- Matplotlib, Seaborn
- scikit-learn
- sentence-transformers
- jiwer (WER/CER metrics)

### `/scripts` - Automation
- Python 3.11
- dotenv
- concurrent.futures (ThreadPoolExecutor)
- pathlib

### Infrastructure
- Docker & Docker Compose
- Nginx (reverse proxy)
- Let's Encrypt (SSL)
- ngrok (public tunneling)

---

## Data Flow Through Directories

```
1. PDF Upload → /data/hackathon_data/*.pdf
2. Ingestion → /scripts/ingest_hackathon_data.py
3. Processing → /app/main.py (OCR extraction)
4. Embedding → BAAI/bge-large-en-v1.5 (1024-dim)
5. Storage → Pinecone Cloud + /data/vector_db/ (backup)
6. Query → /app/main.py (RAG endpoint)
7. Results → /output/ingestion/
```

---

## Build & Deployment Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage Python 3.11 container build |
| `docker-compose.yml` | Development orchestration |
| `docker-compose.prod.yml` | Production configuration |
| `render.yaml` | Render.com deployment spec |
| `nginx/nginx.conf` | Reverse proxy configuration |
| `certbot/` | SSL certificate automation |

---

## Quick Navigation

- **Start Here**: `/README.md`
- **API Code**: `/app/main.py`
- **Documentation**: `/docs/markdowns/`
- **Benchmarks**: `/notebooks/`
- **Results**: `/charts/` and `/output/`
- **Deployment**: `Dockerfile`, `docker-compose.yml`
- **Scripts**: `/scripts/`

---

## Related Documentation

- [Main README](../README.md) - Project overview & quick start
- [Implementation Summary](markdowns/IMPLEMENTATION_SUMMARY.md) - Technical details
- [Benchmark Analysis](markdowns/BENCHMARK_ANALYSIS.md) - Performance results
- [Deployment Guide](markdowns/DEPLOYMENT.md) - Production deployment
- [Scripts Guide](markdowns/scripts.md) - Utility scripts usage

---

**Generated with**: `tree -I 'venv|.vscode|.claude|__pycache__|*.pyc|.git|node_modules|.DS_Store' -L 4 --dirsfirst`

**Last Updated**: December 14, 2025
