import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


CSV_PATH = "data/dvf.csv"
OUT_PATH = "artifacts/model.json"


def train_model(csv_path: str = CSV_PATH, out_path: str = OUT_PATH) -> dict:
    # sep=None lets pandas infer comma vs semicolon
    df = pd.read_csv(csv_path, sep=None, engine="python")

    # Optional filters if columns exist
    if "type_local" in df.columns:
        df["type_local"] = df["type_local"].astype(str)
        df = df[df["type_local"] == "Appartement"]

    if "date_mutation" in df.columns:
        df["date_mutation"] = pd.to_datetime(df["date_mutation"], errors="coerce")
        df = df[df["date_mutation"] >= "2024-01-01"]

    numeric_cols = [
        "valeur_fonciere",
        "surface_reelle_bati",
        "nombre_pieces_principales",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=numeric_cols)

    df = df[df["valeur_fonciere"] > 10000]
    df = df[df["surface_reelle_bati"] > 10]
    df = df[df["nombre_pieces_principales"] > 0]

    if len(df) < 30:
        raise ValueError(f"Not enough rows after filtering: n={len(df)}")

    y = np.log(df["valeur_fonciere"].to_numpy(dtype=float))
    x_surface = np.log(df["surface_reelle_bati"].to_numpy(dtype=float))
    x_rooms = df["nombre_pieces_principales"].to_numpy(dtype=float)

    X = np.column_stack([
        np.ones(len(df)),
        x_surface,
        x_rooms,
    ])

    beta, *_ = np.linalg.lstsq(X, y, rcond=None)

    residuals = y - (X @ beta)
    sigma = float(np.std(residuals, ddof=1))

    model = {
        "intercept": float(beta[0]),
        "coef_log_surface": float(beta[1]),
        "coef_rooms": float(beta[2]),
        "sigma": sigma,
        "n_train": int(len(df)),
    }

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)

    return model


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    model = train_model()
    logger.info("Model saved to artifacts/model.json")
    logger.info("Model parameters: %s", model)