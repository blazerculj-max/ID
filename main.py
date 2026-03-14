import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random
import matplotlib.pyplot as plt
from fpdf import FPDF
from openai import OpenAI
import io

# --- POMOŽNA FUNKCIJA ZA ŠUMNIK ---
def clean_chars(text):
    mapping = {"č": "c", "š": "s", "ž": "z", "Č": "C", "Š": "S", "Ž": "Z", "\xa0": " "}
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

# --- MASTER PROMPT ZA POGLOBLJENO ANALIZO ---
MASTER_SYSTEM_PROMPT = """
Ti si vrhunski Insights Discovery svetovalec. Tvoja naloga je ustvariti izjemno podroben, strokoven in analitičen osebni profil.
NAVODILA ZA VSEBINO:
1. Ne uporabljaj oznak kot so ### ali **. Naslove piši z velikimi tiskanimi črkami.
2. Besedilo naj bo bogato, razpotegnjeno in polno konkretnih opisov lastnosti.
3. Za vsako poglavje uporabi vsaj 5-7 vsebinsko močnih alinej.
4. Interpretiraj dinamiko med barvami – npr. kako visoka Fiery Red vpliva na nižjo Earth Green.
5. Uporabljaj terminologijo iz uradnih Insights poročil (npr. Temeljno poglavje, Manj zavedna pozicija).
"""

# --- KONFIGURACIJA ---
COLORS_MAP = {"Cool Blue": "#0070C0", "Fiery Red": "#FF0000", "Earth Green": "#00B050", "Sunshine Yellow": "#FFFF00"}
OPPOSITES = {"Fiery Red": "Earth Green", "Earth Green": "Fiery Red", "Cool Blue": "Sunshine Yellow", "Sunshine Yellow": "Cool Blue"}
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generiraj_premium_vsebino(polno_ime, conscious, less_conscious, coaching_txt):
    pref_flow = {c: round(conscious[c] - less_conscious[c], 2) for c in COLORS_MAP}
    user_content = f"""
    Ustvari obsežen osebni profil za: {polno_ime}. 
    Zavedne energije: {conscious}. 
    Manj zavedne: {less_conscious}. 
    Tok preferenc: {pref_flow}.
    
    Analiziraj osebni slog, interakcijo, sprejemanje odločitev in tok preferenc zelo podrobno.
    Dodaj poglobljeno analizo za module: {coaching_txt}.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": MASTER_SYSTEM_PROMPT},
                  {"role": "user", "content": user_content}],
        temperature=0.7
    )
    return response.choices[0].message.content

# --- FUNKCIJA ZA GENERIRANJE GRAFIKONA ---
def ustvari_graf(data, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = [COLORS_MAP[c] for c in data.keys()]
    bars = ax.bar(data.keys(), data.values(), color=colors, edgecolor='black', linewidth=0.5)
    ax.set_ylim(0, 6)
    ax.set_title(title, fontsize=12, fontweight='bold')
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center', fontweight='bold')
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight')
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

# --- UI APPLIKACIJE ---
st.set_page_config(page_title="Insights Expert Profiler", layout="wide")
st.title("🌈 Insights Discovery - Profesionalni Profiler")

polno_ime = st.text_input("Vnesite ime in priimek stranke", placeholder="Ime Priimek")

# 15 sklopov
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
            st.markdown(f"#### Vprašanje {i+1} od 15")
            for color, text in items:
                col_txt, col_rad = st.columns([1, 2])
                with col_txt: st.markdown(f"{text}")
                with col_rad:
                    val = st.radio(f"R_{i}_{color}", OPTIONS, index=1, horizontal=True, key=f"q_{i}_{color}", label_visibility="collapsed")
                    all_inputs.append((color, SCORE_MAP[val]))

    st.divider()
    st.subheader("🎯 Napredna Coaching analiza")
    c1, c2 = st.columns(2)
    with c1:
        stres = st.checkbox("Poglobljena analiza stresa", value=True)
        vodenje = st.checkbox("Strategije za vodenje in motivacijo")
    with c2:
        pege = st.checkbox("Slepe pege in področja razvoja")
        komunikacija = st.checkbox("Interakcija z nasprotnimi tipi")

    submitted = st.form_submit_button("USTVARI PROFESIONALNI PDF PROFIL")

if submitted:
    if not polno_ime:
        st.error("Vnesite ime!")
    else:
        conscious = {c: sum([s for col, s in all_inputs if col == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}
        
        opt = ""
        if stres: opt += "Stres. "
        if vodenje: opt += "Vodenje. "
        if pege: opt += "Slepe pege. "
        if komunikacija: opt += "Komunikacija. "

        with st.spinner("Genie AI pripravlja obsežno analizo..."):
            ai_text = generiraj_premium_vsebino(polno_ime, conscious, less_conscious, opt)
            graf_zavedno = ustvari_graf(conscious, "Zavedna Persona")
            graf_nezavedno = ustvari_graf(less_conscious, "Manj zavedna Persona")

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            
            # NASLOVNICA
            pdf.add_page()
            pdf.set_fill_color(0, 112, 192)
            pdf.rect(0, 0, 210, 60, 'F')
            pdf.set_font("Helvetica", "B", 26)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 40, clean_chars("INSIGHTS DISCOVERY OSEBNI PROFIL"), align='C', ln=True)
            pdf.ln(30)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "B", 22)
            pdf.cell(0, 10, clean_chars(polno_ime), align='C', ln=True)
            pdf.set_font("Helvetica", "I", 14)
            pdf.cell(0, 10, "Temeljno poglavje", align='C', ln=True)
            
            # STRAN Z GRAFI
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 15, clean_chars("Pregled barvnih energij"), ln=True)
            pdf.image(graf_zavedno, x=15, y=30, w=85)
            pdf.image(graf_nezavedno, x=110, y=30, w=85)
            
            # INTERPRETACIJA (Daljši tekst)
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(0, 112, 192)
            pdf.cell(0, 15, clean_chars("PODROBNA INTERPRETACIJA PROFILA"), ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 11)
            
            # Razdelimo AI tekst na odstavke za lepši izpis
            lines = ai_text.split('\n')
            for line in lines:
                if line.strip():
                    # Če je vrstica velika (naslov poglavja brez oznak)
                    if any(word.isupper() for word in line.split()) and len(line) < 50:
                        pdf.ln(5)
                        pdf.set_font("Helvetica", "B", 12)
                        pdf.cell(0, 10, clean_chars(line.strip()), ln=True)
                        pdf.set_font("Helvetica", "", 11)
                    else:
                        pdf.multi_cell(0, 7, clean_chars(line.strip()))
                        pdf.ln(2)

            pdf_bytes = bytes(pdf.output())
            st.success("Produkt z grafiko je pripravljen!")
            st.download_button(f"📥 Prenesi PDF Profil", pdf_bytes, f"Insights_Pro_{polno_ime}.pdf")
