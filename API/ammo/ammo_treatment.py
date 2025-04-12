import pandas as pd
from loguru import logger
import os
import numpy as np


def get_csv_ammo() -> pd.DataFrame:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # logger.debug(current_dir)
    ammo = os.path.join(current_dir, "ammo_data.csv")
    ammo_df = pd.read_csv(ammo)

    return ammo_df


def normalize_name(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # mask = ~df['Name'].str.lower().str.contains(df['Manufacturer'].str.lower().str.replace(' ', ''), regex = False, na = False)
    mask = pd.Series(
        [
            mfr not in name
            for mfr, name in zip(df["Manufacturer"].str.lower(), df["Name"].str.lower())
        ],
        index=df.index,
    )

    logger.debug(f" number of names to normalize {sum(mask)}")
    df.loc[mask, "Name"] = df.loc[mask, "Manufacturer"] + " " + df.loc[mask, "Name"]

    return df


def convert_velocity(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Initial Velocity"] = (
        df["Initial Velocity"].astype(str).str.replace(",", "").astype(float)
    )
    mask = df["Velocity Unit"] == "fps"
    df.loc[mask, "Initial Velocity"] = df.loc[mask, "Initial Velocity"] * 0.3048
    df.loc[mask, "Velocity Unit"] = "m/s"

    return df


def convert_mass(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Projectile Weight"] = (
        df["Projectile Weight"].astype(str).str.replace(",", ".").astype(float)
    )
    mask = df["Projectile Weight Unit"] == "g"
    df.loc[mask, "Projectile Weight"] = df.loc[mask, "Projectile Weight"] * 15.432
    df.loc[mask, "Projectile Weight Unit"] = "grains"
    return df


def treat_ammo_data():
    df = get_csv_ammo()

    for col in df.columns:
        df[col] = df[col].str.strip() if df[col].dtype == "object" else df[col]

    # logger.debug(f"\n {df.describe()}")
    df = normalize_name(df)
    df = convert_velocity(df)
    df = convert_mass(df)
    # logger.debug(f"\n {df.describe()}")
    columns_map = {
        "Name": "name",
        "Manufacturer": "manufacturer",
        "Caliber": "caliber",
        "Initial Velocity": "V_0",
        "Velocity Unit": "V_0_unit",
        "Projectile Weight": "weight",
        "Projectile Weight Unit": "weight_unit",
        "Ballistic Coefficient": "CB1",
    }

    df = df.rename(columns=columns_map)
    df = df.replace(np.nan, None)
    df = df.drop_duplicates(["name"])
    return df


if __name__ == "__main__":
    df = treat_ammo_data()
    # logger.debug(f"\n {df.describe()}")
    # logger.debug(df)
