import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random
from fpdf import FPDF
from openai import OpenAI

# --- POMOŽNA FUNKCIJA ZA ŠUMNIK ---
def clean_chars(text):
    mapping = {"č": "c", "š": "s", "ž": "z", "Č": "C", "Š": "S", "Ž": "Z", "\xa0": " "}
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

# --- MASTER PROMPT ---
MASTER_SYSTEM_PROMPT = """
Ti si vrhunski Insights Discovery svetovalec. Tvoja naloga je interpretirati rezultate barvnih energij.
NAVODILA:
1. Uporabljaj strokovno terminologijo (npr. Reformatorski direktor, zavedna/manj zavedna persona, tok preferenc).
2. Odgovor razdeli v jasna poglavja z uporabo alinej (bullet points).
3. Bodi analitičen, neposreden in spodbuden.
4. Vsako poglavje naj ima 3-4 poglobljene točke.
"""

# --- KONFIGURACIJA ---
COLORS_MAP = {"Cool Blue": "#0070C0", "Fiery Red": "#FF0000", "Earth Green": "#00B050", "Sunshine Yellow": "#FFFF00"}
OPPOSITES = {"Fiery Red": "Earth Green", "Earth Green": "Fiery Red", "Cool Blue": "Sunshine Yellow", "Sunshine Yellow": "Cool Blue"}
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generiraj_premium_profil(polno_ime, conscious, less_conscious, coaching_txt):
    pref_flow = {c: round(conscious[c] - less_conscious[c], 2) for c in COLORS_MAP}
    user_content = f"Ustvari osebni profil za: {polno_ime}. Zavedne: {conscious}. Manj zavedne: {less_conscious}. Tok: {pref_flow}. Moduli: {coaching_txt}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": MASTER_SYSTEM_PROMPT},
                  {"role": "user", "content": user_content}],
        temperature=0.7
    )
    return response.choices[0].message.content

# --- UI APPLIKACIJE ---
st.set_page_config(page_title="Insights Discovery Expert", layout="wide")

# CSS za vodoravno poravnavo gumbov v vrsti s tekstom
st.markdown("""
    <style>
    div.row-widget.stRadio > div {
        flex-direction: row;
        justify-content: flex-start;
        gap: 10px;
    }
    .stForm {
        border: 2px solid #0070C0 !important;
        padding: 25px;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌈 Insights Discovery - Profesionalni Profiler")
polno_ime = st.text_input("Vnesite ime in priimek stranke", placeholder="Ime Priimek")

# 15 sklopov trditev
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

if 'shuffled' not in st.session_state:
    st.session_state.shuffled = [[(c, q[k]) for c, k in zip(COLORS_MAP.keys(), ["B","R","G","Y"])] for q in raw_questions]

with st.form("insights_form"):
    all_inputs = []
    
    # Glava tabele
    h1, h2 = st.columns([1, 2])
    with h1: st.markdown("**Trditev**")
    with h2: st.markdown("**L   1   2   3   4   5   M**")
    st.divider()

    for i, items in enumerate(st.session_state.shuffled):
        with st.container(border=True):
            st.markdown(f"#### Vprašanje {i+1} od 15")
            for color, text in items:
                # Trditev in Radio gumbi v ISTI VRSTI
                col_txt, col_rad = st.columns([1, 2])
                with col_txt:
                    st.markdown(f"{text}")
                with col_rad:
                    val = st.radio(f"R_{i}_{color}", OPTIONS, index=1, horizontal=True, key=f"q_{i}_{color}", label_visibility="collapsed")
                    all_inputs.append((color, SCORE_MAP[val]))
    
    st.divider()
    st.subheader("🎯 Coaching nastavitve za AI")
    c1, c2, c3 = st.columns(3)
    with c1:
        stres = st.checkbox("Analiza stresa", value=True)
        vodenje = st.checkbox("Strategije vodenja")
    with c2:
        pege = st.checkbox("Slepe pege")
        okolje = st.checkbox("Idealno okolje")
    with c3:
        komunikacija = st.checkbox("Nasprotni tip")
        tim = st.checkbox("Vrednost za tim")

    submitted = st.form_submit_button("USTVARI PROFESIONALNI PDF")

if submitted:
    if not polno_ime:
        st.error("Prosim, vnesite ime stranke!")
    else:
        # Matematika deljena s 15
        conscious = {c: sum([s for col, s in all_inputs if col == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}
        
        opt = ""
        if stres: opt += "Analiza stresa. "
        if vodenje: opt += "Vodenje. "
        if pege: opt += "Slepe pege. "
        if okolje: opt += "Okolje. "
        if komunikacija: opt += "Nasprotni tip. "
        if tim: opt += "Tim. "

        with st.spinner("Genie AI generira strokovno vsebino..."):
            ai_text = generiraj_premium_profil(polno_ime, conscious, less_conscious, opt)

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Naslovnica
            pdf.set_fill_color(0, 112, 192)
            pdf.rect(0, 0, 210, 50, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 24)
            pdf.cell(0, 35, clean_chars("INSIGHTS DISCOVERY OSEBNI PROFIL"), align='C', ln=True)
            
            pdf.set_text_color(0, 0, 0)
            pdf.ln(20)
            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 10, clean_chars(polno_ime), align='C', ln=True)
            
            # Interpretacija
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 15, clean_chars("Strokovna interpretacija"), ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 7, clean_chars(ai_text))
            
            # Rezultati
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 15, clean_chars("Rezultati energij (0-6)"), ln=True)
            for c in COLORS_MAP:
                diff = conscious[c] - less_conscious[c]
                pdf.cell(0, 10, clean_chars(f"- {c}: Zavedno {round(conscious[c],2)} | Manj zavedno {round(less_conscious[c],2)} | Tok: {round(diff,2)}"), ln=True)

            pdf_bytes = bytes(pdf.output())
            st.success("Analiza pripravljena!")
            st.download_button(f"📥 Prenesi PDF za {polno_ime}", pdf_bytes, f"Insights_Pro_{polno_ime}.pdf")
