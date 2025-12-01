#!/bin/bash

# Run Ingestion (idempotent) using Conda env
conda run -n turbotp python src/tools/ingest.py

# Run Streamlit App using Conda env
conda run -n turbotp streamlit run main.py
