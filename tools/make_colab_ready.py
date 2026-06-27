#!/usr/bin/env python3
"""Make the workshop notebooks portable between local Jupyter and Google Colab."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "khairuladib94/dl-food-research"
RAW_ROOT = f"https://raw.githubusercontent.com/{REPOSITORY}/main"

NOTEBOOKS = {
    "session-6/notebooks/01_tabular_mlp_shelf_life_tensorflow_keras.ipynb": "tabular_shelf_life.csv",
    "session-6/notebooks/02_image_cnn_fruit_defect_tensorflow_keras.ipynb": "fruit_defect_images.npz",
    "session-6/notebooks/03_spectroscopy_1dcnn_tensorflow_keras.ipynb": "spectra_adulteration.npz",
    "session-6/notebooks/04_timeseries_bilstm_tensorflow_keras.ipynb": "fermentation_timeseries.npz",
    "session-6/notebooks/05_autoencoder_anomaly_tensorflow_keras.ipynb": "anomaly_spectra.npz",
    "session-9/notebooks/01_group1_bakery_shelf_life_mlp.ipynb": "group1_bakery_shelf_life.csv",
    "session-9/notebooks/02_group2_fruit_quality_cnn.ipynb": "group2_fruit_quality_images.npz",
    "session-9/notebooks/03_group3_nir_moisture_1dcnn.ipynb": "group3_nir_moisture.npz",
    "session-9/notebooks/04_group4_fermentation_gru.ipynb": "group4_fermentation_deviation.npz",
    "session-9/notebooks/05_group5_oil_autoencoder.ipynb": "group5_oil_anomaly.npz",
}


def source_text(cell: dict) -> str:
    source = cell.get("source", [])
    return "".join(source) if isinstance(source, list) else source


def source_lines(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def make_badge(notebook_path: str) -> str:
    colab_url = (
        "https://colab.research.google.com/github/"
        f"{REPOSITORY}/blob/main/{notebook_path}"
    )
    return (
        f'<a href="{colab_url}" target="_parent">'
        '<img src="https://colab.research.google.com/assets/colab-badge.svg" '
        'alt="Open in Colab"/></a>\n\n'
        "> **Colab workflow:** Save a copy in Drive, then choose Runtime > Run all. "
        "The required teaching dataset downloads automatically; Google Drive is not mounted.\n\n"
    )


def make_bootstrap(session: str, data_file: str, include_figures: bool) -> str:
    lines = [
        "# Portable workshop data setup: local Jupyter first, Colab fallback.\n",
        f"DATA_FILE = {data_file!r}\n",
        "LOCAL_DATA_DIR = Path('../data')\n",
        "if (LOCAL_DATA_DIR / DATA_FILE).exists():\n",
        "    DATA_DIR = LOCAL_DATA_DIR\n",
        "    IN_COLAB = False\n",
        "else:\n",
        "    from urllib.request import urlretrieve\n",
        "    try:\n",
        "        import google.colab  # type: ignore  # noqa: F401\n",
        "        IN_COLAB = True\n",
        "    except ImportError:\n",
        "        IN_COLAB = False\n",
        "    DATA_DIR = Path('/content/dl-food-research-data') if IN_COLAB else Path.cwd() / '.workshop-data'\n",
        "    DATA_DIR.mkdir(parents=True, exist_ok=True)\n",
        "    target = DATA_DIR / DATA_FILE\n",
        "    if not target.exists():\n",
        f"        url = {RAW_ROOT!r} + '/{session}/data/' + DATA_FILE\n",
        "        print(f'Downloading {DATA_FILE} ...')\n",
        "        urlretrieve(url, target)\n",
        "    print(f'Dataset ready: {target}')\n",
    ]
    if include_figures:
        lines.extend(
            [
                "FIG_DIR = Path('/content/dl-food-research-figures') if IN_COLAB else Path('../figures')\n",
                "FIG_DIR.mkdir(parents=True, exist_ok=True)\n",
            ]
        )
    return "".join(lines)


def update_notebook(relative_path: str, data_file: str) -> None:
    path = ROOT / relative_path
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = notebook["cells"]

    first_markdown = next(cell for cell in cells if cell.get("cell_type") == "markdown")
    text = source_text(first_markdown)
    if "colab.research.google.com/assets/colab-badge.svg" not in text:
        first_markdown["source"] = source_lines(text.rstrip() + "\n\n" + make_badge(relative_path))

    session = relative_path.split("/", 1)[0]
    include_figures = session == "session-9"
    bootstrap = make_bootstrap(session, data_file, include_figures)
    replaced = False

    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        text = source_text(cell)
        if "DATA_DIR = Path('../data')" not in text:
            continue
        text = text.replace("DATA_DIR = Path('../data')\n", bootstrap)
        if include_figures:
            text = text.replace("FIG_DIR = Path('../figures')\nFIG_DIR.mkdir(exist_ok=True)\n", "")
        cell["source"] = source_lines(text)
        replaced = True
        break

    if not replaced and "Portable workshop data setup" not in "".join(
        source_text(cell) for cell in cells
    ):
        raise RuntimeError(f"Could not locate DATA_DIR setup in {relative_path}")

    notebook.setdefault("metadata", {}).setdefault("colab", {})["name"] = path.name
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    for relative_path, data_file in NOTEBOOKS.items():
        update_notebook(relative_path, data_file)
        print(f"Updated {relative_path}")


if __name__ == "__main__":
    main()
