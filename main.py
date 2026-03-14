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
    Ti si Insights Discovery strokovnjak. Ustvari uradni osebni profil za: {polno_ime}.
    Zavedne energije: {conscious}
    Manj zavedne energije: {less_conscious}
    Tok preferenc: {pref_flow}
    Struktura: Uvod, Osebni stil, Interakcija, Tok preferenc. 
    Dodaj coaching analizo za: {coaching_options}.
    Uporabljaj terminologijo kot v uradnih porocilih (npr. Reformatorski direktor).
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Ti si strokovni Insights svetovalec Genie."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- UPORABNIŠKI VMESNIK ---
st.set_page_config(page_title="Insights Discovery - Evaluator", layout="wide")

# CSS za vodoravno poravnavo radio gumbov in lepše okvirje
st.markdown("""
    <style>
    div.row-widget.stRadio > div {
        flex-direction: row;
        justify-content: center;
    }
    .stForm {
        border: 2px solid #0070C0 !important;
        padding: 25px;
        border-radius: 12px;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌈 Insights Discovery - Profesionalni Profiler")

polno_ime = st.text_input("Ime in priimek stranke", placeholder="Vnesite polno ime za PDF poročilo...")

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
    
    # Glava vprašalnika
    c_head1, c_head2, c_head3 = st.columns([2, 3, 1])
    with c_head1: st.markdown("**Trditev**")
    with c_head2: st.markdown("<p style='text-align:center;'><b>L  1  2  3  4  5  M</b></p>", unsafe_allow_html=True)
    
    st.divider()

    for i, items in enumerate(st.session_state.shuffled_items):
        st.markdown(f"#### SKLOP {i+1}")
        with st.container(border=True):
            for idx, (color, text) in enumerate(items):
                # Vodoravna postavitev: Trditev -> Radio gumbi
                col_text, col_radio = st.columns([2, 3])
                with col_text:
                    st.markdown(f"**{text}**")
                with col_radio:
                    val = st.radio(f"R_{i}_{color}", OPTIONS, index=1, horizontal=True, key=f"q_{i}_{color}", label_visibility="collapsed")
                    all_inputs.append((color, SCORE_MAP[val]))
        st.write("") # Razmik med sklopi

    st.divider()
    st.subheader("🎯 Coaching vprašanja za Genie AI")
    cols_ai = st.columns(3)
    with cols_ai[0]:
        c_stres = st.checkbox("Analiza stresa", value=True)
        c_vodenje = st.checkbox("Nasveti za vodenje")
    with cols_ai[1]:
        c_komunikacija = st.checkbox("Komunikacija z nasprotnim tipom")
        c_okolje = st.checkbox("Idealno delovno okolje")
    with cols_ai[2]:
        c_blind = st.checkbox("Slepe pege (Blind Spots)")
        c_team = st.checkbox("Prispevek k timu")
    
    submitted = st.form_submit_button("GENERIRAJ PROFESIONALNI PROFIL")

if submitted:
    if not polno_ime:
        st.error("Prosim, vpišite ime na vrhu!")
    else:
        # MATEMATIKA: Deljeno s 15
        conscious = {c: sum([s for col, s in all_inputs if col == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}
        
        coaching_txt = ""
        if c_stres: coaching_txt += "Odziv na stres. "
        if c_vodenje: coaching_txt += "Vodenje. "
        if c_komunikacija: coaching_txt += "Nasprotni tip. "
        if c_okolje: coaching_txt += "Okolje in motivacija. "
        if c_blind: coaching_txt += "Slepe pege. "
        if c_team: coaching_txt += "Timski prispevek. "

        with st.spinner("Genie AI pripravlja PDF poročilo..."):
            ai_vsebina = generiraj_ai_profil(polno_ime, conscious, less_conscious, coaching_txt)

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Naslovnica
            pdf.add_page()
            pdf.set_fill_color(0, 112, 192)
            pdf.rect(0, 0, 210, 297, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 30)
            pdf.cell(0, 100, "INSIGHTS DISCOVERY", align='C', ln=True)
            pdf.set_font("Helvetica", "", 18)
            pdf.cell(0, 20, clean_chars(f"OSEBNI PROFIL: {polno_ime}"), align='C', ln=True)
            
            # AI Analiza
            pdf.add_page()
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 15, clean_chars("Analiza osebnega sloga"), ln=True)
            pdf.ln(5)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 7, clean_chars(ai_vsebina))
            
            # Številke in Tok preferenc
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, clean_chars("Rezultati energij (Skala 0-6)"), ln=True)
            pdf.ln(5)
            for c in COLORS_MAP:
                diff = conscious[c] - less_conscious[c]
                pdf.cell(0, 10, clean_chars(f"{c}: Zavedno {round(conscious[c],2)} | Manj zavedno {round(less_conscious[c],2)} | Tok: {round(diff,2)}"), ln=True)

            pdf_output = bytes(pdf.output())
            st.success("Profil uspešno generiran!")
            st.download_button("📥 Prenesi celoten PDF poročilo", pdf_output, f"Insights_{polno_ime.replace(' ', '_')}.pdf")
