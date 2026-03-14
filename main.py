import streamlit as st
import plotly.graph_objects as go
import random

# 1. Barvna shema
COLORS = {
    "Cool Blue": "#0070C0",
    "Fiery Red": "#FF0000",
    "Earth Green": "#00B050",
    "Sunshine Yellow": "#FFFF00"
}

# 2. Mapiranje lestvice v točke
# L = 0, M = 6, ostalo so vmesne vrednosti
SCORE_MAP = {
    "L": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "M": 6
}
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]

# 3. Podatki (tukaj vnesi vseh 25 vprašanj iz svojega vira)
# Pripravil sem strukturo za prvih nekaj, ostalo dopolni po vzorcu
raw_questions = [
    {"B": "Natančen in premišljen", "R": "Usmerjen v rezultate", "G": "Občutljiv in diplomatski", "Y": "Spodbuja in ceni druge"},
    {"B": "Analitičen in objektiven", "R": "Odločen in močan", "G": "Potrpežljiv in razumevajoč", "Y": "Navdušen in komunikativen"},
    {"B": "Zbran in pozoren na detajle", "R": "Nadzorovan in usmerjen", "G": "Mirna in pomirjujoča", "Y": "Odprt in družaben"},
    {"B": "Jasen in jedrnat", "R": "Neposreden in tekmovalen", "G": "Zvest in prilagodljiv", "Y": "Zgovoren in družaben"},
    {"B": "Premišljen in analitičen", "R": "Samozavesten in močan", "G": "Vztrajen in potrpežljiv", "Y": "Izraža navdušenje"},
    # ... dodaj do 25
]

# Če jih je manj kot 25, jih za testiranje podvojimo
if len(raw_questions) < 25:
    raw_questions = (raw_questions * 5)[:25]

st.set_page_config(page_title="Insights Discovery Profiler", layout="centered")

st.title("🌈 Insights Discovery Vprašalnik")
st.info("Ocenite trditve: L (najmanj jaz) -> M (najbolj jaz)")

with st.form("insights_form"):
    user_responses = []
    
    for i, q_set in enumerate(raw_questions):
        st.subheader(f"Sklop {i+1} od 25")
        
        # Priprava trditev in naključno mešanje (shuffling)
        items = [
            ("Cool Blue", q_set["B"]),
            ("Fiery Red", q_set["R"]),
            ("Earth Green", q_set["G"]),
            ("Sunshine Yellow", q_set["Y"])
        ]
        random.shuffle(items)
        
        # Prikaz dveh trditev v vrsti za boljšo preglednost na telefonu
        col1, col2 = st.columns(2)
        for idx, (color, text) in enumerate(items):
            target_col = col1 if idx % 2 == 0 else col2
            with target_col:
                val = st.select_slider(
                    text,
                    options=OPTIONS,
                    value="1",
                    key=f"q_{i}_{color}_{idx}"
                )
                user_responses.append((color, SCORE_MAP[val]))
        st.divider()

    submit = st.form_submit_button("IZRAČUNAJ MOJ PROFIL")

# 4. Izračun in graf
if submit:
    totals = {"Cool Blue": 0, "Fiery Red": 0, "Earth Green": 0, "Sunshine Yellow": 0}
    for color, points in user_responses:
        totals[color] += points
        
    all_points = sum(totals.values())
    
    if all_points > 0:
        st.balloons()
        st.header("Vaša barvna energija")
        
        # Izračun procentov
        percentages = {k: (v / all_points) * 100 for k, v in totals.items()}
        
        # Radar Chart
        categories = list(percentages.keys())
        p_values = list(percentages.values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=p_values + [p_values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(180, 180, 180, 0.4)',
            line=dict(color='black', width=2)
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(p_values) + 10])),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Rezultati v številkah
        cols = st.columns(4)
        for i,
