#  2026 FIFA World Cup Tournament Simulator

This is a high-fidelity tournament simulator built with Python and Streamlit. The simulation engine leverages real-world FIFA rankings and historical match data to predict tournament outcomes.

---

##  Core Features

* **Live Data:** Integrates the latest FIFA Men's World Rankings.
* **Momentum:** Dynamic form analysis based on the team's last 5 matches.
* **Host Boost:** Custom strength multipliers for the co-hosts (USA, Canada, & Mexico).
* **New Format:** Full 48-team tournament bracket simulation.

---

##  Project Structure

* `app.py` - Main Streamlit application and UI logic.
* `requirements.txt` - Necessary Python dependencies.
* `fifa_mens_rank.csv` - Team ranking and points database.
* `results.csv` - Historical international match data.

---

##  Setup & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt

### 2. Launch the Simulator
```bash
streamlit run app.py
