===========================================================
2026 FIFA WORLD CUP TOURNAMENT SIMULATOR

This is a high-fidelity tournament simulator built with Python and Streamlit. The engine uses real-world FIFA rankings and historical match data to predict outcomes.


[ CORE FEATURES ]
LIVE DATA: Integrates latest FIFA Men's World Rankings.

MOMENTUM: Dynamic Form analysis based on last 5 matches.

HOST BOOST: Strength multipliers for USA, Canada & Mexico.

NEW FORMAT: Full 48-team tournament bracket simulation.


[ PROJECT FILES ]
app.py: Main application & UI 

coderequirements.txt: Necessary Python libraries

fifa_mens_rank.csv: Team ranking & points database

results.csv: International match history data


[ SETUP & EXECUTION ]

Install requirements: 

pip install -r requirements.txt

Launch the simulator:

streamlit run app.py


[ SIMULATION LOGIC ]

The app calculates a "Power Score" (P) for every team:

P = Momentum x (Total Points / Rank) x Host Advantage 

Matches are simulated using these weighted scores to calculate win probabilities, ensuring realistic upsets and tournament progression.===========================================================
CREATED WITH STREAMLIT & PYTHON