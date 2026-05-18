# patitas-match

Minimal Flask project with IA (simple matching score model) for pet adoption profiles.

## Requirements

- Python 3.10+

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Service endpoints:

- `GET /` health/info
- `POST /predict` IA score prediction

Example payload:

```json
{
  "energy_level": 4,
  "apartment_friendly": true,
  "children_friendly": true
}
```

## Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```
