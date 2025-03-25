from pathlib import Path

# Ruta base del proyecto (automática)
PROJECT_ROOT = Path(__file__).parent.parent

# Rutas importantes (relativas al proyecto)
CSV_PATH = PROJECT_ROOT / "Scraper" / "src" / "data" / "bvl_data.csv"
LOG_DIR = PROJECT_ROOT / "logs"

# Crea carpetas si no existen
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)