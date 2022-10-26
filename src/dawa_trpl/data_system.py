import functools
import os
import typing as t
from collections import abc

import numpy as np
import tlab_analysis.photo_luminescence as pl

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
def load_pldata(filepath: str) -> pl.Data:
    return pl.read_img(filepath)


@functools.lru_cache(maxsize=32)
def load_time_resolved(
    filepath: str, normalize_intensity: bool = False
) -> pl.TimeResolved:
    data = load_pldata(filepath)
    tr = data.resolve_along_time()
    if normalize_intensity:
        tr.df["intensity"] /= tr.df["intensity"].max()
    tr.df["name"] = os.path.basename(filepath)
    return tr


def load_time_resolveds(
    filepaths: abc.Iterable[str],
    normalize_intensity: bool = False,
) -> list[pl.TimeResolved]:
    load = functools.partial(
        load_time_resolved, normalize_intensity=normalize_intensity
    )
    return list(map(load, filepaths))


@functools.lru_cache(maxsize=32)
def load_wavelength_resolved(
    filepath: str,
    wavelength_range: tuple[float, float] | None = None,
    fitting: bool = False,
    normalize_intensity: bool = False,
) -> pl.WavelengthResolved:
    data = load_pldata(filepath)
    wr = data.resolve_along_wavelength(wavelength_range)
    wr.df["fit"] = np.nan
    wr.df["name"] = os.path.basename(filepath)
    if fitting:
        _fit_to_wavelength_resolved(wr)
    if normalize_intensity:
        max_intensity = wr.df["intensity"].max()
        wr.df["intensity"] /= max_intensity
        wr.df["fit"] /= max_intensity
    return wr


def _double_exponential(
    time: float, a: float, tau1: float, b: float, tau2: float
) -> t.Any:
    return a * np.exp(-time / tau1) + b * np.exp(-time / tau2)


def _fit_to_wavelength_resolved(wr: pl.WavelengthResolved) -> pl.WavelengthResolved:
    max_intensity = wr.df["intensity"].max()
    wr.df["intensity"] /= max_intensity
    params, cov = wr.fit(_double_exponential, bounds=(0.0, np.inf))  # type: ignore
    fast, slow = sorted((params[:2], params[2:]), key=lambda x: x[1])  # type: ignore
    a = int(fast[0] / (fast[0] + slow[0]) * 100)
    wr.df.attrs["fit"] = {
        "a": a,
        "tau1": fast[1],
        "b": 100 - a,
        "tau2": slow[1],
        "params": params,
        "cov": cov,
    }
    wr.df["intensity"] *= max_intensity
    wr.df["fit"] *= max_intensity
    return wr


def load_wavelength_resolveds(
    filepaths: abc.Iterable[str],
    wavelength_range: tuple[float, float] | None = None,
    fitting: bool = False,
    normalize_intensity: bool = False,
) -> list[pl.WavelengthResolved]:
    load = functools.partial(
        load_wavelength_resolved,
        wavelength_range=wavelength_range,
        fitting=fitting,
        normalize_intensity=normalize_intensity,
    )
    return list(map(load, filepaths))
