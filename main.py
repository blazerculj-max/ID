import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random
from fpdf import FPDF

# --- POMOŽNA FUNKCIJA ZA ŠUMNIK ---
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

# Profesionalni Insights opisi za PDF
INSIGHTS_DESCS = {
    "Cool Blue": "Cool Blue (Snezno modra): Vase vedenje je objektivno, analiticno in preudarno. Cenite dejstva, tocnost in logiko.",
    "Fiery Red": "Fiery Red (Ognjeno rdeca): Ste usmerjeni k rezultatom, odlocni in mocni. Vase vedenje je neposredno in aktivno.",
    "Earth Green": "Earth Green (Zemeljsko zelena): Vase vedenje je skrbno, harmonicno in potrpezljivo. Cenite odnose in osebne vrednote.",
    "Sunshine Yellow": "Sunshine Yellow (Soncno rumena): Ste druzabni, navduseni in optimisticni. Vase vedenje je ustvarjalno in dinamicno."
}

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

st.set_page_config(page_title="Insights Discovery - Blaž", layout="centered")

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
    submitted = st.form_submit_button("IZRAČUNAJ MOJ PROFIL")

if submitted:
    if not ime or not priimek:
        st.error("Prosim, vnesite ime in priimek!")
    else:
        conscious = {c: sum([score for color, score in all_user_inputs if color == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}

        st.success("Vaša analiza je končana!")

        # --- PDF GENERIRANJE ---
        pdf = FPDF()
        
        # 1. STRAN: Naslovnica v slogu Insights
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 26)
        pdf.cell(0, 80, clean_chars("Insights Discovery"), align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 10, clean_chars("Osebni profil"), align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(20)
        pdf.set_font("Helvetica", "", 16)
        pdf.cell(0, 10, clean_chars(f"{ime} {priimek}"), align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "I", 12)
        pdf.cell(0, 10, clean_chars("Temeljno poglavje"), align='C', new_x="LMARGIN", new_y="NEXT")

        # 2. STRAN: Uvod v barvne energije
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 15, clean_chars("Vasa zavedna persona"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, clean_chars("Zavedna persona predstavlja stil vedenja, ki ga namenoma izbirate in ga kazete v svojem delovnem okolju. Spodaj so vase vrednosti energij na lestvici od 0 do 6:"))
        pdf.ln(5)
        for c, v in conscious.items():
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, clean_chars(f"{c}: {round(v, 2)}"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, clean_chars(INSIGHTS_DESCS[c]))
            pdf.ln(2)

        # 3. STRAN: Manj zavedna persona
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 15, clean_chars("Vasa manj zavedna persona"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, clean_chars("Manj zavedna persona odraza vas naravni slog in instinktivne odzive, ko niste pod pritiskom okolice."))
        pdf.ln(10)
        for c, v in less_conscious.items():
            pdf.cell(0, 8, clean_chars(f"{c}: {round(v, 2)} / 6.00"), border="B", new_x="LMARGIN", new_y="NEXT")

        # 4. STRAN: Preference Flow
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 15, clean_chars("Preference Flow"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, clean_chars("Preference Flow prikazuje razliko med vaso naravno energijo in energijo, ki jo kazete navzven. Pozitivna vrednost pomeni povecano zavestno rabo energije."))
        pdf.ln(5)
        for c in COLORS_MAP:
            diff = conscious[c] - less_conscious[c]
            pdf.cell(0, 10, clean_chars(f"{c}: Premik {round(diff, 2)}"), new_x="LMARGIN", new_y="NEXT")

        pdf_bytes = bytes(pdf.output())
        
        st.divider()
        st.download_button(
            label="📥 Prenesi PDF Osebni profil",
            data=pdf_bytes,
            file_name=f"Insights_{ime}_{priimek}.pdf",
            mime="application/pdf"
        )
