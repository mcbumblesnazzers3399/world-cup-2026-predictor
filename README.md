# 2026 FIFA World Cup Tournament Simulator

A high-fidelity tournament simulator built for the 2026 FIFA World Cup, integrating real-world FIFA rankings and historical match data to run a full 48-team bracket simulation.

## Live Demo

Try the simulator here: [world-cup-2026-predictor](https://world-cup-2026-predictor-rashminshasramay1026.streamlit.app/)

## Project Structure

- `app.py` — Core Streamlit application and UI engine.
- `requirements.txt` — Required Python libraries for deployment.
- `fifa_mens_rank.csv` — Current FIFA rankings and points data.
- `results.csv` — Historical match data used for performance analytics.

## Running Locally

**1. Clone the repository**

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Launch the app**

```bash
streamlit run app.py
```

## Methodology

Predictions are built on three weighted factors:

- **FIFA Ranking (60%)** — Baseline team strength derived from current FIFA standings.
- **Momentum (30%)** — Performance score calculated from each team's last 5 international matches.
- **Host Advantage (10%)** — A multiplier applied when USA, Canada, or Mexico are playing at home.

## Contributing

Issues and pull requests are welcome. If you have ideas for improving the algorithm or the interface, open an issue or submit a PR.

