import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random

# 1. Konfiguracija in barve
COLORS = {
    "Cool Blue": "#0070C0",
    "Fiery Red": "#FF0000",
    "Earth Green": "#00B050",
    "Sunshine Yellow": "#FFFF00"
}

OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

# 2. Baza 25 vprašanj
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
st.title("🌈 Insights Discovery Profil")
st.write("Ocenite trditve: **L** (0 točk) do **M** (6 točk).")

# Mešanje vprašanj (da se ne premešajo ob vsakem premiku drsnika)
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
    
    submitted = st.form_submit_button("IZRAČUNAJ PROFIL")

if submitted:
    # 1. Izračun ZAVEDNE persone (Povprečje)
    conscious = {"Cool Blue": 0, "Fiery Red": 0, "Earth Green": 0, "Sunshine Yellow": 0}
    for color, score in all_user_inputs:
        conscious[color] += score
    
    # Normalizacija na povprečje (0-6)
    for color in conscious:
        conscious[color] = conscious[color] / 25

    # 2. Izračun NEZAVEDNE persone (Logika zrcaljenja nasprotnih barv)
    # Rdeča <-> Zelena | Modra <-> Rumena
    less_conscious = {
        "Fiery Red": 6.0 - conscious["Earth Green"],
        "Earth Green": 6.0 - conscious["Fiery Red"],
        "Cool Blue": 6.0 - conscious["Sunshine Yellow"],
        "Sunshine Yellow": 6.0 - conscious["Cool Blue"]
    }

    st.balloons()
    
    # 3. PRIKAZ REZULTATOV
    st.header("Vaša barvna analiza")

    # Stolpčni graf primerjave
    comparison_data = []
    for color in COLORS:
        comparison_data.append({"Barva": color, "Vrednost": conscious[color], "Persona": "Zavedna (Conscious)"})
        comparison_data.append({"Barva": color, "Vrednost": less_conscious[color], "Persona": "Nezavedna (Less Conscious)"})
    
    df = pd.DataFrame(comparison_data)
    fig_bar = px.bar(df, x="Barva", y="Vrednost", color="Persona", barmode="group",
                     color_discrete_map={"Zavedna (Conscious)": "#333333", "Nezavedna (Less Conscious)": "#AAAAAA"},
                     title="Primerjava: Zavedna vs. Nezavedna Persona")
    fig_bar.update_yaxes(range=[0, 6])
    st.plotly_chart(fig_bar)

    # 4. PREFERENCE FLOW (Delta)
    st.subheader("Preference Flow (Prilagajanje)")
    st.write("Razlika med tem, kdo ste (nezavedno) in kako delujete (zavedno).")
    
    flow_cols = st.columns(4)
    for i, color in enumerate(COLORS.keys()):
        diff = conscious[color] - less_conscious[color]
        with flow_cols[i]:
            st.markdown(f"<p style='color:{COLORS[color]}; font-weight:bold;'>{color}</p>", unsafe_allow_html=True)
            st.metric(label="Zavedno", value=f"{round(conscious[color], 2)}", delta=f"{round(diff, 2)}")

    # 5. RADAR GRAF (Zavedni profil)
    st.subheader("Insights Discovery Kolo")
    categories = list(conscious.keys())
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[conscious[c] for c in categories] + [conscious[categories[0]]],
        theta=categories + [categories[0]],
        fill='toself',
        line_color='black',
        name='Zavedno'
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 6])))
    st.plotly_chart(fig_radar)

    st.info("Opomba: Pozitivna delta pri Preference Flow pomeni, da v to energijo vlagate zavesten trud. Negativna delta pomeni, da to energijo v trenutnem okolju verjetno zadržujete.")
