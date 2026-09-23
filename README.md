# API-Powered Travel Intelligence Tool

Given a country name, prints a clean snapshot: capital, currency,
population, languages, region, and neighbouring countries (ISO codes).
Uses the [REST Countries API](https://restcountries.com/) (v5).

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env   # then add your free REST Countries API key
```

## Usage
```bash
python travel_intel.py "India"
python travel_intel.py            # prompts for a name instead
```

## Files
- `travel_intel.py` — fetch, parse, and print the snapshot
- `config.py` — reads endpoint/key/timeout from the environment
- `.env.example` — config template (real `.env` is gitignored)
- `sample_outputs/` — example runs for India, Japan, and an invalid name
- `obstacle_log.md` — issues hit along the way and how they were fixed
