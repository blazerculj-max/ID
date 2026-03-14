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

# --- MASTER PROMPT (Možgani svetovalca) ---
MASTER_SYSTEM_PROMPT = """
Ti si vrhunski Insights Discovery svetovalec z globokim razumevanjem Jungovih psiholoških tipov.
Tvoja naloga je interpretirati rezultate barvnih energij (Cool Blue, Fiery Red, Earth Green, Sunshine Yellow).

NAVODILA ZA STIL IN FORMAT:
1. Ton naj bo profesionalen, analitičen, spodbuden in usmerjen v razvoj.
2. Vsebino obvezno strukturiraj v jasna poglavja.
3. Uporabljaj ALINEJE (bullet points) za vse ključne ugotovitve. Vsaka alineja naj bo vsebinsko bogata (ne le ena beseda).
4. Interpretiraj "Tok preferenc" (Preference Flow) – razliko med zavedno in manj zavedno persono.
5. Uporabljaj uradno terminologijo (npr. Reformatorski direktor, Inspiracijski motivator, Koordinacijski opazovalec).

STRUKTURA ODGOVORA:
- TIP OSEBNOSTI: Določi primarno pozicijo na kolesu.
- OSEBNI STIL: Kako oseba deluje (3-4 alineje).
- INTERAKCIJA Z DRUGIMI: Komunikacija in vpliv na ekipo (3-4 alineje).
- TOK PREFERENC: Kaj nam pove premik med naravnim in prilagojenim vedenjem.
- COACHING MODULI: Podrobno razdelaj izbrane dodatne teme (Stres, Vodenje, Slepe pege).
"""

# --- KONFIGURACIJA ---
COLORS_MAP = {"Cool Blue": "#0070C0", "Fiery Red": "#FF0000", "Earth Green": "#00B050", "Sunshine Yellow": "#FFFF00"}
OPPOSITES = {"Fiery Red": "Earth Green", "Earth Green": "Fiery Red", "Cool Blue": "Sunshine Yellow", "Sunshine Yellow": "Cool Blue"}
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generiraj_premium_profil(polno_ime, conscious, less_conscious, coaching_txt):
    pref_flow = {c: round(conscious[c] - less_conscious[c], 2) for c in COLORS_MAP}
    
    user_content = f"""
    Ustvari osebni profil za: {polno_ime}.
    Zavedne energije: {conscious}
    Manj zavedne energije: {less_conscious}
    Tok preferenc (Preference Flow): {pref_flow}
    
    Vključi naslednje coaching module:
    {coaching_txt}
    
    Prosim, uporabi alineje in bodi strokoven.
    """
    
    response = client.chat.completions.create(
        model="gpt-4-turbo", # Najmočnejši model za najboljšo strukturo
        messages=[
            {"role": "system", "content": MASTER_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# --- UI APPLIKACIJE ---
st.set_page_config(page_title="Insights Discovery Expert", layout="wide")
st.title("🌈 Insights Discovery - Profesionalni Profiler")

polno_ime = st.text_input("Ime in priimek stranke", placeholder="Vnesite polno ime...")

# 15 sklopov trditev (Matematika deljena s 15)
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
    for i, items in enumerate(st.session_state.shuffled):
        with st.container(border=True):
            st.markdown(f"#### SKLOP {i+1}")
            cols = st.columns(4)
            for idx, (color, text) in enumerate(items):
                with cols[idx]:
                    st.markdown(f"<div style='height: 40px; font-weight: bold;'>{text}</div>", unsafe_allow_html=True)
                    val = st.radio(f"R_{i}_{color}", OPTIONS, index=1, horizontal=True, key=f"q_{i}_{color}", label_visibility="collapsed")
                    all_inputs.append((color, SCORE_MAP[val]))
    
    st.divider()
    st.subheader("🎯 Coaching nastavitve za AI (Master Prompt)")
    c1, c2, c3 = st.columns(3)
    with c1:
        stres = st.checkbox("Analiza stresa in pritiska", value=True)
        vodenje = st.checkbox("Strategije za vodjo")
    with c2:
        pege = st.checkbox("Slepe pege (Blind spots)")
        okolje = st.checkbox("Idealno delovno okolje")
    with c3:
        komunikacija = st.checkbox("Komunikacija z nasprotnim tipom")
        tim = st.checkbox("Vrednost za tim")

    submitted = st.form_submit_button("USTVARI PROFESIONALNI PDF PRODUKT")

if submitted:
    if not polno_ime:
        st.error("Prosim, vnesite ime stranke!")
    else:
        conscious = {c: sum([s for col, s in all_inputs if col == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}
        
        opt = ""
        if stres: opt += "ANALIZA STRESA: Podrobno v alinejah. "
        if vodenje: opt += "VODENJE: Navodila za ucinkovito upravljanje. "
        if pege: opt += "SLEPE PEGE: Na kaj mora biti oseba pozorna. "
        if okolje: opt += "OKOLJE: Kje bo oseba najbolj cvetela. "
        if komunikacija: opt += "NASPROTNI TIP: Kako komunicirati z nekom, ki je popolnoma drugacen. "
        if tim: opt += "TIM: Prispevek k ekipi. "

        with st.spinner("Genie AI pripravlja strokovno vsebino..."):
            ai_text = generiraj_premium_profil(polno_ime, conscious, less_conscious, opt)

            # --- PDF OBLIKOVANJE (Produktni videz) ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # NASLOVNICA
            pdf.add_page()
            pdf.set_fill_color(0, 112, 192) # Insights modra
            pdf.rect(0, 0, 210, 60, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 26)
            pdf.cell(0, 45, clean_chars("INSIGHTS DISCOVERY OSEBNI PROFIL"), align='C', ln=True)
            
            pdf.set_text_color(0, 0, 0)
            pdf.ln(30)
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(0, 10, clean_chars(polno_ime), align='C', ln=True)
            pdf.set_font("Helvetica", "I", 14)
            pdf.cell(0, 10, "Temeljno poglavje", align='C', ln=True)
            
            # VSEBINA
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(0, 112, 192)
            pdf.cell(0, 15, clean_chars("Strokovna interpretacija profila"), ln=True)
            pdf.ln(5)
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 11)
            # AI tekst vsebuje alineje, fpdf2 jih bo pravilno izpisal
            pdf.multi_cell(0, 7, clean_chars(ai_text))
            
            # STRAN Z REZULTATI
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 15, clean_chars("Pregled barvnih energij (0.0 - 6.0)"), ln=True)
            pdf.set_font("Helvetica", "", 12)
            for c in COLORS_MAP:
                diff = conscious[c] - less_conscious[c]
                pdf.cell(0, 12, clean_chars(f"- {c}: Zavedno {round(conscious[c],2)} | Manj zavedno {round(less_conscious[c],2)} | Tok: {round(diff,2)}"), ln=True)

            pdf_bytes = bytes(pdf.output())
            st.success("Produkt je pripravljen za prenos!")
            st.download_button(f"📥 Prenesi PDF za {polno_ime}", pdf_bytes, f"Insights_Pro_{polno_ime}.pdf", "application/pdf")
