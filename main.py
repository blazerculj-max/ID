import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random
from fpdf import FPDF
from openai import OpenAI
from datetime import datetime

# --- POMOŽNA FUNKCIJA ZA ČIŠČENJE ---
def clean_chars(text):
    """Odstrani šumnike in trde presledke za PDF motor."""
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

# Inicializacija OpenAI odjemalca
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generiraj_ai_interpretacijo(ime, conscious, less_conscious):
    """Klic Genie-ja za strokovno interpretacijo profila."""
    prompt = f"""
    Ti si Insights Discovery strokovnjak. Ustvari kratek osebni profil za osebo: {ime}.
    Zavedne energije (0-6): {conscious}.
    Manj zavedne energije (0-6): {less_conscious}.
    
    Navodila:
    1. Uporabi strokovno terminologijo (npr. 'Reformatorski direktor', 'Koordinacijski opazovalec', 'Inspiracijski motivator').
    2. Na podlagi razmerja energij določi prevladujoč tip.
    3. Napiši tri poglavja: 
       - Osebni stil (kratek opis vedenja)
       - Interakcija z drugimi (kako oseba komunicira)
       - Predlogi za razvoj (kaj bi bilo dobro optimizirati).
    Bodi profesionalen in spodbuden.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Ti si Insights Discovery svetovalec Genie."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Interpretacija trenutno ni na voljo. ({e})"

# --- VPRAŠALNIK (15 SKLOPOV) ---
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

st.set_page_config(page_title="Insights Discovery - Genie AI", layout="centered")

st.title("🌈 Insights Discovery AI Profiler")
ime_vnos = st.text_input("Ime")
priimek_vnos = st.text_input("Priimek")

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
    submitted = st.form_submit_button("USTVARI MOJ AI PROFIL")

if submitted:
    if not ime_vnos or not priimek_vnos:
        st.error("Prosim, vnesite ime in priimek!")
    else:
        # 1. IZRAČUN
        conscious = {c: sum([score for color, score in all_user_inputs if color == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}

        with st.spinner('Genie pripravlja vašo interpretacijo...'):
            ai_interpretacija = generiraj_ai_interpretacijo(ime_vnos, conscious, less_conscious)

        # 2. VIZUALIZACIJA NA EKRANU
        st.header(f"Insights Discovery Poročilo: {ime_vnos} {priimek_vnos}")
        
        def draw_bar_chart(data, title):
            return go.Figure(go.Bar(
                x=list(data.keys()), y=list(data.values()),
                marker_color=[COLORS_MAP[c] for c in data.keys()],
                text=[f"{v:.2f}" for v in data.values()], textposition='auto'
            )).update_layout(title=title, yaxis=dict(range=[0, 6]), template="plotly_white", height=400)

        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(draw_bar_chart(conscious, "Zavedna Persona"), use_container_width=True)
        with c2: st.plotly_chart(draw_bar_chart(less_conscious, "Manj zavedna Persona"), use_container_width=True)

        st.markdown("### Strokovna interpretacija (Genie AI)")
        st.write(ai_interpretacija)

        # 3. PDF GENERIRANJE
        pdf = FPDF()
        
        # Naslovnica
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 25)
        pdf.cell(0, 60, "Insights Discovery", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, "Osebni profil (Foundation)", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(20)
        pdf.set_font("Helvetica", "", 16)
        pdf.cell(0, 10, clean_chars(f"{ime_vnos} {priimek_vnos}"), align='C', new_x="LMARGIN", new_y="NEXT")
        
        # AI poglavje
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 15, clean_chars("Vasa osebna interpretacija"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, clean_chars(ai_interpretacija))
        
        # Grafični podatki
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 15, clean_chars("Vrednosti barvnih energij"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 12)
        for c in COLORS_MAP:
            pdf.cell(0, 10, clean_chars(f"{c}: Zavedno {round(conscious[c], 2)} | Manj zavedno {round(less_conscious[c], 2)}"), new_x="LMARGIN", new_y="NEXT")

        pdf_bytes = bytes(pdf.output())
        
        st.divider()
        st.download_button(
            label="📥 Prenesi celoten PDF profil",
            data=pdf_bytes,
            file_name=f"Insights_{ime_vnos}_{priimek_vnos}.pdf",
            mime="application/pdf"
        )
