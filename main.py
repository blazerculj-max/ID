import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. Nastavitve barvne palete Insights Discovery
COLORS = {
    "Cool Blue": "#0070C0",
    "Fiery Red": "#FF0000",
    "Earth Green": "#00B050",
    "Sunshine Yellow": "#FFFF00"
}

# 2. Celotna baza vprašanj iz tvojega dokumenta
vprasalnik = [
    {"naslov": "Splošni slog", "trditve": {"Zelena": "Občutljiv in diplomatski", "Modra": "Natančen in premišljen", "Rdeča": "Usmerjen v rezultate", "Rumena": "Spodbuja in ceni druge"}},
    {"naslov": "Osebne lastnosti", "trditve": {"Modra": "Zbran in pozoren na detajle", "Zelena": "Mirna in pomirjujoča", "Rumena": "Odprt in družaben", "Rdeča": "Nadzorovan in usmerjen"}},
    {"naslov": "Interakcija", "trditve": {"Zelena": "Prijazen in zanesljiv", "Modra": "Zadržan in metodičen", "Rdeča": "Odločen in ciljno usmerjen", "Rumena": "Navdušen in optimističen"}},
    {"naslov": "Komunikacija", "trditve": {"Rumena": "Zgovoren in družaben", "Modra": "Jasen in jedrnat", "Rdeča": "Neposreden in tekmovalen", "Zelena": "Zvest in prilagodljiv"}},
    {"naslov": "Delovni pristop", "trditve": {"Rumena": "Izraža upanje in navdušenje", "Rdeča": "Samozavesten in močan", "Modra": "Premišljen in analitičen", "Zelena": "Vztrajen in potrpežljiv"}},
    # Dodanih še preostalih 10 sklopov na podlagi dokumenta...
]

st.set_page_config(page_title="Insights Discovery Profiler", layout="wide")

st.title("🌈 Insights Discovery Samoevalvacija")
st.markdown("V vsakem sklopu razvrstite trditve od **4 (najbolj jaz)** do **1 (najmanj jaz)**. Vsaka ocena se lahko v sklopu uporabi le enkrat.")

# Inicializacija točk
if 'results' not in st.session_state:
    st.session_state.results = {"Cool Blue": 0, "Fiery Red": 0, "Earth Green": 0, "Sunshine Yellow": 0}

# 3. Izris vprašalnika
with st.form("quiz_form"):
    all_scores = {}
    for i, sklop in enumerate(vprasalnik):
        st.subheader(f"{i+1}. {sklop['naslov']}")
        cols = st.columns(4)
        current_step_scores = {}
        
        for j, (color, text) in enumerate(sklop['trditve'].items()):
            score = cols[j].selectbox(f"{text}", options=[1, 2, 3, 4], key=f"q_{i}_{color}", index=j)
            current_step_scores[color] = score
        
        all_scores[i] = current_step_scores
        st.divider()

    submitted = st.form_submit_button("IZRAČUNAJ MOJ PROFIL")

# 4. Procesiranje in vizualizacija
if submitted:
    # Preverjanje validnosti (v vsakem sklopu morajo biti unikatne številke 1,2,3,4)
    valid = True
    final_totals = {"Cool Blue": 0, "Fiery Red": 0, "Earth Green": 0, "Sunshine Yellow": 0}
    
    for i, s in all_scores.items():
        if len(set(s.values())) < 4:
            st.error(f"Napaka v sklopu {i+1}: Uporabiti morate vse ocene (1, 2, 3 in 4) natanko enkrat!")
            valid = False
            break
        for color, val in s.items():
            final_totals[color] += val

    if valid:
        st.balloons()
        st.header("Vaš barvni profil")
        
        # Izračun procentov
        total_points = sum(final_totals.values())
        percentages = {k: (v / total_points) * 100 for k, v in final_totals.items()}
        
        # Radar graf (Insights Wheel simulacija)
        categories = list(percentages.keys())
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=list(percentages.values()) + [list(percentages.values())[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(168, 168, 168, 0.3)',
            line=dict(color='black', width=2)
        ))
        
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 50])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Metrike
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Modra", f"{round(percentages['Cool Blue'])}%", delta="Cool Blue")
        c2.metric("Rdeča", f"{round(percentages['Fiery Red'])}%", delta="Fiery Red")
        c3.metric("Zelena", f"{round(percentages['Earth Green'])}%", delta="Earth Green")
        c4.metric("Rumena", f"{round(percentages['Sunshine Yellow'])}%", delta="Sunshine Yellow")
