# Machine Learning and Deep Learning for Food Research

Public code and synthetic teaching datasets for the workshop. The recommended
participant workflow is Google Colab; no local Python installation is required.

## Participant entry point

Open the workshop page:

**https://khairuladib94.github.io/dl-food-research/**

Choose a notebook, click **Open in Colab**, save a copy to Google Drive, and use
**Runtime > Run all**. Each notebook downloads only its matching dataset and
does not mount Google Drive.

## Repository layout

- `session-6/`: five guided TensorFlow/Keras case studies and datasets.
- `session-9/`: five group challenge notebooks and datasets.
- `assets/participant-guide.pdf`: two-page Colab quick-start guide.
- `FACILITATOR.md`: delivery, fallback, and pre-workshop checks.
- `tools/make_colab_ready.py`: reproducible notebook portability update.

All supplied datasets are synthetic and intended for teaching. They should not
be used to make real food-quality or food-safety decisions.

## Local fallback

Open a terminal in either session's `notebooks` directory and start Jupyter
there. The notebooks use the adjacent `../data` directory automatically.

## Licence

Code is released under the MIT License. Workshop slide decks remain distributed
separately through Google Drive.
