"""
Backend FastAPI para BVL - Versión Mejorada
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import List, Dict
import uvicorn
import os
from typing import List, Dict, Any

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BVL-Backend")

# Rutas posibles al CSV (en orden de prioridad)
POSSIBLE_CSV_PATHS = [
    # Ruta relativa desde el backend
    Path(__file__).parent.parent.parent / "Scraper" / "src" / "data" / "bvl_data.csv",
    # Ruta absoluta específica (tu caso)
    Path(r"E:\papx\end_to_end_ml\nb_pr\scraping-bvl\Scraper\src\data\bvl_data.csv"),
    # Otra posible estructura
    Path(__file__).parent.parent / "Scraper" / "src" / "data" / "bvl_data.csv"
]


def find_csv_file():
    """Busca el archivo CSV en las ubicaciones posibles"""
    for path in POSSIBLE_CSV_PATHS:
        if path.exists():
            logger.info(f"CSV encontrado en: {path}")
            return path

    # Si no se encuentra, mostrar todas las rutas probadas
    error_msg = "No se encontró el archivo CSV. Se buscó en:\n"
    error_msg += "\n".join(f"- {str(path)}" for path in POSSIBLE_CSV_PATHS)
    error_msg += "\n\nSolución: Coloque el archivo bvl_data.csv en una de estas ubicaciones"
    raise FileNotFoundError(error_msg)


# Inicialización de FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class CSVDataLoader:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.df = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """Carga los datos del CSV con validación"""
        try:
            df = pd.read_csv(
                self.csv_path,
                parse_dates=["timestamp"],
                encoding="utf-8-sig"
            )

            # Validar columnas requeridas
            required_columns = {"companyName", "last", "timestamp"}
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Faltan columnas requeridas: {missing}")

            df["companyName"] = df["companyName"].str.strip().str.upper()
            return df.sort_values("timestamp")

        except Exception as e:
            logger.error(f"Error cargando CSV: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error procesando el archivo CSV. Verifique el formato: {str(e)}"
            )


# Intenta encontrar y cargar el CSV
try:
    CSV_PATH = find_csv_file()
    data_loader = CSVDataLoader(CSV_PATH)
except Exception as e:
    logger.critical(str(e))


    # Crea una versión mínima funcional sin datos
    class EmptyDataLoader:
        df = pd.DataFrame(columns=["companyName", "last", "timestamp"])


    data_loader = EmptyDataLoader()


# Endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "running",
        "csv_path": str(CSV_PATH) if 'CSV_PATH' in globals() else "No configurado",
        "data_loaded": not data_loader.df.empty,
        "details": "El backend está funcionando pero sin datos" if data_loader.df.empty else "Datos cargados correctamente"
    }


@app.get("/api/companies", response_model=List[str])
async def get_companies():
    if data_loader.df.empty:
        raise HTTPException(
            status_code=503,
            detail="Servicio no disponible. No se encontraron datos. Verifique el archivo CSV."
        )
    return data_loader.df["companyName"].unique().tolist()


@app.get("/api/credicorp", response_model=Dict[str, Any])
async def get_credicorp_data():
    """
    Devuelve todos los datos disponibles para Credicorp Ltd.
    Estructura de respuesta:
    {
        "realtime": {datos más recientes},
        "historical": [lista de datos históricos]
    }
    """
    try:
        # Filtrar datos de Credicorp
        credicorp_data = data_loader.df[
            data_loader.df["companyName"] == "CREDICORP LTD."
        ]

        if credicorp_data.empty:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron datos para CREDICORP LTD."
            )

        # Obtener el último registro
        latest = credicorp_data.iloc[-1].to_dict()

        # Preparar datos en tiempo real
        realtime_data = {
            "price": float(latest["last"]),
            "variation": float(latest.get("percentageChange", 0)),
            "volume": float(latest.get("negotiatedQuantity", 0)),
            "timestamp": datetime.timestamp(latest["timestamp"])  # Convert to numeric timestamp
        }

        # Preparar datos históricos (últimos 30 días)
        cutoff_date = datetime.now() - timedelta(days=30)
        historical = credicorp_data[
            credicorp_data["timestamp"] >= cutoff_date
        ].sort_values("timestamp", ascending=False)

        historical_data = [
            {
                "price": float(row["last"]) if pd.notna(row["last"]) else None,
                "variation": float(row.get("percentageChange", 0)) if pd.notna(row.get("percentageChange", 0)) else None,
                "volume": float(row.get("negotiatedQuantity", 0)) if pd.notna(row.get("negotiatedQuantity", 0)) else None,
                "timestamp": datetime.timestamp(row["timestamp"])  # Convert to numeric timestamp
            }
            for _, row in historical.iterrows()
        ]

        # Filter out None values from historical data
        historical_data = [item for item in historical_data if all(value is not None for value in item.values())]

        return {
            "realtime": realtime_data,
            "historical": historical_data,
            "metadata": {
                "data_points": len(historical_data),
                "time_range": {
                    "from": datetime.timestamp(historical["timestamp"].min()),
                    "to": datetime.timestamp(historical["timestamp"].max())
                }
            }
        }

    except Exception as e:
        logger.error(f"Error obteniendo datos de Credicorp: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando datos de Credicorp: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )