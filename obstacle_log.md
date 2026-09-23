# Obstacle Log : API-Powered Travel Intelligence Tool

## 1. The "obvious" API (restcountries.com v3.1) is dead

```json
{"success": false, "data": null, "errors": [{"message": "This API version has been deprecated..."}]}
```

`v1`-`v4` were retired; the only maintained version is `v5`, served from a
new host (`api.restcountries.com`) and gated behind a bearer-token API key
(free tier: 500 requests/month). This wasn't a code bug, the fix was
migrating to the new base URL, auth header and response shape:
- Old: bare array `[ { "name": {...}, "capital": [...] } ]`
- New: enveloped object `{ "data": { "objects": [ {...} ], "meta": {...} } }`,
  with renamed/nested fields (`names.common` instead of `name.common`,
  `capitals` as a list of objects instead of `capital` as a list of strings,
  etc.)

**Fix:** targeted the v5 endpoint and envelope shape, and treated the API
key as required configuration rather than assuming a keyless public API.

## 2. Keeping the API key out of the codebase
Since v5 requires a key, hardcoding it was a non-starter, it would leak
straight into the GitHub repo. Solved with `config.py` + `.env` (via
`python-dotenv`): the script reads `REST_COUNTRIES_API_KEY` and
`REST_COUNTRIES_BASE_URL` from the environment, `.env` is what a real user
fills in locally, and only `.env.example` (no real key) is committed.

## 3. Neighbouring countries are only given as ISO codes
`borders` in the v5 response is a list of alpha-3 codes (eg: `PAK`, `CHN`),
not full country names. Resolving each one to a name would mean one extra
API call per neighbour which burns through the 500/month free quota fast
for something cosmetic. Decided to surface the codes directly and label
them clearly ("ISO alpha-3 codes") rather than add N extra round-trips per
lookup.

## 4. Missing fields shouldn't crash the tool
Some countries have no land borders (island nations), and any field can
theoretically be absent from the API response. Used a `safe_get` helper
with defaults everywhere a field is read, so a sparse record prints
"Unknown" / "None (island nation or no land borders)" for that field
instead of raising.

## 5. Testing without live network access
This was built in a sandboxed dev environment with no outbound network
access for the code itself, so `requests.get` was mocked
(`unittest.mock.patch`) to exercise every path: a full successful record,
an unknown-country (empty result set) response, a sparse/missing-fields
record, a simulated connection failure, and a malformed/unexpected
payload shape. All five passed. The sample outputs in `sample_outputs/`
are illustrative, built from the documented v5 response shape and public
reference data (India, Japan) rather than a live run, swap in a real
`REST_COUNTRIES_API_KEY` and they'll match a genuine `python
travel_intel.py "India"` call.
