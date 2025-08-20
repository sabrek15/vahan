# Vahan Registrations — Investor Dashboard

This Streamlit app visualizes vehicle registration and revenue data from public Parivahan APIs.

---

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sabrek15/vahan.git
   cd <your-repo-folder>
   ```

2. **Create and activate a Python virtual environment (recommended):**
   ```bash
   python3 -m venv .env
   source .env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

---

## Data Assumptions

- The app fetches data from public Parivahan dashboard APIs.
- API responses may change; parsing logic assumes current JSON structures.
- Data includes vehicle registrations, revenue, and trends by year, quarter, and month.
- No personally identifiable information is processed.
- All data is for informational and visualization purposes only.

---

## Notes

- If API endpoints or data formats change, update the parsing functions in `vahan/parsing.py`.
- For troubleshooting, use the debug expanders in the app to inspect raw API responses.