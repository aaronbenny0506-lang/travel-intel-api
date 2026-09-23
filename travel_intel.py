"""
API-Powered Travel Intelligence Tool
-------------------------------------
Given a country name, pulls its capital, currency, population, languages,
region and neighbouring countries into one clean summary using the
REST Countries API (v5).

Usage:
    python travel_intel.py "India"
    python travel_intel.py            # prompts for a name instead
"""

import sys
import requests

import config


class CountryLookupError(Exception):
    """Raised for any recoverable failure while building a country snapshot
    (unknown country, missing config, bad network, unexpected payload)."""


def _get(url, params, headers, timeout):
    """Thin wrapper around requests.get so network failures raise one
    consistent, tool-specific error type."""
    try:
        return requests.get(url, params=params, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout:
        raise CountryLookupError("The request timed out. Check your connection and try again.")
    except requests.exceptions.ConnectionError:
        raise CountryLookupError("Couldn't reach the REST Countries API. Check your internet connection.")
    except requests.exceptions.RequestException as exc:
        raise CountryLookupError(f"Network error while calling the API: {exc}")


def fetch_country_data(country_name: str) -> dict:
    """Fetch and parse the raw API response for a single country name.

    Returns the first matching country record (a dict) straight from the
    API's data.objects array.
    """
    if not config.API_KEY:
        raise CountryLookupError(
            "No API key configured. Set REST_COUNTRIES_API_KEY in your .env file "
            "(see .env.example)."
        )

    headers = {"Authorization": f"Bearer {config.API_KEY}"}
    params = {"q": country_name, "limit": 1}

    response = _get(config.API_BASE_URL, params, headers, config.REQUEST_TIMEOUT)

    if response.status_code == 401:
        raise CountryLookupError("API key was rejected (401). Double-check REST_COUNTRIES_API_KEY.")
    if response.status_code == 429:
        raise CountryLookupError("Rate limit hit (429). Wait a bit before trying again.")
    if response.status_code >= 500:
        raise CountryLookupError(f"REST Countries API is having issues (HTTP {response.status_code}).")
    if response.status_code != 200:
        raise CountryLookupError(f"Unexpected response (HTTP {response.status_code}).")

    try:
        payload = response.json()
    except ValueError:
        raise CountryLookupError("API did not return valid JSON — the response may have changed shape.")

    try:
        objects = payload["data"]["objects"]
    except (KeyError, TypeError):
        raise CountryLookupError("Unexpected response shape from the API (missing data.objects).")

    if not objects:
        raise CountryLookupError(f"'{country_name}' doesn't match any country. Check the spelling.")

    return objects[0]


def parse_country_data(raw: dict) -> dict:
    """Turn one raw API country record into the clean summary dict the
    tool promises: capital, currency, population, languages, region,
    neighbours. Every field falls back gracefully if missing."""

    def safe_get(obj, *keys, default="Unknown"):
        for key in keys:
            if not isinstance(obj, dict):
                return default
            obj = obj.get(key)
        return obj if obj not in (None, "", []) else default

    try:
        name = safe_get(raw, "names", "common")

        capitals = raw.get("capitals") or []
        capital = capitals[0].get("name", "Unknown") if capitals else "Unknown"

        currencies = raw.get("currencies") or []
        if currencies:
            currency = ", ".join(
                f"{c.get('name', 'Unknown')} ({c.get('code', '?')})" for c in currencies
            )
        else:
            currency = "Unknown"

        population = raw.get("population")
        population = f"{population:,}" if isinstance(population, int) else "Unknown"

        languages = raw.get("languages") or []
        language_names = ", ".join(l.get("name", "Unknown") for l in languages) or "Unknown"

        region = safe_get(raw, "region")

        borders = raw.get("borders") or []
        if borders:
            neighbours = ", ".join(borders) + " (ISO alpha-3 codes)"
        else:
            neighbours = "None (island nation or no land borders)"

        return {
            "name": name,
            "capital": capital,
            "currency": currency,
            "population": population,
            "languages": language_names,
            "region": region,
            "neighbours": neighbours,
        }
    except Exception as exc:
        # Catch-all so a surprising payload shape never crashes the tool —
        # it just reports a clear failure instead.
        raise CountryLookupError(f"Couldn't parse the API response: {exc}")


def get_travel_snapshot(country_name: str) -> dict:
    """Full pipeline: fetch -> parse -> clean summary dict."""
    raw = fetch_country_data(country_name)
    return parse_country_data(raw)


def format_snapshot(snapshot: dict) -> str:
    lines = [
        f"Travel Snapshot: {snapshot['name']}",
        "-" * (18 + len(snapshot["name"])),
        f"Capital:      {snapshot['capital']}",
        f"Currency:     {snapshot['currency']}",
        f"Population:   {snapshot['population']}",
        f"Languages:    {snapshot['languages']}",
        f"Region:       {snapshot['region']}",
        f"Neighbours:   {snapshot['neighbours']}",
    ]
    return "\n".join(lines)


def run(country_name: str) -> None:
    try:
        snapshot = get_travel_snapshot(country_name)
        print(format_snapshot(snapshot))
    except CountryLookupError as exc:
        print(f"Couldn't build a snapshot for '{country_name}': {exc}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(" ".join(sys.argv[1:]))
    else:
        run(input("Enter a country name: ").strip())
