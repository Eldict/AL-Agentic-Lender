# Makes a SYNTHETIC (fake) housing dataset and trains the valuation model.
# python train_valuation.py                      -> fake data
# python train_valuation.py --data data/real.csv -> real data

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_percentage_error, r2_score
from sklearn.model_selection import train_test_split

from al_ai import valuation_model as vm

DATA_PATH = "data/synthetic_housing.csv"
ROWS = 2000
SEED = 42

# made-up euro per m2 by county
COUNTY_PRICE_M2 = {
    "Dublin": 5600, "Wicklow": 4300, "Kildare": 3800, "Meath": 3500, "Cork": 3600,
    "Galway": 3500, "Louth": 3100, "Limerick": 2900, "Kilkenny": 3000, "Waterford": 2800,
    "Wexford": 2700, "Kerry": 2700, "Clare": 2600, "Westmeath": 2500, "Tipperary": 2300,
    "Sligo": 2200, "Mayo": 2100, "Donegal": 1900, "Roscommon": 1800, "Leitrim": 1600,
}
# how many rows per county (Dublin and Cork get the most)
COUNTY_WEIGHT = {"Dublin": 8, "Cork": 4, "Galway": 2.5, "Kildare": 2.5, "Meath": 2, "Wicklow": 1.5,
                 "Limerick": 2, "Louth": 1.5}
TYPE_MULT = {"detached": 1.10, "semi-detached": 1.00, "terraced": 0.95, "apartment": 1.05}
TYPE_AREA = {"detached": (165, 40), "semi-detached": (115, 20), "terraced": (95, 18), "apartment": (70, 15)}


def ber_effect(rating: str) -> float:
    letter = rating[0]
    return {"A": 1.08, "B": 1.04, "C": 1.00, "D": 0.96, "E": 0.93, "F": 0.90, "G": 0.88}[letter]


def age_effect(year: int) -> float:
    if year >= 2015:
        return 1.06
    if year < 1940:
        return 1.02           # period homes hold value
    if 1950 <= year < 1990:
        return 0.95
    return 1.0


def generate_synthetic(rows: int = ROWS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    counties = list(COUNTY_PRICE_M2)
    weights = np.array([COUNTY_WEIGHT.get(c, 1.0) for c in counties])
    records = []
    for _ in range(rows):
        county = rng.choice(counties, p=weights / weights.sum())
        ptype = rng.choice(list(TYPE_MULT), p=[0.25, 0.35, 0.22, 0.18])
        mean_area, sd_area = TYPE_AREA[ptype]
        area = float(np.clip(rng.normal(mean_area, sd_area), 35, 350).round())
        bedrooms = int(np.clip(round(area / 35 + rng.normal(0, 0.6)), 1, 6))
        bathrooms = int(np.clip(round(bedrooms * 0.6 + rng.normal(0, 0.5)), 1, 4))
        year = int(rng.choice([rng.integers(1890, 1940), rng.integers(1940, 2000), rng.integers(2000, 2026)],
                              p=[0.12, 0.5, 0.38]))
        # newer homes get better BERs
        ber_idx = int(np.clip(rng.normal(3 if year >= 2015 else 8 if year >= 1990 else 11, 2), 0, 14))
        ber = vm.BER_ORDER[ber_idx]
        price = (COUNTY_PRICE_M2[county] * area * TYPE_MULT[ptype] * ber_effect(ber) * age_effect(year)
                 * (1 + 0.02 * (bathrooms - 1)) * rng.lognormal(0, 0.08))
        records.append({"property_type": ptype, "floor_area_m2": area, "bedrooms": bedrooms,
                        "bathrooms": bathrooms, "year_built": year, "ber_rating": ber,
                        "county": county, "price": round(price, -3), "source": "SYNTHETIC"})
    return pd.DataFrame(records)


def main() -> None:
    with open("config.yaml", encoding="utf-8") as f:
        model_path = yaml.safe_load(f)["valuation"]["model_path"]

    parser = argparse.ArgumentParser(description="Train the valuation model.")
    parser.add_argument("--data", help="train on this real dataset instead of generating synthetic data")
    args = parser.parse_args()

    if args.data:
        path, synthetic = args.data, False
    else:
        path, synthetic = DATA_PATH, True
        df = generate_synthetic()
        df.to_csv(path, index=False)
        print(f"Wrote {len(df)} SYNTHETIC rows to {path}")

    data = vm.load_dataset(path)
    X, y = data[vm.FEATURES], data["price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED)
    model = vm.build_pipeline().fit(X_train, y_train)

    pred = model.predict(X_test)
    metrics = {"r2": round(r2_score(y_test, pred), 3),
               "mape": round(mean_absolute_percentage_error(y_test, pred), 3),
               "test_rows": len(X_test)}
    print(f"Hold-out R2 = {metrics['r2']}, mean abs % error = {metrics['mape']:.1%}")

    vm.save(vm.build_pipeline().fit(X, y), model_path,
            {"dataset": path, "synthetic": synthetic, "rows": len(data),
             "counties": sorted(data["county"].unique()),
             "property_types": sorted(data["property_type"].unique()),
             "algorithm": "GradientBoostingRegressor (log price)", "holdout_metrics": metrics})
    print(f"Saved model to {model_path}")


if __name__ == "__main__":
    main()
