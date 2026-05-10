import streamlit as st
import pandas as pd
import numpy as np
import itertools

# =========================================================
# PAGE SETUP & PREMIUM STYLING
# =========================================================
st.set_page_config(
    page_title="2026 World Cup Simulator",
    layout="wide"
)

# Professional Sports App UI Styles
st.markdown("""
    <style>
    /* Main Background and Text */
    .main {
        background-color: #0e1117;
    }
    
    /* Header Styling */
    .stTitle {
        font-weight: 800 !important;
        letter-spacing: -1px !important;
        color: #ffffff !important;
        margin-bottom: 0px !important;
    }
    
    .stCaption {
        font-size: 1.1em !important;
        color: #8892b0 !important;
        margin-bottom: 30px !important;
    }

    /* Professional Match Card */
    .match-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .match-card:hover {
        border-color: rgba(255, 255, 255, 0.3);
        background: rgba(255, 255, 255, 0.05);
    }

    .team-name {
        font-size: 1.1em;
        font-weight: 600;
        color: #e6edf3;
    }

    .vs-divider {
        font-size: 0.75em;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #8b949e;
        margin: 0 10px;
    }

    .winner-badge {
        background: #238636;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        margin-top: 10px;
        display: inline-block;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        color: #8b949e;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: #238636 !important;
        color: white !important;
    }

    /* Sidebar and Dataframe styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Champion Display */
    .champ-card {
        background: linear-gradient(145deg, #238636, #1a6328);
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-top: 20px;
    }
    
    .champ-title {
        text-transform: uppercase;
        letter-spacing: 5px;
        font-size: 0.9em;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 10px;
    }
    
    .champ-name {
        font-size: 3em;
        font-weight: 900;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# DATA LOADING & DYNAMIC FORM LOGIC
# =========================================================

@st.cache_data
def load_all_data():
    try:
        # Load Rankings
        rank_df = pd.read_csv("fifa_mens_rank.csv")
        rank_df.columns = rank_df.columns.str.strip()
        rank_df = rank_df.rename(columns={'total.points': 'total_points'})
        rank_df = rank_df.sort_values("date").drop_duplicates(subset=["team"], keep="last")
        teams_meta = rank_df.set_index('team').to_dict('index')

        # Load Match Results for Form Calculation
        # (Assuming standard Kaggle results.csv structure: date, home_team, away_team, home_score, away_score)
        match_df = pd.read_csv("results.csv")
        match_df['date'] = pd.to_datetime(match_df['date'])
        match_df = match_df.sort_values("date", ascending=False)
        
        return teams_meta, match_df
    except Exception as e:
        st.error(f"Error loading datasets: {e}")
        return {}, pd.DataFrame()

teams_metadata, match_history = load_all_data()

def calculate_team_momentum(team):
    """
    Calculates a form multiplier (0.9 to 1.1) based on the last 5 match results
    from the Kaggle results.csv file.
    """
    if match_history.empty:
        return 1.0
        
    # Filter matches where the team played (Home or Away)
    team_matches = match_history[(match_history['home_team'] == team) | (match_history['away_team'] == team)].head(5)
    
    if len(team_matches) == 0:
        return 1.0
        
    points = 0
    weights = [1.0, 0.8, 0.6, 0.4, 0.2] # Recent matches matter more
    
    for i, (_, row) in enumerate(team_matches.iterrows()):
        is_home = row['home_team'] == team
        if row['home_score'] == row['away_score']:
            res_points = 1 # Draw
        elif (is_home and row['home_score'] > row['away_score']) or (not is_home and row['away_score'] > row['home_score']):
            res_points = 3 # Win
        else:
            res_points = 0 # Loss
            
        points += res_points * (weights[i] if i < len(weights) else 0.1)
        
    # Normalize: Max possible points with these weights is 3 * sum(weights) = 9
    max_pts = sum(weights[:len(team_matches)]) * 3
    normalized_form = points / max_pts if max_pts > 0 else 0.5
    
    # Map normalized form (0 to 1) to a multiplier (0.9 to 1.15)
    # This ensures form doesn't completely break the ranking logic but gives a nice edge.
    multiplier = 0.9 + (normalized_form * 0.25)
    return multiplier

def get_team_power(team):
    data = teams_metadata.get(team, {'rank': 50, 'total_points': 1000})
    base_power = data.get('total_points', 1000) / max(1, data.get('rank', 50))
    
    # 1. Apply Host Advantage
    if team in ['USA', 'Canada', 'Mexico']:
        base_power *= 1.2
        
    # 2. Apply Dynamic Form Factor from Match History
    momentum = calculate_team_momentum(team)
    base_power *= momentum
    
    return base_power

# =========================================================
# SIMULATION ENGINES
# =========================================================

def simulate_match(team1, team2, can_draw=True):
    p1 = get_team_power(team1)
    p2 = get_team_power(team2)
    prob_t1_win = p1 / (p1 + p2)
    
    if can_draw:
        draw_chance = 0.25
        if np.random.random() < draw_chance:
            return "Draw"
    
    if np.random.random() < prob_t1_win:
        return team1
    else:
        return team2

def simulate_group(team_list):
    stats = {team: {
        "Team": team, 
        "W": 0, "D": 0, "L": 0, "Pts": 0, 
        "Form": f"{calculate_team_momentum(team):.2f}x",
        "Strength": get_team_power(team)
    } for team in team_list}
    
    for t1, t2 in itertools.combinations(team_list, 2):
        result = simulate_match(t1, t2, can_draw=True)
        if result == "Draw":
            stats[t1]["D"] += 1; stats[t1]["Pts"] += 1
            stats[t2]["D"] += 1; stats[t2]["Pts"] += 1
        elif result == t1:
            stats[t1]["W"] += 1; stats[t1]["Pts"] += 3
            stats[t2]["L"] += 1
        else:
            stats[t2]["W"] += 1; stats[t2]["Pts"] += 3
            stats[t1]["L"] += 1
            
    return pd.DataFrame(stats.values()).sort_values(by=["Pts", "Strength"], ascending=False).reset_index(drop=True)

# =========================================================
# APP STRUCTURE & STATE
# =========================================================

groups = {
    "Group A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "Group B": ["Canada", "Bosnia", "Qatar", "Switzerland"],
    "Group C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "Group D": ["USA", "Paraguay", "Australia", "Türkiye"],
    "Group E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "Group F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "Group G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "Group H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "Group I": ["France", "Senegal", "Iraq", "Norway"],
    "Group J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "Group K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "Group L": ["England", "Croatia", "Ghana", "Panama"]
}

if 'group_results' not in st.session_state:
    st.session_state.group_results = {g: None for g in groups.keys()}
if 'knockouts' not in st.session_state:
    st.session_state.knockouts = {
        'r32': None, 'r16': None, 'qf': None, 'sf': None, 'final': None
    }
if 'winners_revealed' not in st.session_state:
    st.session_state.winners_revealed = {}
if 'match_winners' not in st.session_state:
    st.session_state.match_winners = {}

st.title("2026 World Cup Simulator")
st.caption("A professional-grade simulation based on live FIFA rankings and dynamic Match Momentum.")

# =========================================================
# GROUP STAGE UI
# =========================================================
tabs = st.tabs([name.split(" ")[1] for name in groups.keys()])

for i, g_name in enumerate(groups.keys()):
    with tabs[i]:
        col_ctrl, col_table = st.columns([1, 2.5], gap="large")
        
        with col_ctrl:
            st.write(f"### {g_name}")
            if st.button(f"Simulate Group", key=f"btn_{g_name}", use_container_width=True):
                st.session_state.group_results[g_name] = simulate_group(groups[g_name])
            
            res = st.session_state.group_results[g_name]
            if res is not None:
                st.write("---")
                st.write("**Top Seed**")
                st.write(f"{res.iloc[0]['Team']}")
                st.write("**Runner Up**")
                st.write(f"{res.iloc[1]['Team']}")

        with col_table:
            if res is not None:
                display_df = res[['Team', 'W', 'D', 'L', 'Pts', 'Form']]
                def style_rows(row):
                    if row.name < 2: return ['background-color: rgba(35, 134, 54, 0.1)'] * len(row)
                    return [''] * len(row)
                st.dataframe(display_df.style.apply(style_rows, axis=1), use_container_width=True, hide_index=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("Qualifications")
thirds = []
for g_name, df in st.session_state.group_results.items():
    if df is not None:
        row = df.iloc[2].copy()
        row['Group'] = g_name
        thirds.append(row)

if thirds:
    st.sidebar.subheader("Wildcard Rank")
    thirds_df = pd.DataFrame(thirds).sort_values(by=["Pts", "Strength"], ascending=False).reset_index(drop=True)
    thirds_df.index += 1
    st.sidebar.dataframe(
        thirds_df[['Team', 'Pts']].head(8),
        use_container_width=True
    )

# =========================================================
# KNOCKOUT STAGE UI
# =========================================================
st.divider()
st.header("Tournament Bracket")

all_groups_done = all(v is not None for v in st.session_state.group_results.values())

if not all_groups_done:
    st.info("Complete the group stage simulations to progress to the knockout bracket.")
else:
    def knockout_match_ui(t1, t2, round_key, match_idx):
        key = f"{round_key}_{match_idx}"
        
        if key not in st.session_state.match_winners:
            st.session_state.match_winners[key] = simulate_match(t1, t2, can_draw=False)
        
        winner = st.session_state.match_winners[key]
        
        # Modern Card UI
        st.markdown(f"""
            <div class="match-card">
                <span class="team-name">{t1}</span>
                <span class="vs-divider">vs</span>
                <span class="team-name">{t2}</span>
            </div>
        """, unsafe_allow_html=True)
        
        if key not in st.session_state.winners_revealed:
            if st.button("See Outcome", key=f"rev_{key}", use_container_width=True):
                st.session_state.winners_revealed[key] = winner
                st.rerun()
            return None # Don't return winner to list yet if not revealed
        else:
            st.markdown(f'<div style="text-align:center; margin-top:-15px;"><span class="winner-badge">{winner} Advances</span></div>', unsafe_allow_html=True)
            return winner

    # --- ROUND OF 32 ---
    if st.button("Generate Initial Bracket", use_container_width=True):
        firsts = [df.iloc[0]['Team'] for df in st.session_state.group_results.values()]
        seconds = [df.iloc[1]['Team'] for df in st.session_state.group_results.values()]
        best_thirds = thirds_df.head(8)['Team'].tolist()
        pool = firsts + seconds + best_thirds
        np.random.shuffle(pool) 
        st.session_state.knockouts['r32'] = [(pool[i], pool[i+1]) for i in range(0, 32, 2)]
        st.session_state.winners_revealed = {}
        st.session_state.match_winners = {}
        st.session_state.knockouts['r16'] = None

    if st.session_state.knockouts['r32']:
        st.subheader("Round of 32")
        cols = st.columns(4, gap="medium")
        r16_winners = []
        for i, (t1, t2) in enumerate(st.session_state.knockouts['r32']):
            with cols[i % 4]:
                w = knockout_match_ui(t1, t2, 'r32', i)
                r16_winners.append(w)
        
        all_revealed = len([w for w in r16_winners if w is not None]) == 16
        if all_revealed and st.button("Lock Round & Advance", key="adv_r16", use_container_width=True):
            st.session_state.knockouts['r16'] = [(r16_winners[i], r16_winners[i+1]) for i in range(0, 16, 2)]
            
    if st.session_state.knockouts['r16']:
        st.subheader("Round of 16")
        cols = st.columns(4, gap="medium")
        qf_winners = []
        for i, (t1, t2) in enumerate(st.session_state.knockouts['r16']):
            with cols[i % 4]:
                w = knockout_match_ui(t1, t2, 'r16', i)
                qf_winners.append(w)
            
        all_revealed = len([w for w in qf_winners if w is not None]) == 8
        if all_revealed and st.button("Lock Round & Advance", key="adv_qf", use_container_width=True):
            st.session_state.knockouts['qf'] = [(qf_winners[i], qf_winners[i+1]) for i in range(0, 8, 2)]

    if st.session_state.knockouts['qf']:
        st.subheader("Quarter-Finals")
        cols = st.columns(2, gap="large")
        sf_winners = []
        for i, (t1, t2) in enumerate(st.session_state.knockouts['qf']):
            with cols[i % 2]:
                w = knockout_match_ui(t1, t2, 'qf', i)
                sf_winners.append(w)
            
        all_revealed = len([w for w in sf_winners if w is not None]) == 4
        if all_revealed and st.button("Lock Round & Advance", key="adv_sf", use_container_width=True):
            st.session_state.knockouts['sf'] = [(sf_winners[i], sf_winners[i+1]) for i in range(0, 4, 2)]

    if st.session_state.knockouts['sf']:
        st.subheader("Semi-Finals")
        cols = st.columns(2, gap="large")
        finalists = []
        for i, (t1, t2) in enumerate(st.session_state.knockouts['sf']):
            with cols[i % 2]:
                w = knockout_match_ui(t1, t2, 'sf', i)
                finalists.append(w)
            
        all_revealed = len([w for w in finalists if w is not None]) == 2
        if all_revealed and st.button("Final Matchup", key="adv_final", use_container_width=True):
            st.session_state.knockouts['final'] = (finalists[0], finalists[1])

    if st.session_state.knockouts['final']:
        st.header("The Final")
        t1, t2 = st.session_state.knockouts['final']
        
        col_f1, col_f2, col_f3 = st.columns([1,2,1])
        with col_f2:
            st.markdown(f"""
                <div class="match-card" style="padding:40px;">
                    <h2 style="margin:0;">{t1} <span class="vs-divider" style="font-size:0.5em;">vs</span> {t2}</h2>
                </div>
            """, unsafe_allow_html=True)
            
            if "final_reveal" not in st.session_state.winners_revealed:
                if st.button("DECIDE CHAMPION", use_container_width=True):
                    if "final_match" not in st.session_state.match_winners:
                        st.session_state.match_winners["final_match"] = simulate_match(t1, t2, can_draw=False)
                    st.session_state.winners_revealed["final_reveal"] = st.session_state.match_winners["final_match"]
                    st.rerun()
            else:
                champ = st.session_state.winners_revealed["final_reveal"]
                st.balloons()
                st.markdown(f"""
                <div class="champ-card">
                    <div class="champ-title">World Cup Champion</div>
                    <div class="champ-name">{champ}</div>
                </div>
                """, unsafe_allow_html=True)