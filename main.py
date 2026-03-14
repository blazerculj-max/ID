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

# --- KONFIGURACIJA E-POŠTE ---
EMAIL_SENDER = "blazerculj@gmail.com"
# Tukaj boš moral vpisati "App Password" (glej navodila spodaj)
EMAIL_PASSWORD = "hsmq lbkk huny bfdk" 
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

st.set_page_config(page_title="Insights Discovery Profiler", layout="centered")

# 1. Vnos osebnih podatkov
st.title("🌈 Insights Discovery Profiler")
col_name, col_surname = st.columns(2)
ime = col_name.text_input("Ime")
priimek = col_surname.text_input("Priimek")

# --- VPRAŠALNIK (Vseh 25 sklopov - skrajšano za primer, uporabi svoje) ---
raw_questions = [
    {"B": "Natančen", "R": "Usmerjen v rezultate", "G": "Diplomatski", "Y": "Navdušen"},
    # ... (Vključi vseh 25 vprašanj tukaj)
] * 25
raw_questions = raw_questions[:25]

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
        st.subheader(f"Sklop {i+1} od 25")
        for idx, (color, text) in enumerate(items):
            val = st.radio(f"**{text}**", options=OPTIONS, index=1, horizontal=True, key=f"q_{i}_{color}")
            all_user_inputs.append((color, SCORE_MAP[val]))
    
    submitted = st.form_submit_button("GENERIRAJ IN POŠLJI PROFIL")

if submitted:
    if not ime or not priimek:
        st.error("Prosim, vnesite ime in priimek!")
    else:
        # 2. Izračun
        conscious = {c: 0 for c in COLORS_MAP}
        for color, score in all_user_inputs:
            conscious[color] += score
        for c in conscious: conscious[c] /= 25

        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}

        # 3. Ustvarjanje PDF dokumenta
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Stran 1: Naslovnica
        pdf.add_page()
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(200, 60, "Insights Discovery Profil", ln=True, align='C')
        pdf.set_font("Arial", '', 18)
        pdf.cell(200, 20, f"Osebno poročilo za: {ime} {priimek}", ln=True, align='C')
        
        # Stran 2: Zavedni profil
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "Vaša zavedna persona (Conscious)", ln=True)
        pdf.set_font("Arial", '', 12)
        for c, v in conscious.items():
            pdf.cell(200, 10, f"{c}: {round(v, 2)}", ln=True)
            
        # Stran 3: Nezavedni profil
        pdf.add_page()
        pdf.cell(200, 10, "Vaša nezavedna persona (Less Conscious)", ln=True)
        for c, v in less_conscious.items():
            pdf.cell(200, 10, f"{c}: {round(v, 2)}", ln=True)

        # Stran 4: Preference Flow
        pdf.add_page()
        pdf.cell(200, 10, "Preference Flow (Analiza prilagajanja)", ln=True)
        for c in COLORS_MAP:
            diff = conscious[c] - less_conscious[c]
            pdf.cell(200, 10, f"{c}: Premik {round(diff, 2)}", ln=True)

        filename = f"{ime}_{priimek}.pdf"
        pdf.output(filename)

        # 4. Pošiljanje E-pošte
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECEIVER
            msg['Subject'] = f"Insights Profil: {ime} {priimek}"
            
            body = f"Pozdravljen Blaž,\n\nV priponki je nov Insights profil za osebo {ime} {priimek}."
            msg.attach(MIMEText(body, 'plain'))

            with open(filename, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {filename}")
                msg.attach(part)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()

            st.success(f"Profil za {ime} {priimek} je bil uspešno ustvarjen in poslan na blazerculj@gmail.com!")
            os.remove(filename) # Počiščimo datoteko s strežnika
        except Exception as e:
            st.error(f"Prišlo je do napake pri pošiljanju: {e}")
