import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
from openai import OpenAI
import io
import unicodedata

# --- IZBOLJŠANA FUNKCIJA ZA ČIŠČENJE BESEDILA ---
def clean_chars(text):
    if text is None:
        return ""
    # Najprej normaliziramo Unicode (pretvori npr. posebne narekovaje v navadne)
    text = unicodedata.normalize('NFKD', text)
    # Ročna zamenjava šumnikov in pogostih problematičnih znakov
    mapping = {
        "č": "c", "š": "s", "ž": "z", 
        "Č": "C", "Š": "S", "Ž": "Z",
        "\xa0": " ", "–": "-", "—": "-", 
        "“": "\"", "”": "\"", "‘": "'", "’": "'"
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    # Odstranimo vse znake, ki niso ASCII (varnostna mreža)
    return text.encode("ascii", "ignore").decode("ascii")

# --- PRODAJNI PSIHOMETRIČNI MASTER PROMPT ---
MASTER_SYSTEM_PROMPT = """
Ti si vrhunski prodajni coach in strokovnjak za psihometrijo. Tvoja naloga je "prevesti" podatke v privlačen, razumljiv in prodajen jezik.

NAVODILA ZA VSEBINO:
1. JEZIK: Uporabljaj pogovorni, razumljiv ton. Izogibaj se tehničnemu žargonu in barvam (ne piši "modra energija").
2. BARNUMOVI STAVKI: Uporabljaj prepričljive formulacije, ki stranko navdušijo nad njenim potencialom.
3. PRODAJNI STIL: Analiziraj, kako oseba prepričuje in gradi zaupanje.
4. PLUSI IN IZZIVI: Navedi konkretne prednosti in jasna področja za izboljšavo.
5. FORMAT: Naslove poglavij piši z VELIKIMI ČRKAMI. Ne uporabljaj znakov ### ali **.
"""

# --- KONFIGURACIJA ---
COLORS_MAP = {"Cool Blue": "#0070C0", "Fiery Red": "#FF0000", "Earth Green": "#00B050", "Sunshine Yellow": "#FFFF00"}
OPPOSITES = {"Fiery Red": "Earth Green", "Earth Green": "Fiery Red", "Cool Blue": "Sunshine Yellow", "Sunshine Yellow": "Cool Blue"}
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generiraj_prodajni_profil(ime, conscious, less_conscious, coaching_txt):
    user_content = f"""
    Sestavi prodajni psihološki profil za: {ime}.
    Rezultati (0-6): {conscious}. Manj zavedno: {less_conscious}.
    Vključi poglavja: PRODAJNI STIL, PLUSI, RAZVOJNA PODROČJA in {coaching_txt}.
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
    buf.seek(0)
    return buf

# --- UI APPLIKACIJE ---
st.set_page_config(page_title="Sales Psychometric Expert", layout="wide")

st.markdown("""
    <style>
    div.row-widget.stRadio > div { flex-direction: row; justify-content: flex-start; gap: 10px; }
    .instruction-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Prodajni Psihometrični Profiler")

st.markdown("""
<div class="instruction-box">
    <h3>📝 Navodila za vnos</h3>
    <p>Ocenite trditve (L do M) glede na to, kako močno veljajo za vas v delovnem okolju.</p>
</div>
""", unsafe_allow_html=True)

polno_ime = st.text_input("Ime in priimek stranke", placeholder="Janez Novak")

# 15 Vprašanj
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
    c1, c2 = st.columns(2)
    with c1:
        stres = st.checkbox("Odziv v stresnih situacijah", value=True)
        vodenje = st.checkbox("Nasveti za vodjo")
    with c2:
        pege = st.checkbox("Slepe pege")
        tim = st.checkbox("Dinamika v timu")
    
    submitted = st.form_submit_button("USTVARI PRODAJNI PDF")

if submitted:
    if not polno_ime:
        st.error("Prosim, vnesite ime stranke.")
    else:
        conscious = {c: sum([s for col, s in all_inputs if col == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}
        
        with st.spinner("Genie pripravlja poročilo..."):
            ai_text = generiraj_prodajni_profil(polno_ime, conscious, less_conscious, "Stres, Vodenje, Slepe pege, Tim")
            graf_z = ustvari_graf(conscious, "Profil preferenc")
            
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            
            # NASLOVNICA
            pdf.add_page()
            pdf.set_fill_color(40, 167, 69)
            pdf.rect(0, 0, 210, 60, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 24)
            pdf.cell(0, 40, clean_chars("PRODAJNI PROFIL OSEBNOSTI"), align='C', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(30)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(0, 10, clean_chars(polno_ime), align='C', new_x="LMARGIN", new_y="NEXT")
            
            # GRAF
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 15, clean_chars("Vizualni povzetek"), new_x="LMARGIN", new_y="NEXT")
            pdf.image(graf_z, x=40, w=130)
            
            # ANALIZA
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(40, 167, 69)
            pdf.cell(0, 15, clean_chars("EKSPERTNA INTERPRETACIJA"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)
            
            for line in ai_text.split('\n'):
                line = line.strip()
                if line:
                    if line.isupper():
                        pdf.ln(4)
                        pdf.set_font("Helvetica", "B", 12)
                        pdf.multi_cell(0, 8, clean_chars(line), new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", "", 11)
                    else:
                        pdf.multi_cell(0, 7, clean_chars(line), new_x="LMARGIN", new_y="NEXT")
                        pdf.ln(1)
            
            pdf_out = bytes(pdf.output())
            st.success("Uspešno!")
            st.download_button("📥 Prenesi PDF", pdf_out, f"Profil_{polno_ime}.pdf")
