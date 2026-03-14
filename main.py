import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

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

# 15 SKLOPOV VPRAŠANJ
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

# Povezava z Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

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
    
    submitted = st.form_submit_button("ODDAJ IN IZRAČUNAJ PROFIL")

if submitted:
    if not ime or not priimek:
        st.error("Prosim, vnesite ime in priimek!")
    else:
        # 1. IZRAČUN
        conscious = {c: sum([score for color, score in all_user_inputs if color == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}

        # 2. SHRANJEVANJE V GOOGLE SHEETS
        try:
            # Priprava nove vrstice za tabelo
            new_entry = {
                "Ime": ime,
                "Priimek": priimek,
                "Datum": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "B_Zavedno": round(conscious["Cool Blue"], 2),
                "R_Zavedno": round(conscious["Fiery Red"], 2),
                "G_Zavedno": round(conscious["Earth Green"], 2),
                "Y_Zavedno": round(conscious["Sunshine Yellow"], 2),
                "B_Nezavedno": round(less_conscious["Cool Blue"], 2),
                "R_Nezavedno": round(less_conscious["Fiery Red"], 2),
                "G_Nezavedno": round(less_conscious["Earth Green"], 2),
                "Y_Nezavedno": round(less_conscious["Sunshine Yellow"], 2)
            }
            
            # Branje obstoječih podatkov
            existing_data = conn.read(worksheet="Insights_Rezultati")
            updated_df = pd.concat([existing_data, pd.DataFrame([new_entry])], ignore_index=True)
            
            # Posodobitev tabele
            conn.update(worksheet="Insights_Rezultati", data=updated_df)
            st.success("Vaši rezultati so varno shranjeni v bazi.")
        except Exception as e:
            st.warning(f"Podatki niso bili shranjeni v bazo, vendar jih vidite spodaj: {e}")

        # 3. PRIKAZ REZULTATOV NA EKRANU (Insights Grafi)
        st.header(f"Rezultat za {ime} {priimek}")
        
        # Tukaj bova kasneje dodala še grafe, ki sva jih imela prej
        st.write("Vaše zavedne vrednosti:", conscious)
        st.write("Vaše nezavedne vrednosti:", less_conscious)
