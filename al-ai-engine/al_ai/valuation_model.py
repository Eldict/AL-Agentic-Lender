# House price model (scikit-learn).
# To use real data, only change load_dataset().

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder

NUMERIC = ["floor_area_m2", "bedrooms", "bathrooms", "year_built", "ber_score"]
CATEGORICAL = ["property_type", "county"]
FEATURES = NUMERIC + CATEGORICAL
REQUIRED_PROPERTY_FIELDS = ["property_type", "floor_area_m2", "bedrooms", "bathrooms",
                            "year_built", "ber_rating", "county"]

# Irish BER scale, best to worst
BER_ORDER = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D1", "D2", "E1", "E2", "F", "G"]


# turns a BER into a number: A1 = 15 ... G = 1
def ber_score(rating: str) -> int:
    rating = rating.strip().upper()
    if rating not in BER_ORDER:
        raise ValueError(f"Unknown BER rating: {rating!r}")
    return len(BER_ORDER) - BER_ORDER.index(rating)


# loads the training data (swap this for Daft.ie / Property Price Register data)
def load_dataset(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["ber_score"] = df["ber_rating"].map(ber_score)
    return df[FEATURES + ["price"]]


# numbers pass straight through, text columns become one-hot columns
def build_pipeline() -> TransformedTargetRegressor:
    pre = ColumnTransformer([
        ("num", FunctionTransformer(), NUMERIC),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ])
    model = Pipeline([("pre", pre), ("gbr", GradientBoostingRegressor(n_estimators=300, max_depth=3,
                                                                      learning_rate=0.05, random_state=42))])
    return TransformedTargetRegressor(regressor=model, func=np.log, inverse_func=np.exp)  # learns log(price)


def save(model, path: str | Path, metadata: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "metadata": {**metadata, "sklearn_version": sklearn.__version__,
                                              "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}},
                path)


# returns {"model": ..., "metadata": ...}
def load(path: str | Path) -> dict:
    return joblib.load(path)


def predict_value(bundle: dict, prop: dict) -> float:
    row = {**{k: prop[k] for k in FEATURES if k != "ber_score"}, "ber_score": ber_score(prop["ber_rating"])}
    return float(bundle["model"].predict(pd.DataFrame([row])[FEATURES])[0])
