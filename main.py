import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random

# 1. Barvna konfiguracija Insights Discovery
COLORS_MAP = {
    "Cool Blue": "#0070C0",
    "Fiery Red": "#FF0000",
    "Earth Green": "#00B050",
    "Sunshine Yellow": "#FFFF00"
}

# Mapiranje nasprotnih barv za nezavedno persono
OPPOSITES = {
    "Fiery Red": "Earth Green",
    "Earth Green": "Fiery Red",
    "Cool Blue": "Sunshine Yellow",
    "Sunshine Yellow": "Cool Blue"
}

OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

# 2. Vprašalnik (25 sklopov)
raw_questions = [
    {"B": "Natančen in premišljen", "R": "Usmerjen v rezultate", "G": "Občutljiv in diplomatski", "Y": "Spodbuja in ceni druge"},
    {"B": "Zbran in pozoren na detajle", "R": "Nadzorovan in usmerjen", "G": "Mirna in pomirjujoča", "Y": "Odprt in družaben"},
    {"B": "Jasen in jedrnat", "R": "Neposreden in tekmovalen", "G": "Zvest in prilagodljiv", "Y": "Zgovoren in družaben"},
    {"B": "Premišljen in analitičen", "R": "Samozavesten in močan", "G": "Vztrajen in potrpežljiv", "Y": "Izraža navdušenje"},
    {"B": "Razumen in objektiven", "R": "Odločen in močna volja", "G": "Raziskovalen in miren", "Y": "Zagnan in optimističen"},
    {"B": "Temeljit in precizen", "R": "Robusten in direkten", "G": "Nezahteven in prilagodljiv", "Y": "Vpliven in prepričljiv"},
    {"B": "Logičen in sistematičen", "R": "Drzen in tekmovalen", "G": "Uravnotežen in ustrežljiv", "Y": "Živahen in igriv"},
    {"B": "Formalen in zadržan", "R": "Podjeten in hiter", "G": "Topel in iskren", "Y": "Sproščen in zabaven"},
    {"B": "Skeptičen in previden", "R": "Zahteven in nepopustljiv", "G": "Zanesljiv in konstanten", "Y": "Ekspresiven in živahen"},
    {"B": "Metodičen in urejen", "R": "Gospodovalen in močan", "G": "Sodelovalen in prijazen", "Y": "Domišljijski in komunikativen"}
]
# Dopuni do 25
if len(raw_questions) < 25:
    raw_questions = (raw_questions * 3)[:25]

st.set_page_config(page_title="Insights Discovery - Blaž", layout="centered")

# CSS za lepši izgled gumbov
st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] { background-color: #f9f9f9; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
    .stRadio > div { flex-direction: row; justify-content: space-around; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌈 Insights Discovery Profiler")
st.write("Izberite vrednost od **L (0)** do **M (6)** za vsako trditev.")

# Mešanje vprašanj (shranjeno v session_state)
if 'shuffled_items' not in st.session_state:
    order = []
    for q in raw_questions:
        items = [("Cool Blue", q["B"]), ("Fiery Red", q["R"]), ("Earth Green", q["G"]), ("Sunshine Yellow", q["Y"])]
        random.shuffle(items)
        order.append(items)
    st.session_state.shuffled_items = order

with st.form("insights_form"):
    all_user_inputs = []
    for i, items in enumerate(st.session_state.shuffled_items):
        st.subheader(f"Sklop {i+1} od 25")
        
        for idx, (color, text) in enumerate(items):
            # Uporaba st.radio horizontalno namesto sliderja
            val = st.radio(
                f"**{text}**",
                options=OPTIONS,
                index=1, # Privzeto na "1"
                horizontal=True,
                key=f"q_{i}_{color}"
            )
            all_user_inputs.append((color, SCORE_MAP[val]))
        st.divider()
    
    submitted = st.form_submit_button("IZRAČUNAJ MOJ PROFIL")

if submitted:
    # 1. IZRAČUN ZAVEDNE PERSONE (Povprečje)
    conscious = {c: 0 for c in COLORS_MAP}
    for color, score in all_user_inputs:
        conscious[color] += score
    
    for c in conscious: conscious[c] /= 25

    # 2. IZRAČUN NEZAVEDNE PERSONE (Zrcaljenje)
    less_conscious = {}
    for color in COLORS_MAP:
        opposite_color = OPPOSITES[color]
        less_conscious[color] = 6.0 - conscious[opposite_color]

    st.balloons()
    
    # 3. PRIKAZ GRAFOV (Original Insights Style)
    def draw_insights_chart(data, title):
        fig = go.Figure(data=[
            go.Bar(
                x=list(data.keys()),
                y=list(data.values()),
                marker_color=[COLORS_MAP[c] for c in data.keys()],
                text=[f"{v:.2f}" for v in data.values()],
                textposition='outside',
                cliponaxis=False
            )
        ])
        fig.update_layout(
            title=title,
            yaxis=dict(range=[0, 7], title="Energija (0-6)"),
            template="plotly_white",
            height=450
        )
        return fig

    st.header("Rezultati analize")
    
    # Zavedna Persona
    st.plotly_chart(draw_insights_chart(conscious, "Zavedna Persona (Conscious)"), use_container_width=True)
    
    # Nezavedna Persona
    st.plotly_chart(draw_insights_chart(less_conscious, "Nezavedna Persona (Less Conscious)"), use_container_width=True)

    # 4. PREFERENCE FLOW (S puščicami/deltami)
    st.divider()
    st.subheader("Preference Flow (Prilagajanje)")
    f_cols = st.columns(4)
    for i, color in enumerate(COLORS_MAP.keys()):
        diff = conscious[color] - less_conscious[color]
        with f_cols[i]:
            st.markdown(f"<div style='border-bottom: 4px solid {COLORS_MAP[color]}; padding-bottom:5px; font-weight:bold;'>{color}</div>", unsafe_allow_html=True)
            st.metric(label="Zavedno", value=f"{round(conscious[color], 2)}", delta=f"{round(diff, 2)}")
            st.caption(f"Nezavedno: {round(less_conscious[color], 2)}")

    # 5. RADAR KOLO
    st.divider()
    st.subheader("Položaj na kolesu (Zavedni profil)")
    cat = list(conscious.keys())
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[conscious[c] for c in cat] + [conscious[cat[0]]],
        theta=cat + [cat[0]],
        fill='toself',
        fillcolor='rgba(150, 150, 150, 0.2)',
        line=dict(color='black', width=2)
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 6])), showlegend=False)
    st.plotly_chart(fig_radar)
