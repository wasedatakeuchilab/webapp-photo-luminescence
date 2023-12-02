import functools
import os
import typing as t
from collections import abc

import numpy as np
import pandas as pd
from tlab_analysis import trpl, utils

from dawa_trpl import config


def validate_upload_dir(upload_dir: str | None) -> str:
    if upload_dir is None:
        raise ValueError("The upload directory must not be None.")
    if not upload_dir.startswith(config.UPLOAD_BASEDIR):
        raise ValueError("Invalid directory as a upload directory")
    return upload_dir


def get_item_filepath(item_name: str, upload_dir: str) -> str | None:
    filepath = os.path.join(upload_dir, item_name)
    return filepath if os.path.exists(filepath) else None


def get_item_filepaths(
    item_names: abc.Iterable[str],
    upload_dir: str,
) -> list[str | None]:
    _get_item_filepath = functools.partial(get_item_filepath, upload_dir=upload_dir)
    return list(map(_get_item_filepath, item_names))


def get_existing_item_filepaths(
    item_names: abc.Iterable[str],
    upload_dir: str,
) -> list[str]:
    return [
        path for path in get_item_filepaths(item_names, upload_dir) if path is not None
    ]


@functools.lru_cache(maxsize=32)
def load_trpl_data(filepath: str) -> trpl.TRPLData:
    return trpl.read_file(filepath)


@functools.lru_cache(maxsize=32)
def load_wavelength_df(
    filepath: str, normalize_intensity: bool = False
) -> pd.DataFrame:
    data = load_trpl_data(filepath)
    df = data.aggregate_along_time()
    df.attrs["filename"] = os.path.basename(filepath)
    if normalize_intensity:
        max_intensity = df["intensity"].max()
        df["intensity"] /= max_intensity
    return df


def load_wavelength_dfs(
    filepaths: abc.Iterable[str],
    normalize_intensity: bool = False,
) -> list[pd.DataFrame]:
    load = functools.partial(
        load_wavelength_df, normalize_intensity=normalize_intensity
    )
    return list(map(load, filepaths))


@functools.lru_cache(maxsize=32)
def load_time_df(
    filepath: str,
    wavelength_range: tuple[float, float] | None = None,
    fitting: bool = False,
    normalize_intensity: bool = False,
) -> pd.DataFrame:
    data = load_trpl_data(filepath)
    df = data.aggregate_along_wavelength(wavelength_range)
    df["fit"] = np.nan
    df.attrs["filename"] = os.path.basename(filepath)
    if fitting:
        max_intensity = df["intensity"].max()
        fit = df["time"].between(
            *utils.determine_fit_range_dc(
                df["time"].to_list(),
                df["intensity"].to_list(),
            ),
        )
        params, cov = utils.curve_fit(
            _double_exponential,
            xdata=df["time"][fit].to_list(),
            ydata=df["intensity"][fit].to_list() / max_intensity,
            bounds=(0.0, np.inf),
        )
        fast, slow = sorted((params[:2], params[2:]), key=lambda x: 1 / x[1])
        a = int(fast[0] / (fast[0] + slow[0]) * 100)
        df.attrs["fit"] = {
            "a": a,
            "tau1": fast[1],
            "b": 100 - a,
            "tau2": slow[1],
            "params": params,
            "cov": cov,
        }
        df["fit"] = _double_exponential(df["time"][fit], *params) * max_intensity  # type: ignore[arg-type]
    if normalize_intensity:
        max_intensity = df["intensity"].max()
        df["intensity"] /= max_intensity
        df["fit"] /= max_intensity
    return df


def _double_exponential(
    time: float, a: float, tau1: float, b: float, tau2: float
) -> t.Any:
    return a * np.exp(-time / tau1) + b * np.exp(-time / tau2)


def load_time_dfs(
    filepaths: abc.Iterable[str],
    wavelength_range: tuple[float, float] | None = None,
    fitting: bool = False,
    normalize_intensity: bool = False,
) -> list[pd.DataFrame]:
    load = functools.partial(
        load_time_df,
        wavelength_range=wavelength_range,
        fitting=fitting,
        normalize_intensity=normalize_intensity,
    )
    return list(map(load, filepaths))
