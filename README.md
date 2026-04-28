# Chocoholics-Anonymous
ChocAn Data Processing System — a localhost demo app built with **Python/Flask** + **vanilla HTML/CSS/JS**. Includes member/provider validation, service billing, and report generation.

## Run locally
From the repo root:

```bash
pip install -r chocan/requirements.txt
python chocan/app.py
```

Open `http://127.0.0.1:5000/`.

## Using the web UI
The home page has two tabs:
- **Provider terminal**
  - Validate a member number
  - Bill a service (writes a record to `chocan/data/services_log.json`)
- **Manager terminal**
  - View the provider directory (services sorted alphabetically)
  - Run reports (writes `.txt` files to `chocan/outputs/`)

## Quick demo values
- **Member (active)**: `100000001`
- **Member (suspended)**: `100000002`
- **Provider (active)**: `200000001`
- **Service code**: `598470`

## Outputs
- Billing log: `chocan/data/services_log.json`
- Generated files: `chocan/outputs/` (member reports, provider reports, summary report, EFT file)
