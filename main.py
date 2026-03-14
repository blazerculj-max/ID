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

def generiraj_ai_profil(ime, conscious, less_conscious, coaching_options):
    """Generira strukturirano vsebino z upoštevanjem coaching izbir."""
    pref_flow = {c: round(conscious[c] - less_conscious[c], 2) for c in COLORS_MAP}
    
    prompt = f"""
    Ti si Insights Discovery strokovnjak. Ustvari uradni osebni profil (Foundation Chapter) za: {ime}.
    Zavedne energije: {conscious}
    Manj zavedne energije: {less_conscious}
    Tok preferenc (Preference Flow): {pref_flow}
    
    Struktura PDF poročila naj obsega:
    1. UVOD: Določi tip (npr. Reformatorski direktor) in na kratko opiši bistvo.
    2. OSEBNI STIL: Podroben opis vedenja.
    3. INTERAKCIJA: Kako oseba komunicira.
    4. TOK PREFERENC: Interpretacija razlik med personama (ali se oseba kje prilagaja?).
    
    DODATNE COACHING ANALIZE (vključi le izbrane):
    {coaching_options}
    
    Uporabi profesionalen ton in terminologijo iz tvojih uradnih datotek.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Ti si profesionalni Insights svetovalec."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- UI ---
st.set_page_config(page_title="Insights Discovery - Coaching Tool", layout="wide")
st.title("🌈 Insights Discovery - Profesionalni Profiler")

with st.sidebar:
    st.header("Podatki o stranki")
    ime = st.text_input("Ime")
    priimek = st.text_input("Priimek")
    st.divider()
    st.info("Izpolnite vseh 15 sklopov trditev spodaj.")

# 15 sklopov (uporabljamo tvojih 15 sklopov)
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
        with st.container(border=True): # Boldani okvir okoli sklopa
            st.markdown(f"#### **Sklop {i+1} od 15**")
            cols = st.columns(4)
            for idx, (color, text) in enumerate(items):
                with cols[idx]:
                    st.write(f"**{text}**")
                    val = st.radio("Izberi:", OPTIONS, index=1, horizontal=True, key=f"q_{i}_{color}", label_visibility="collapsed")
                    all_inputs.append((color, SCORE_MAP[val]))
    
    st.divider()
    st.subheader("🎯 Coaching modul (označi relevantne vsebine za profil)")
    c_stres = st.checkbox("Analiza odziva na stres", value=True)
    c_vodenje = st.checkbox("Nasveti za vodenje te osebe")
    c_sodelovanje = st.checkbox("Kako komunicirati z nasprotnim tipom?")
    c_motiviranje = st.checkbox("Glavni motivatorji in idealno delovno okolje")
    c_slepe_pege = st.checkbox("Možne slepe pege v vedenju")
    
    submitted = st.form_submit_button("USTVARI PROFESIONALNI AI PROFIL")

if submitted:
    if not ime or not priimek:
        st.error("Prosim, vnesite ime in priimek v stranskem meniju!")
    else:
        conscious = {c: sum([s for col, s in all_inputs if col == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}
        
        coaching_txt = ""
        if c_stres: coaching_txt += "- Podroben odziv na stres. "
        if c_vodenje: coaching_txt += "- Strategije za ucinkovito vodenje te osebe. "
        if c_sodelovanje: coaching_txt += "- Interakcija z nasprotnim barvnim tipom. "
        if c_motiviranje: coaching_txt += "- Idealno delovno okolje in motivacija. "
        if c_slepe_pege: coaching_txt += "- Morebitne slepe pege (Blind Spots). "

        with st.spinner("Genie AI pripravlja strukturirano poročilo po vzoru Insights Discovery..."):
            ai_vsebina = generiraj_ai_profil(ime, conscious, less_conscious, coaching_txt)

            # PDF GENERIRANJE
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Naslovnica
            pdf.add_page()
            pdf.set_fill_color(0, 112, 192) # Insights modra
            pdf.rect(0, 0, 210, 297, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 35)
            pdf.cell(0, 100, "INSIGHTS DISCOVERY", align='C', ln=True)
            pdf.set_font("Helvetica", "", 20)
            pdf.cell(0, 20, clean_chars(f"OSEBNI PROFIL"), align='C', ln=True)
            pdf.ln(40)
            pdf.set_font("Helvetica", "B", 24)
            pdf.cell(0, 10, clean_chars(f"{ime} {priimek}"), align='C', ln=True)
            
            # Vsebina
            pdf.add_page()
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, clean_chars("Temeljno poglavje in interpretacija"), ln=True)
            pdf.ln(5)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 7, clean_chars(ai_vsebina))
            
            # Grafi in vrednosti
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, clean_chars("Pregled barvnih energij in Tok preferenc"), ln=True)
            pdf.ln(5)
            pdf.set_font("Helvetica", "", 11)
            for c in COLORS_MAP:
                diff = conscious[c] - less_conscious[c]
                pdf.cell(0, 10, clean_chars(f"- {c}: Zavedno {round(conscious[c],2)} | Nezavedno {round(less_conscious[c],2)} | Premik: {round(diff,2)}"), ln=True)

            pdf_output = bytes(pdf.output())
            
            st.success("Profil je pripravljen!")
            st.download_button(
                label="📥 Prenesi razširjen PDF profil (Coaching Edition)",
                data=pdf_output,
                file_name=f"Insights_Coaching_{ime}.pdf",
                mime="application/pdf"
            )
