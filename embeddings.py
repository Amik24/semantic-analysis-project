{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyO9cHg2bt/pNcUP1CaAPafW",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/Amik24/semantic-analysis-project/blob/Ikram_notebooks/embeddings.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 1,
      "metadata": {
        "id": "szh9fj8XkAOT"
      },
      "outputs": [],
      "source": [
        "# code/embeddings.py\n",
        "# ---------------------------------------------\n",
        "# Rôle : charger un modèle SBERT et encoder des textes.\n",
        "# Utilisé par recommend.py et scoring.py\n",
        "\n",
        "from typing import List\n",
        "from sentence_transformers import SentenceTransformer\n",
        "\n",
        "# Par défaut on prend le modèle plus costaud (configurable)\n",
        "DEFAULT_MODEL = \"all-mpnet-base-v2\"  # ou \"all-MiniLM-L6-v2\" si besoin de vitesse\n",
        "\n",
        "_model_cache = {}\n",
        "\n",
        "def get_model(name: str = DEFAULT_MODEL) -> SentenceTransformer:\n",
        "    \"\"\"\n",
        "    Charge le modèle SBERT une fois et le met en cache pour réutilisation.\n",
        "    \"\"\"\n",
        "    if name not in _model_cache:\n",
        "        _model_cache[name] = SentenceTransformer(name)\n",
        "    return _model_cache[name]\n",
        "\n",
        "def embed_texts(texts: List[str], model_name: str = DEFAULT_MODEL):\n",
        "    \"\"\"\n",
        "    Encode une liste de textes -> tenseur (n_texts x d).\n",
        "    \"\"\"\n",
        "    model = get_model(model_name)\n",
        "    return model.encode(texts, convert_to_tensor=True)\n"
      ]
    }
  ]
}