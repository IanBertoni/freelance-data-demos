"""Configuración central. Lo que cambia entre entornos vive en .env."""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

# --- Rutas ---
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
OUTPUT_DIR = DATA_DIR / "output"
REPORTS_DIR = ROOT / "reports"
LOGS_DIR = ROOT / "logs"
DB_PATH = DATA_DIR / "prices.db"
for _d in (RAW_DIR, CLEAN_DIR, OUTPUT_DIR, REPORTS_DIR, LOGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --- Fuente de la demo (sitio creado para practicar scraping) ---
SOURCE_NAME = "Books to Scrape"
SOURCE_START_URL = "https://books.toscrape.com/catalogue/page-1.html"
USER_AGENT = "Mozilla/5.0 (compatible; PortfolioDemoBot/1.0)"
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.5"))

# --- LLM vía proxy LiteLLM ---
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:4000/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-local-1234")
LLM_MODEL = os.getenv("LLM_MODEL", "groq-qwen")

# --- Demo 3: umbrales ---
ALERT_PCT = float(os.getenv("ALERT_PCT", "10"))     # cambios >= este % son severidad HIGH
MIN_PCT = float(os.getenv("MIN_PCT_CHANGE", "0.5"))  # cambios menores se ignoran (ruido)

# --- Logging a consola y archivo ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOGS_DIR / "app.log", encoding="utf-8")],
)
log = logging.getLogger("demos")