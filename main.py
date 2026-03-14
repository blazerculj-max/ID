import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
from openai import OpenAI
import io

# --- POMOŽNA FUNKCIJA ZA ŠUMNIK ---
def clean_chars(text):
    mapping = {"č": "c", "š": "s", "ž": "z", "Č": "C", "Š": "S", "Ž": "Z", "\xa0": " "}
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

# --- PSIHOMETRIČNI MASTER PROMPT ---
MASTER_SYSTEM_PROMPT = """
Ti si vrhunski strokovnjak za psihometrične profile (DISC, MBTI, Insights). 
Tvoja naloga je ustvariti poglobljeno analizo osebnosti na podlagi kvantitativnih podatkov.

NAVODILA ZA VSEBINO:
1. STROGO PREPOVEDANO: Ne uporabljaj besednih zvez kot so "barvne energije", "modra", "rdeča", "zelena" ali "rumena energija".
2. UPORABLJAJ strokovne termine: "kognitivna kompleksnost", "analitična natančnost", "ekspresivna komunikacija", "direktivni slog", "kooperativna naravnanost", "metodičen pristop".
3. STIL PISANJA: Uporabljaj t.i. Barnumove stavke – strokovne ugotovitve, ki delujejo globoko osebno in specifično.
4. STRUKTURA: Besedilo naj bo razpotegnjeno, analitično in bogato. Vsako poglavje naj vsebuje 5-7 dolgih alinej.
5. FORMATIRANJE: Naslove poglavij piši z VELIKIMI ČRKAMI. Ne uporabljaj ### ali **.
"""

# --- KONFIGURACIJA ---
COLORS_MAP = {"Cool Blue": "#0070C0", "Fiery Red": "#FF0000", "Earth Green": "#00B050", "Sunshine Yellow": "#FFFF00"}
OPPOSITES = {"Fiery Red": "Earth Green", "Earth Green": "Fiery Red", "Cool Blue": "Sunshine Yellow", "Sunshine Yellow": "Cool Blue"}
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generiraj_psihometricni_profil(ime, conscious, less_conscious, coaching_txt):
    user_content = f"""
    Ustvari osebni profil za: {ime}.
    Rezultati zavednega dela (0-6): {conscious}
    Rezultati manj zavednega dela (0-6): {less_conscious}
    Analiziraj osebni slog, proces odločanja in vpliv na ekipo. 
    Vključi analizo za: {coaching_txt}.
    Bodi izjemno podroben in strokoven.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": MASTER_SYSTEM_PROMPT},
                  {"role": "user", "content": user_content}],
        temperature=0.7
    )
    return response.choices[0].message.content

def ustvari_graf(data, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = [COLORS_MAP[c] for c in data.keys()]
    ax.bar(data.keys(), data.values(), color=colors, edgecolor='black', linewidth=0.5)
    ax.set_ylim(0, 6)
    ax.set_title(title, fontsize=12, fontweight='bold')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return buf

# --- UI APPLIKACIJE ---
st.set_page_config(page_title="Professional Psychometric Profiler", layout="wide")

# CSS za lepšo poravnavo gumbov
st.markdown("""
    <style>
    div.row-widget.stRadio > div { flex-direction: row; justify-content: flex-start; gap: 10px; }
    .instruction-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #0070C0; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Profesionalni Psihometrični Profiler")

# --- NAVODILA NA VRHU ---
st.markdown("""
<div class="instruction-box">
    <h3>📋 Navodila za izpolnjevanje</h3>
    <p>Vprašalnik je zasnovan za analizo vaših vedenjskih preferenc na delovnem mestu. Pri vsakem vprašanju boste videli štiri trditve. Vaša naloga je, da za <b>vsako posamezno trditev</b> določite stopnjo, ki vas najbolje opisuje:</p>
    <ul>
        <li><b>L (Least)</b>: Ta trditev vas sploh ne opisuje oziroma vas opisuje najmanj.</li>
        <li><b>M (Most)</b>: Ta trditev vas popolnoma opisuje oziroma je za vas najbolj značilna.</li>
        <li><b>Številke 1–5</b>: Uporabite jih za vmesne stopnje strinjanja.</li>
    </ul>
    <p><i>Nasvet: Bodite iskreni in se odločite hitro na podlagi prvega občutka. Ni napačnih odgovorov!</i></p>
</div>
""", unsafe_allow_html=True)

polno_ime = st.text_input("Ime in priimek stranke", placeholder="Janez Novak")

# 15 vprašanj (vstavi svoje v celoti)
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

with st.form("main_form"):
    all_inputs = []
    for i, items in enumerate(st.session_state.shuffled):
        with st.container(border=True):
            st.markdown(f"#### Vprašanje {i+1} od 15")
            for color, text in items:
                col_t, col_r = st.columns([1, 2])
                with col_t: st.markdown(f"{text}")
                with col_r:
                    val = st.radio(f"R_{i}_{color}", OPTIONS, index=1, horizontal=True, key=f"q_{i}_{color}", label_visibility="collapsed")
                    all_inputs.append((color, SCORE_MAP[val]))
    
    st.divider()
    st.subheader("🎯 Izbira modulov za končno poročilo")
    c1, c2 = st.columns(2)
    with c1:
        stres = st.checkbox("Analiza vedenja v stresnih situacijah", value=True)
        vodenje = st.checkbox("Slog vodenja in motivacijski dejavniki")
    with c2:
        pege = st.checkbox("Slepe pege in razvojni izzivi")
        tim = st.checkbox("Vloga v timu in komunikacijski slog")
    
    submitted = st.form_submit_button("GENERIRAJ PROFESIONALNO POROČILO")

if submitted:
    if not polno_ime:
        st.error("Prosim, vnesite ime za generiranje poročila.")
    else:
        conscious = {c: sum([s for col, s in all_inputs if col == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}
        
        with st.spinner("Pripravljam psihometrično analizo..."):
            ai_text = generiraj_psihometricni_profil(polno_ime, conscious, less_conscious, "Stres, Vodenje, Slepe pege, Tim")
            graf_z = ustvari_graf(conscious, "Profil zavedne persone")
            
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            
            # NASLOVNICA
            pdf.add_page()
            pdf.set_fill_color(0, 112, 192)
            pdf.rect(0, 0, 210, 60, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 24)
            pdf.cell(0, 40, clean_chars("PSIHOMETRICNO POROCILO OSEBNOSTI"), align='C', ln=True)
            pdf.ln(30)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(0, 10, clean_chars(polno_ime), align='C', ln=True)
            pdf.set_font("Helvetica", "I", 12)
            pdf.cell(0, 10, "Ekspertna interpretacija vedenjskih preferenc", align='C', ln=True)
            
            # GRAFIKON
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 15, clean_chars("Kvantitativni profil preferenc"), ln=True)
            pdf.image(graf_z, x=40, y=40, w=130)
            
            # ANALIZA
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(0, 112, 192)
            pdf.cell(0, 15, clean_chars("EKSPERTNA ANALIZA"), ln=True)
            pdf.set_text_color(0, 0, 0)
            
            for line in ai_text.split('\n'):
                if line.strip():
                    if line.strip().isupper(): # Naslov poglavja
                        pdf.ln(4)
                        pdf.set_font("Helvetica", "B", 12)
                        pdf.cell(0, 10, clean_chars(line.strip()), ln=True)
                        pdf.set_font("Helvetica", "", 11)
                    else:
                        pdf.multi_cell(0, 7, clean_chars(line.strip()))
            
            pdf_out = bytes(pdf.output())
            st.success("Analiza je bila uspešno generirana.")
            st.download_button("📥 Prenesi PDF poročilo", pdf_out, f"Psihometricni_Profil_{polno_ime}.pdf")
