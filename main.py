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

def generiraj_kompleksno_analizo(ime, conscious, less_conscious, dodatna_vprasanja=""):
    """Generira strukturirano vsebino po vzoru uradnih Insights profilov."""
    pref_flow = {c: conscious[c] - less_conscious[c] for c in COLORS_MAP}
    
    prompt = f"""
    Ti si Insights Discovery strokovnjak. Ustvari uradni osebni profil za: {ime}.
    Zavedne energije: {conscious}
    Manj zavedne energije: {less_conscious}
    Tok preferenc (razlika): {pref_flow}
    
    Struktura naj bo identična uradnim profilom:
    1. UVOD: Kratek povzetek tipa.
    2. OSEBNI STIL: Kako oseba deluje.
    3. INTERAKCIJA Z DRUGIMI: Komunikacijski stil.
    4. SPREJEMANJE ODLOČITEV: Kako se odloča.
    5. TOK PREFERENC: Interpretiraj razlike med personama (ali se oseba kje zavira ali sili).
    {f'6. DODATNO VPRAŠANJE: {dodatna_vprasanja}' if dodatna_vprasanja else ''}
    
    Uporabljaj profesionalno slovenščino in Insights terminologijo.
    """
    response = client.chat.completions.create(
        model="gpt-4", # Priporočam gpt-4 za boljšo strukturo
        messages=[{"role": "system", "content": "Ti si profesionalni Insights svetovalec."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- UI APPLIKACIJE ---
st.set_page_config(page_title="Insights Discovery Expert", layout="wide")
st.title("🌈 Insights Discovery - Profesionalni Profiler")

col_i, col_p = st.columns(2)
with col_i: ime = st.text_input("Ime")
with col_p: priimek = st.text_input("Priimek")

# Vprašalnik (skrajšan prikaz za kodo, uporabi svojih 15 vprašanj)
raw_questions = [{"B": "Sistematicen", "R": "Odlocen", "G": "Skrben", "Y": "Navdihujoc"}] * 15 

if 'shuffled_items' not in st.session_state:
    st.session_state.shuffled_items = [[(c, q[k]) for c, k in zip(COLORS_MAP.keys(), ["B","R","G","Y"])] for q in raw_questions]

with st.form("main_form"):
    all_inputs = []
    for i, items in enumerate(st.session_state.shuffled_items):
        st.write(f"Sklop {i+1}")
        cols = st.columns(4)
        for idx, (color, text) in enumerate(items):
            val = cols[idx].select_slider(text, options=OPTIONS, value="2", key=f"q_{i}_{color}")
            all_inputs.append((color, SCORE_MAP[val]))
    
    st.divider()
    st.subheader("💡 Dodatna AI vprašanja")
    q1 = st.checkbox("Kako ta oseba reagira pod stresom?")
    q2 = st.checkbox("Kakšen je najboljši način za vodenje te osebe?")
    q3 = st.checkbox("Katere so glavne slepe pege?")
    
    submitted = st.form_submit_button("USTVARI PROFESIONALNI PROFIL")

if submitted:
    conscious = {c: sum([s for col, s in all_inputs if col == c]) / 15 for c in COLORS_MAP}
    less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}
    
    dodatno = ""
    if q1: dodatno += "Analiziraj odziv na stres. "
    if q2: dodatno += "Svetuj glede vodenja te osebe. "
    if q3: dodatno += "Izpostavi slepe pege. "

    with st.spinner("Genie oblikuje vaš PDF profil..."):
        ai_vsebina = generiraj_kompleksno_analizo(ime, conscious, less_conscious, dodatno)

        # PDF OBLIKOVANJE
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Naslovnica
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(0, 112, 192) # Insights modra
        pdf.cell(0, 100, "INSIGHTS DISCOVERY", align='C', ln=True)
        pdf.set_font("Helvetica", "", 18)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, clean_chars(f"Osebni profil: {ime} {priimek}"), align='C', ln=True)
        pdf.cell(0, 10, f"Datum: {pd.Timestamp.now().strftime('%d.%m.%Y')}", align='C', ln=True)

        # Vsebina po poglavjih (AI razdeli tekst)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Interpretacija profila", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, clean_chars(ai_vsebina))

        # Grafi (v PDF-ju bi potrebovali shranjevanje slike, zaenkrat pustimo tekstovne vrednosti)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, clean_chars("Stevilcne vrednosti in Tok preferenc"), ln=True)
        pdf.set_font("Helvetica", "", 11)
        for c in COLORS_MAP:
            diff = conscious[c] - less_conscious[c]
            pdf.cell(0, 10, clean_chars(f"{c}: Zavedno {round(conscious[c],2)} | Manj zavedno {round(less_conscious[c],2)} | Tok: {round(diff,2)}"), ln=True)

        pdf_output = bytes(pdf.output())
        
        st.success("Profil zgeneriran!")
        st.download_button("📥 Prenesi razširjen PDF profil", pdf_output, f"Insights_Pro_{ime}.pdf")
