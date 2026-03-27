# Property Scoring API — Gif-sur-Yvette (CentraleSupélec)

## Overview

This project is a simple decision-support tool designed for students or professors looking to buy a property near CentraleSupélec (Gif-sur-Yvette).

The objective is straightforward:

Evaluate whether a property price is coherent with the local market and its proximity to the campus.

The API combines:
- a market-based estimation using DVF real estate transactions
- a location score based on distance to CentraleSupélec

---

## Data

The model is trained on DVF (Demande de Valeur Foncière) data, which contains real estate transactions in France.

Filtering applied:
- Location: Gif-sur-Yvette
- Property type: Apartments only
- Recent transactions (to reflect current market conditions)
- Cleaning: removal of missing or unrealistic values

Variables used:
- valeur_fonciere (price)
- surface_reelle_bati (surface)
- nombre_pieces_principales (rooms)

---

## Method

The model follows a simple and interpretable approach.

### Training (offline)

A regression model is trained on DVF data:

log(price) = b0 + b1 * log(surface) + b2 * rooms

- The model is calibrated using historical transactions
- Parameters and variability (sigma) are saved in:

artifacts/model.json

### Inference (API)

- The API loads the trained model
- Computes an expected price
- Compares it to the user input
- Adds a distance-based score to CentraleSupélec

---

## API Output

The /score endpoint returns:

- expected_price: estimated market price
- price_ratio: price / expected_price
- market_label: underpriced / fair / overpriced
- market_score: closeness to expected price
- distance_to_campus_km
- distance_score
- final_score: weighted combination of market + distance

---

## Project Structure

app/
  main.py        # FastAPI endpoints
  scoring.py     # inference logic

artifacts/
  model.json     # trained model (committed)

train_model.py   # training script (offline)

data/            # DVF dataset (not committed)

---

## Installation & Run

1. Create environment

python -m venv .venv
source .venv/bin/activate

2. Install dependencies

pip install -r requirements.txt

3. Train the model

python train_model.py

4. Run the API

uvicorn app.main:app --reload

---

## Usage

Open:

http://127.0.0.1:8000/docs

Test /score with:

- price
- surface
- rooms
- latitude
- longitude

---

## Notes

- No database is used (stateless API)
- The dataset is not included in the repository
- The model is stored as a lightweight artifact (model.json)
- Coordinates are used instead of addresses for simplicity

---

## Author

Project developed as a practical MLOps exercise focused on building a simple and interpretable real estate scoring API.