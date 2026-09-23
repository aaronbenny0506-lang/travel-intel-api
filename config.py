"""
Externalized configuration for the Travel Intelligence Tool.

Nothing API-specific lives in travel_intel.py — endpoint, key, and timeout
are all read from the environment (optionally loaded from a local .env file
via python-dotenv, if it's installed). Copy .env.example to .env and fill
in your own values to run the tool.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional — the tool still works if config is set
    # via real environment variables instead of a .env file.
    pass

# REST Countries API (v5). v1-v4 were retired in 2026; v5 requires a free
# API key. See obstacle_log.md for details.
API_BASE_URL = os.getenv("REST_COUNTRIES_BASE_URL", "https://api.restcountries.com/countries/v5")
API_KEY = os.getenv("REST_COUNTRIES_API_KEY", "")
REQUEST_TIMEOUT = float(os.getenv("REST_COUNTRIES_TIMEOUT", "10"))
