import os
import time
import logging
import schedule
import pandas as pd
import yfinance as yf
from datetime import datetime

# Configuración de logs
LOG_FILE = "bap_stock.log"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])


def fetch_bap_data():
    """Descarga los datos de la acción BAP y los guarda en un CSV."""
    logging.info("Descargando datos de BAP...")
    try:
        stock = yf.Ticker("BAP")
        data = stock.history(period="1d", interval="1h")
        data.reset_index(inplace=True)

        # Crear carpeta si no existe
        if not os.path.exists("data"):
            os.makedirs("data")

        file_path = "data/bap_stock_data.csv"

        if os.path.exists(file_path):
            data.to_csv(file_path, mode='a', header=False, index=False)
        else:
            data.to_csv(file_path, index=False)

        logging.info(f"Datos guardados en {file_path}")
    except Exception as e:
        logging.error(f"Error al obtener datos de BAP: {e}")


# Programar ejecución cada 2 horas, pero solo 4 veces
execution_count = 0


def limited_execution():
    global execution_count
    if execution_count < 4:
        fetch_bap_data()
        execution_count += 1
    else:
        logging.info("Se completaron las 4 ejecuciones. Finalizando programa.")
        return schedule.CancelJob


schedule.every(2).hours.do(limited_execution)

logging.info("Iniciando programa para descargar datos de BAP")

while execution_count < 4:
    schedule.run_pending()
    time.sleep(60)


