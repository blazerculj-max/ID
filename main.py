import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# --- KONFIGURACIJA ---
EMAIL_SENDER = "blazerculj@gmail.com"
EMAIL_PASSWORD = "hsmq lbkk huny bfdk" # <--- SEM VPISI GESLO
EMAIL_RECEIVER = "blazerculj@gmail.com"

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

# 15 NOVIH SKLOPOV TRDITEV
raw_questions = [
    {"B": "Sistematičen in dosleden", "R": "Neposreden in prodoren", "G": "Razumevajoč in ustrežljiv", "Y": "Živahen in komunikativen"},
    {"B": "Objektiven opazovalec", "R": "Močan in neodvisen", "G": "Zanesljiv sopotnik", "Y": "Navdihujoč govorec"},
    {"B": "Logičen in preudaren", "R": "Hiter in odločen", "G": "Prijazen in skrben", "Y": "Sproščen in igriv"},
    {"B": "Pozoren na podrobnosti", "R": "Usmerjen h končnemu cilju", "G": "Uravnotežen in potrpežljiv", "Y": "Ustvarjalen in optimističen"},
    {"B": "Analitičen in distanciran", "R": "Energičen in tekmovalen", "G": "Iskren in lojalen", "Y": "Družaben in prepričljiv"},
    {"B": "Strokovno podkovan", "R": "Drzen pri odločanju", "G": "Uravnotežen in nežen", "Y": "Poln novih idej"},
    {"B": "Premišljen strateg", "R": "Dinamičen vodja", "G": "Podporen poslušalec", "Y": "Navdušen motivator"},
    {"B": "Metodičen in urejen", "R": "Avtoritativen in fokisiran", "G": "Diplomatski in miren", "Y": "Priljubljen in odprt"},
    {"B": "Previdno previden", "R": "Rezultatno zahteven", "G": "Stabilno zanesljiv", "Y": "Zgovorno prijazen"},
    {"B": "Uraden in zadržan", "R": "Vpliven in hiter", "G": "Topel in miren", "Y": "Duhovit in opazen"},
    {"B": "Temeljit preučevalec", "R": "Samozavesten akter", "G": "Zvest sodelavec", "Y": "Domišljijski vizionar"},
    {"B": "Resen in dejstven", "R": "Vztrajen in oster", "G": "Sodelovalen in toleranten", "Y": "Zabaven in prilagodljiv"},
    {"B": "Umirjen in natančen", "R": "Samostojen in močan", "G": "Skrben za odnose", "Y": "Povezovalen in aktiven"},
    {"B": "Zbran in analitičen", "R": "Ambiciozen in hiter", "G": "Prilagodljiv in blag", "Y": "Zabaven in zgovoren"},
    {"B": "Fokusiran na proces", "R": "Fokusiran na zmago", "G": "Fokusiran na ljudi", "Y": "Fokusiran na prihodnost"}
]

st.set_page_config(page_title="Insights Discovery - 15", layout="centered")

st.title("🌈 Insights Discovery Profiler")
ime = st.text_input("Vaše ime")
priimek = st.text_input("Vaš priimek")

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
    
    submitted = st.form_submit_button("IZRAČUNAJ IN POŠLJI PROFIL")

if submitted:
    if not ime or not priimek:
        st.error("Prosim, vpišite ime in priimek!")
    else:
        # IZRAČUN (Povprečje na 15 vprašanj)
        conscious = {c: sum([score for color, score in all_user_inputs if color == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}

        # PDF GENERIRANJE
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Stran 1: Naslovnica
        pdf.add_page()
        pdf.set_font("Arial", 'B', 25)
        pdf.cell(200, 60, "Insights Discovery Osebni Profil", ln=True, align='C')
        pdf.set_font("Arial", '', 18)
        pdf.cell(200, 20, f"Pripravljeno za: {ime} {priimek}", ln=True, align='C')
        
        # Stran 2: Zavedna Persona
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "1. Zavedna Persona (Conscious)", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, "Zavedna persona predstavlja stil vedenja, ki ga namenoma izbirate in kažeta v svojem delovnem okolju.")
        for c, v in conscious.items():
            pdf.cell(200, 10, f"- {c}: {round(v, 2)} od 6.00", ln=True)

        # Stran 3: Nezavedna Persona
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "2. Nezavedna Persona (Less Conscious)", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, "Nezavedna persona odraža vaš naravni odziv, ko niste pod pritiskom ali ko se odzivate instinktivno.")
        for c, v in less_conscious.items():
