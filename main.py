import streamlit as st
import plotly.graph_objects as go
import random

# 1. Barvna shema Insights Discovery
COLORS = {
    "Cool Blue": "#0070C0",
    "Fiery Red": "#FF0000",
    "Earth Green": "#00B050",
    "Sunshine Yellow": "#FFFF00"
}

# 2. Lestvica in točkovanje
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

# 3. Baza 25 vprašanj (povzeto po tvojem dokumentu in dopolnjeno)
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
    {"B": "Metodičen in urejen", "R": "Gospodovalen in močan", "G": "Sodelovalen in prijazen", "Y": "Domišljijski in komunikativen"},
    {"B": "Analitičen", "R": "Hiter", "G": "Diplomatski", "Y": "Navdušen"},
    {"B": "Objektiven", "R": "Odločen", "G": "Ustrežljiv", "Y": "Družaben"},
    {"B": "Natančen", "R": "Direkten", "G": "Zvest", "Y": "Zgovoren"},
    {"B": "Premišljen", "R": "Močan", "G": "Miren", "Y": "Odprt"},
    {"B": "Sistematičen", "R": "Tekmovalen", "G": "Prilagodljiv", "Y": "Optimističen"},
    {"B": "Zadržan", "R": "Samozavesten", "G": "Potrpežljiv", "Y": "Živahen"},
    {"B": "Previdni", "R": "Hrabri", "G": "Skrbni", "Y": "Veseli"},
    {"B": "Urejeni", "R": "Učinkoviti", "G": "Harmonični", "Y": "Ustvarjalni"},
    {"B": "Fokusirani", "R": "Proaktivni", "G": "Podporni", "Y": "Komunikativni"},
    {"B": "Logični", "R": "Ambiciozni", "G": "Sočutni", "Y": "Navdihujoči"},
    {"B": "Pripravljeni", "R": "Odgovorni", "G": "Mirni", "Y": "Priljubljeni"},
    {"B": "Dejstveni", "R": "Iniciativni", "G": "Uravnoteženi", "Y": "Dinamični"},
    {"B": "Resni", "R": "Energični", "G": "Prijazni", "Y": "Zabavni"},
    {"B": "Tehnični", "R": "Vodstveni", "G": "Ekipni", "Y": "Promocijski"},
    {"B": "Stabilni", "R": "Močni", "G": "Varni", "Y": "Svobodni"}
]

st.set_page_config(page_title="Insights Discovery - 25", layout="centered")
st.title("🌈 Insights Discovery Vprašalnik")
st.write("Ocenite trditve: **L** (najmanj jaz) do **M** (najbolj jaz).")

# Shranimo vrstni red trditev v session_state, da se ne premešajo ob vsakem kliku
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
        col1, col2 = st.columns(2)
        for idx, (color, text) in enumerate(items):
            target_col = col1 if idx % 2 == 0 else col2
            with target_col:
                val = st.select_slider(text, options=OPTIONS, value="1", key=f"q_{i}_{color}")
                all_user_inputs.append((color, SCORE_MAP[val]))
        st.divider()
    
    submitted = st.form_submit_button("IZRAČUNAJ MOJ PROFIL")

if submitted:
    totals = {"Cool Blue": 0, "Fiery Red": 0, "Earth Green": 0, "Sunshine Yellow": 0}
    for color, score in all_user_inputs:
        totals[color] += score
    
    total_all = sum(totals.values())
    if total_all > 0:
        st.balloons()
        pct = {k: (v / total_all) * 100 for k, v in totals.items()}
        
        # Graf
        categories = list(pct.keys())
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=list(pct.values()) + [list(pct.values())[0]], theta=categories + [categories[0]], fill='toself', line_color='black'))
        st.plotly_chart(fig)
        
        # Metrike
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Modra", f"{round(pct['Cool Blue'])}%")
        c2.metric("Rdeča", f"{round(pct['Fiery Red'])}%")
        c3.metric("Zelena", f"{round(pct['Earth Green'])}%")
        c4.metric("Rumena", f"{round(pct['Sunshine Yellow'])}%")
    else:
        st.error("Prosim, izpolnite vprašalnik.")
