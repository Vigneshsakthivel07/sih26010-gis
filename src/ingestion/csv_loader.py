from pathlib import Path
import pandas as pd


def load_csv(csv_path):
    """
    Load an already digitized CSV.

    Required columns:
        point_id
        x
        y
    """

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    required_columns = {
        "point_id",
        "x",
        "y",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"CSV is missing columns: {sorted(missing)}"
        )

    return df
