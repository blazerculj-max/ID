import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random
from fpdf import FPDF
import io

# --- POMOŽNA FUNKCIJA ZA ŠUMNIK (fpdf fix) ---
def clean_chars(text):
    mapping = {"č": "c", "š": "s", "ž": "z", "Č": "C", "Š": "S", "Ž": "Z", "\xa0": " "}
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

# --- KONFIGURACIJA ---
COLORS_MAP = {
    "Cool Blue": "#0070C0", "Fiery Red": "#FF0000",
    "Earth Green": "#00B050", "Sunshine Yellow": "#FFFF00"
}
OPPOSITES = {
    "Fiery Red": "Earth Green", "Earth Green": "Fiery Red",
    "Cool Blue": "Sunshine Yellow", "Sunshine Yellow": "Cool Blue"
}
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

raw_questions = [
    {"B": "Sistematičen in dosleden", "R": "Neposreden in prodoren", "G": "Razumevajoč in ustrežljiv", "Y": "Živahen in komunikativen"},
    {"B": "Objektiven opazovalec", "R": "Močan in neodvisen", "G": "Zanesljiv sopotnik", "Y": "Navdihujoč govorec"},
    {"B": "Logičen in preudaren", "R": "Hiter in odločen", "G": "Prijazen in skrben", "Y": "Sproščen in igriv"},
    {"B": "Pozoren na podrobnosti", "R": "Usmerjen h končnemu cilju", "G": "Uravnotežen in potrpežljiv", "Y": "Ustvarjalen in optimističen"},
    {"B": "Analitičen in distanciran", "R": "Energičen in tekmovalen", "G": "Iskren in lojalen", "Y": "Družaben in prepričljiv"},
    {"B": "Strokovno podkovan", "R": "Drzen pri odločanju", "G": "Uravnotežen in nežen", "Y": "Poln novih idej"},
    {"B": "Premišljen strateg", "R": "Dinamičen vodja", "G": "Podporen poslušalec", "Y": "Navdušen motivator"},
    {"B": "Metodičen in urejen", "R": "Avtoritativen in fokusiran", "G": "Diplomatski in miren", "Y": "Priljubljen in odprt"},
    {"B": "Previdno previden", "R": "Rezultatno zahteven", "G": "Stabilno zanesljiv", "Y": "Zgovorno prijazen"},
    {"B": "Uraden in zadržan", "R": "Vpliven in hiter", "G": "Topel in miren", "Y": "Duhovit in opazen"},
    {"B": "Temeljit preučevalec", "R": "Samozavesten akter", "G": "Zvest sodelavec", "Y": "Domišljijski vizionar"},
    {"B": "Resen in dejstven", "R": "Vztrajen in oster", "G": "Sodelovalen in toleranten", "Y": "Zabaven in prilagodljiv"},
    {"B": "Umirjen in natančen", "R": "Samostojen in močan", "G": "Skrben za odnose", "Y": "Povezovalen in aktiven"},
    {"B": "Zbran in analitičen", "R": "Ambiciozen in hiter", "G": "Prilagodljiv in blag", "Y": "Zabaven in zgovoren"},
    {"B": "Fokusiran na proces", "R": "Fokusiran na zmago", "G": "Fokusiran na ljudi", "Y": "Fokusiran na prihodnost"}
]

st.set_page_config(page_title="Insights Discovery - PDF Download", layout="centered")

st.title("🌈 Insights Discovery Profiler")
ime = st.text_input("Ime")
priimek = st.text_input("Priimek")

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
        st.subheader(f"Sklop {i+1} od 15")
        for idx, (color, text) in enumerate(items):
            val = st.radio(f"**{text}**", options=OPTIONS, index=1, horizontal=True, key=f"q_{i}_{color}")
            all_user_inputs.append((color, SCORE_MAP[val]))
        st.divider()
    
    submitted = st.form_submit_button("IZRAČUNAJ MOJ PROFIL")

if submitted:
    if not ime or not priimek:
        st.error("Prosim, vnesite ime in priimek za generiranje PDF-ja!")
    else:
        # 1. IZRAČUN
        conscious = {c: sum([score for color, score in all_user_inputs if color == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}

        st.success("Rezultati so pripravljeni!")

        # --- VIZUALIZACIJA NA EKRANU ---
        def draw_bar(data, title):
            fig = go.Figure(go.Bar(
                x=list(data.keys()), y=list(data.values()),
                marker_color=[COLORS_MAP[c] for c in data.keys()],
                text=[f"{v:.2f}" for v in data.values()], textposition='auto'
            ))
            fig.update_layout(title=title, yaxis=dict(range=[0, 6]), template="plotly_white", height=400)
            return fig

        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(draw_bar(conscious, "Zavedna Persona"), use_container_width=True)
        with c2: st.plotly_chart(draw_bar(less_conscious, "Nezavedna Persona"), use_container_width=True)

        # --- GENERIRANJE PDF-ja V POMNILNIK ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 25)
        pdf.cell(0, 60, clean_chars("Insights Discovery Osebni Profil"), align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 18)
        pdf.cell(0, 20, clean_chars(f"Pripravljeno za: {ime} {priimek}"), align='C', new_x="LMARGIN", new_y="NEXT")
        
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, clean_chars("Rezultati energij"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 12)
        pdf.ln(5)
        for c in COLORS_MAP:
            val_c = conscious[c]
            val_lc = less_conscious[c]
            pdf.cell(0, 10, clean_chars(f"- {c}: Zavedno {round(val_c, 2)} | Nezavedno {round(val_lc, 2)}"), new_x="LMARGIN", new_y="NEXT")

        # Ustvarimo bajte za download gumb
        pdf_output = pdf.output(dest='S')
        
        st.divider()
        st.subheader("Prenos poročila")
        st.download_button(
            label="📥 Prenesi PDF na računalnik",
            data=pdf_output,
            file_name=f"{ime}_{priimek}_Insights.pdf",
            mime="application/pdf"
        )
