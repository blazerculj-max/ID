import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
from openai import OpenAI
import io
import unicodedata

# --- 1. POMOŽNE FUNKCIJE ---
def clean_chars(text):
    if text is None: return ""
    text = unicodedata.normalize('NFKD', text)
    mapping = {"č": "c", "š": "s", "ž": "z", "Č": "C", "Š": "S", "Ž": "Z", "\xa0": " ", "–": "-", "—": "-"}
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text.encode("ascii", "ignore").decode("ascii")

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

# --- 2. KONFIGURACIJA ---
MASTER_SYSTEM_PROMPT = """
Ti si vrhunski prodajni coach in psihometrik. Tvoja naloga je interpretirati podatke v prepričljiv, 
razumljiv in prodajen jezik (uporabljaj Barnumove stavke).
NAVODILA:
1. NE UPORABLJAJ barvnih metafor (modra, rdeča energija...).
2. UPORABLJAJ strokovne termine: "direktivni slog", "kognitivna kompleksnost", "ekspresivna komunikacija".
3. STRUKTURA: Naslovi naj bodo z VELIKIMI ČRKAMI. Uporabi bogate alineje.
4. POGLAVJA: PRODAJNI STIL, MOČNE TOČKE (PLUSI), IZZIVI ZA RAZVOJ, DELOVANJE POD PRITISKOM.
"""

COLORS_MAP = {"Cool Blue": "#0070C0", "Fiery Red": "#FF0000", "Earth Green": "#00B050", "Sunshine Yellow": "#FFFF00"}
OPPOSITES = {"Fiery Red": "Earth Green", "Earth Green": "Fiery Red", "Cool Blue": "Sunshine Yellow", "Sunshine Yellow": "Cool Blue"}
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 3. UI IN DIZAJN ---
st.set_page_config(page_title="Pro Sales Profiler", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #fdfdfd, #f0f2f6); }
    .instruction-box { background: white; padding: 25px; border-radius: 15px; border-left: 6px solid #28a745; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    div[data-testid="stVerticalBlock"] > div:has(div.stRadio) { background: white; padding: 20px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 30px; height: 3.5em; background-color: #28a745; color: white; font-weight: bold; border: none; }
    div.row-widget.stRadio > div { flex-direction: row; justify-content: flex-start; gap: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Prodajni Psihometrični Profiler")

st.markdown("""
<div class="instruction-box">
    <h3>📝 Pravila ocenjevanja (Obvezno)</h3>
    <p>Pri vsakem vprašanju morate med štirimi trditvami razdeliti ocene po naslednjem ključu:</p>
    <ul>
        <li><b>1x M (Most)</b>: Trditev, ki vas najbolje opisuje.</li>
        <li><b>1x L (Least)</b>: Trditev, ki vas najmanj opisuje.</li>
        <li><b>2x Številka (1-5)</b>: Preostali dve trditvi ocenite s številko, vendar <b>ne smeta biti enaki</b>.</li>
    </ul>
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

with st.form("insights_form"):
    form_results = []
    for i, items in enumerate(st.session_state.shuffled):
        st.markdown(f"#### Vprašanje {i+1} od 15")
        current_q_results = {}
        for color, text in items:
            col_t, col_r = st.columns([1, 2])
            with col_t: st.markdown(f"**{text}**")
            with col_r:
                val = st.radio(f"Radio_{i}_{color}", OPTIONS, index=1, horizontal=True, key=f"q_{i}_{color}", label_visibility="collapsed")
                current_q_results[color] = val
        form_results.append(current_q_results)
    
    st.divider()
    st.subheader("🎯 Dodatki za poročilo")
    c1, c2 = st.columns(2)
    with c1:
        stres = st.checkbox("Analiza v stresu", value=True)
        vodenje = st.checkbox("Nasveti za vodjo")
    with c2:
        pege = st.checkbox("Slepe pege")
        tim = st.checkbox("Dinamika tima")
    
    submitted = st.form_submit_button("USTVARI PRODAJNI PDF")

# --- 4. VALIDACIJA IN GENERIRANJE ---
if submitted:
    valid_all = True
    for idx, res in enumerate(form_results):
        vals = list(res.values())
        if vals.count("L") != 1 or vals.count("M") != 1:
            st.error(f"Napaka pri vprašanju {idx+1}: Imeti morate natanko en 'L' in en 'M'.")
            valid_all = False
            break
        num_vals = [v for v in vals if v not in ["L", "M"]]
        if len(set(num_vals)) != len(num_vals):
            st.error(f"Napaka pri vprašanju {idx+1}: Številčni vrednosti ne smeta biti enaki.")
            valid_all = False
            break

    if valid_all and polno_ime:
        all_flat_scores = []
        for res in form_results:
            for color, val in res.items():
                all_flat_scores.append((color, SCORE_MAP[val]))
        
        conscious = {c: sum([s for col, s in all_flat_scores if col == c]) / 15 for c in COLORS_MAP}
        less_conscious = {c: 6.0 - conscious[OPPOSITES[c]] for c in COLORS_MAP}
        
        with st.spinner("Genie pripravlja premium poročilo..."):
            user_content = f"Profil za: {polno_ime}. Rezultati: {conscious}. Manj zavedno: {less_conscious}."
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": MASTER_SYSTEM_PROMPT}, {"role": "user", "content": user_content}]
            )
            ai_text = response.choices[0].message.content
            graf_z = ustvari_graf(conscious, "Prodajni potencial")
            
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.add_page()
            pdf.set_fill_color(40, 167, 69); pdf.rect(0, 0, 210, 50, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 24)
            pdf.cell(0, 30, clean_chars("PRODAJNI PROFIL OSEBNOSTI"), align='C', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(30); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", "B", 20)
            pdf.cell(0, 10, clean_chars(polno_ime), align='C', new_x="LMARGIN", new_y="NEXT")
            
            pdf.add_page()
            pdf.image(graf_z, x=40, w=130)
            
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14); pdf.set_text_color(40, 167, 69)
            pdf.cell(0, 15, clean_chars("EKSPERTNA INTERPRETACIJA"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", "", 11)
            
            for line in ai_text.split('\n'):
                line = line.strip()
                if line:
                    if line.isupper():
                        pdf.ln(4); pdf.set_font("Helvetica", "B", 12)
                        pdf.multi_cell(0, 8, clean_chars(line), new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", "", 11)
                    else:
                        pdf.multi_cell(0, 7, clean_chars(line), new_x="LMARGIN", new_y="NEXT")
            
            st.download_button("📥 Prenesi Prodajni PDF", bytes(pdf.output()), f"Profil_{polno_ime}.pdf")
