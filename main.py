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

# --- POMOŽNA FUNKCIJA ZA ŠUMNIK (fpdf fix) ---
def clean_chars(text):
    """Zamenja šumnike, ker standardni PDF fonti v fpdf2 ne podpirajo Unicode brez zunanjih TTF datotek."""
    mapping = {"č": "c", "š": "s", "ž": "z", "Č": "C", "Š": "S", "Ž": "Z"}
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

# --- KONFIGURACIJA ---
EMAIL_SENDER = "blazerculj@gmail.com"
EMAIL_PASSWORD = "vpisi_svoj_google_app_password" # <--- TUKAJ VPISI SVOJE GESLO
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

st.set_page_config(page_title="Insights Discovery - 15", layout="centered")

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
    
    submitted = st.form_submit_button("IZRAČUNAJ IN POŠLJI PROFIL")

if submitted:
    if not ime or not priimek:
        st.error("Prosim, vnesite ime in priimek!")
    else:
        # 1. IZRAČUN
        conscious = {c: sum([score for color, score in all_user_inputs if color == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}

        # 2. PDF GENERIRANJE
        pdf = FPDF()
        pdf.add_page()
        
        # Naslovnica
        pdf.set_font("Helvetica", "B", 25)
        pdf.cell(0, 60, clean_chars("Insights Discovery Osebni Profil"), new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.set_font("Helvetica", "", 18)
        pdf.cell(0, 20, clean_chars(f"Pripravljeno za: {ime} {priimek}"), new_x="LMARGIN", new_y="NEXT", align='C')
        
        # Stran 2: Zavedna Persona
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, clean_chars("1. Zavedna Persona (Conscious)"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 12)
        pdf.ln(5)
        text1 = "Zavedna persona predstavlja stil vedenja, ki ga namenoma izbirate in kazete v svojem delovnem okolju."
        pdf.multi_cell(0, 10, clean_chars(text1))
        pdf.ln(5)
        for c, v in conscious.items():
            pdf.cell(0, 10, clean_chars(f"- {c}: {round(v, 2)} od 6.00"), new_x="LMARGIN", new_y="NEXT")

        # Stran 3: Nezavedna Persona
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, clean_chars("2. Nezavedna Persona (Less Conscious)"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 12)
        pdf.ln(5)
        text2 = "Nezavedna persona odraza vas naravni odziv, ko niste pod pritiskom ali ko se odzivate instinktivno."
        pdf.multi_cell(0, 10, clean_chars(text2))
        pdf.ln(5)
        for c, v in less_conscious.items():
            pdf.cell(0, 10, clean_chars(f"- {c}: {round(v, 2)} od 6.00"), new_x="LMARGIN", new_y="NEXT")

        # Stran 4: Preference Flow
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, clean_chars("3. Preference Flow (Analiza premika)"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 12)
        pdf.ln(5)
        text3 = "Prikazuje razliko med vaso naravno energijo in energijo, ki jo kazete navzven."
        pdf.multi_cell(0, 10, clean_chars(text3))
        pdf.ln(5)
        for c in COLORS_MAP:
            diff = conscious[c] - less_conscious[c]
            status = "Poudarjanje" if diff >= 0 else "Zadrzevanje"
            pdf.cell(0, 10, clean_chars(f"- {c}: Premik {round(diff, 2)} ({status})"), new_x="LMARGIN", new_y="NEXT")

        # Ime datoteke brez šumnikov za varnost
        safe_filename = clean_chars(f"{ime}_{priimek}.pdf").replace(" ", "_")
        pdf.output(safe_filename)

        # 3. POŠILJANJE
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECEIVER
            msg['Subject'] = f"Nov Insights Profil: {ime} {priimek}" # E-mail naslov lahko ima šumnike
            msg.attach(MIMEText(f"V priponki je PDF profil za {ime} {priimek}.", 'plain'))

            with open(safe_filename, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {safe_filename}")
                msg.attach(part)

            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(EMAIL_SENDER, EMAIL_PASSWORD)
            s.send_message(msg)
            s.quit()
            
            st.success(f"Profil {safe_filename} je uspešno poslan!")
            os.remove(safe_filename)
        except Exception as e:
            st.error(f"Napaka pri pošiljanju: {e}")
