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

# --- KONFIGURACIJA ---
COLORS_MAP = {"Cool Blue": "#0070C0", "Fiery Red": "#FF0000", "Earth Green": "#00B050", "Sunshine Yellow": "#FFFF00"}
OPPOSITES = {"Fiery Red": "Earth Green", "Earth Green": "Fiery Red", "Cool Blue": "Sunshine Yellow", "Sunshine Yellow": "Cool Blue"}
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generiraj_ai_profil(polno_ime, conscious, less_conscious, coaching_options):
    pref_flow = {c: round(conscious[c] - less_conscious[c], 2) for c in COLORS_MAP}
    prompt = f"""
    Ti si strokovnjak za Insights Discovery. Ustvari uradni osebni profil za: {polno_ime}.
    Zavedne energije (0-6): {conscious}
    Manj zavedne energije (0-6): {less_conscious}
    Preference Flow: {pref_flow}
    
    Navodila za vsebino:
    - Doloci tip (npr. Reformatorski direktor, Inspiracijski motivator).
    - Opisi osebni slog, interakcijo in tok preferenc.
    - Vkljuci odgovore na: {coaching_options}.
    Uporabljaj profesionalen ton po vzoru uradnih porocil.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Ti si strokovni Insights svetovalec Genie."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- UPORABNIŠKI VMESNIK ---
st.set_page_config(page_title="Insights Discovery Profiler", layout="wide")

st.markdown("""
    <style>
    .stRadio > div {
        flex-direction: row;
        justify-content: center;
    }
    .stForm {
        border: 3px solid #0070C0 !important;
        padding: 30px;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌈 Insights Discovery - Profesionalni Profiler")

# 1. ZDRUŽENO IME NA VRHU
polno_ime = st.text_input("Ime in priimek stranke", placeholder="Vpišite polno ime (npr. Janez Novak)")

# 15 SKLOPOV (Matematika prilagojena na 15)
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

if 'shuffled_items' not in st.session_state:
    st.session_state.shuffled_items = [[(c, q[k]) for c, k in zip(COLORS_MAP.keys(), ["B","R","G","Y"])] for q in raw_questions]

with st.form("insights_form"):
    all_inputs = []
    for i, items in enumerate(st.session_state.shuffled_items):
        with st.container(border=True):
            st.markdown(f"### **SKLOP {i+1}**")
            cols = st.columns(4)
            for idx, (color, text) in enumerate(items):
                with cols[idx]:
                    st.markdown(f"<div style='height: 45px; font-weight: bold; text-align: center;'>{text}</div>", unsafe_allow_html=True)
                    val = st.radio(f"Lestvica_{i}_{color}", OPTIONS, index=1, horizontal=True, key=f"q_{i}_{color}", label_visibility="collapsed")
                    all_inputs.append((color, SCORE_MAP[val]))
    
    st.divider()
    st.subheader("🎯 Modul za Coaching in Interpretacijo")
    c_stres = st.checkbox("Analiza vedenja pod stresom", value=True)
    c_vodenje = st.checkbox("Strategije za vodenje te osebe")
    c_komunikacija = st.checkbox("Komunikacija z nasprotnim tipom")
    c_blind = st.checkbox("Prepoznavanje slepih peg")
    c_team = st.checkbox("Prispevek k timski dinamiki")
    
    submitted = st.form_submit_button("GENERIRAJ PROFESIONALNI AI PROFIL")

if submitted:
    if not polno_ime:
        st.error("Prosim, vnesite ime na vrhu strani!")
    else:
        # MATEMATIKA: Delimo s 15 za skalo 0-6
        conscious = {c: sum([s for col, s in all_inputs if col == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}
        
        coaching_txt = ""
        if c_stres: coaching_txt += "Odziv na stres. "
        if c_vodenje: coaching_txt += "Nasveti za vodjo. "
        if c_komunikacija: coaching_txt += "Komunikacija z nasprotnim tipom. "
        if c_blind: coaching_txt += "Slepe pege. "
        if c_team: coaching_txt += "Vrednost za tim. "

        with st.spinner("Genie AI pripravlja PDF po meri..."):
            ai_vsebina = generiraj_ai_profil(polno_ime, conscious, less_conscious, coaching_txt)

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Naslovnica
            pdf.add_page()
            pdf.set_fill_color(0, 112, 192)
            pdf.rect(0, 0, 210, 297, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 35)
            pdf.cell(0, 100, "INSIGHTS DISCOVERY", align='C', ln=True)
            pdf.set_font("Helvetica", "", 20)
            pdf.cell(0, 15, clean_chars(f"OSEBNI PROFIL: {polno_ime}"), align='C', ln=True)
            
            # AI Vsebina
            pdf.add_page()
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 15, clean_chars("Temeljno poglavje in AI interpretacija"), ln=True)
            pdf.ln(5)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 7, clean_chars(ai_vsebina))
            
            # Graficni povzetek
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 15, clean_chars("Pregled vrednosti barvnih energij"), ln=True)
            pdf.ln(5)
            for c in COLORS_MAP:
                diff = conscious[c] - less_conscious[c]
                pdf.cell(0, 10, clean_chars(f"{c}: Zavedno {round(conscious[c],2)} | Nezavedno {round(less_conscious[c],2)} | Tok: {round(diff,2)}"), ln=True)

            pdf_output = bytes(pdf.output())
            st.success("Analiza končana!")
            st.download_button("📥 Prenesi PDF poročilo", pdf_output, f"Insights_{polno_ime}.pdf")
