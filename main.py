import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
from openai import OpenAI
import io
import unicodedata

# --- 1. VRHUNSKI PSIHOMETRIČNI PROMPT ---
# Modelirano po strukturi naloženega dokumenta (Blaž Erčulj)
MASTER_SYSTEM_PROMPT = """
Ti si ekspertni Insights Discovery generator. Tvoja naloga je ustvariti osebni profil, 
ki je po tonu in strukturi identičen uradnim poročilom.

PRAVILA PISANJA:
- Obvezno piši v TRETJI OSEBI (npr. "Blaž se odziva...", "Njegov slog je...").
- Uporabljaj formalen, analitičen in opolnomočujoč jezik.
- Vsako poglavje naj bo bogato z vsebino (vsaj 3-4 dolgi odstavki).

STRUKTURA, KI JO MORAŠ UPOŠTEVATI:
1. UVOD: Splošni osebnostni tipi in pristop.
2. PREGLED IN OSEBNI STIL: Kako oseba deluje, njene prioritete in notranje vrednote.
3. INTERAKCIJA Z DRUGIMI: Komunikacijski slog in vpliv na ekipo.
4. SPREJEMANJE ODLOČITEV: Logika proti intuiciji in hitrost odločanja.
5. KLJUČNE PREDNOSTI IN MOŽNE SLABOSTI: Jasne točke moči in področja za razvoj.

NE uporabljaj barvnih metafor v besedilu (npr. ne piši 'rdeča energija').
"""

def clean_chars(text):
    if text is None: return ""
    text = unicodedata.normalize('NFKD', text)
    mapping = {"č": "c", "š": "s", "ž": "z", "Č": "C", "Š": "S", "Ž": "Z", "–": "-", "—": "-", "ć": "c", "Ć": "C"}
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text.encode("ascii", "ignore").decode("ascii")

# --- 2. KONFIGURACIJA ---
COLORS_MAP = {"Cool Blue": "#0070C0", "Fiery Red": "#FF0000", "Earth Green": "#00B050", "Sunshine Yellow": "#FFFF00"}
OPPOSITES = {"Fiery Red": "Earth Green", "Earth Green": "Fiery Red", "Cool Blue": "Sunshine Yellow", "Sunshine Yellow": "Cool Blue"}
OPTIONS = ["L", "1", "2", "3", "4", "5", "M"]
SCORE_MAP = {"L": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "M": 6}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 3. MODEREN UX DIZAJN (CSS) ---
st.set_page_config(page_title="Insights Discovery Expert", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .q-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); margin-bottom: 20px; border: 1px solid #eee; }
    .stRadio > div { flex-direction: row; gap: 15px; }
    .stButton > button { width: 100%; border-radius: 30px; height: 3.5em; background-color: #0070C0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌈 Insights Discovery Osebni Profiler")
polno_ime = st.text_input("Ime in priimek stranke", placeholder="Npr. Blaž Erčulj")

# Seznam 15 vprašanj (lahko jih dopolniš z dejanskimi pari trditev)
questions_data = [
    {"B": "Natančen in premišljen", "R": "Odločen in neposreden", "G": "Potrpežljiv in razumevajoč", "Y": "Navdušen in komunikativen"},
    # ... tukaj ponoviš za vseh 15 vprašanj
] * 15 

with st.form("insights_form"):
    all_responses = []
    for i, q in enumerate(questions_data):
        st.markdown(f"<div class='q-card'><h4>Sklop {i+1} od 15</h4>", unsafe_allow_html=True)
        q_res = {}
        for color, label in [("Cool Blue", q["B"]), ("Fiery Red", q["R"]), ("Earth Green", q["G"]), ("Sunshine Yellow", q["Y"])]:
            c1, c2 = st.columns([1, 2])
            with c1: st.write(f"**{label}**")
            with c2: val = st.radio(f"R_{i}_{color}", OPTIONS, index=1, horizontal=True, key=f"k_{i}_{color}", label_visibility="collapsed")
            q_res[color] = val
        all_responses.append(q_res)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.info("Pravilo: Vsak sklop mora vsebovati en 'L', en 'M' in dve različni številki.")
    submitted = st.form_submit_button("USTVARI CELOVITO POROČILO")

# --- 4. LOGIKA VALIDACIJE IN GENERIRANJA ---
if submitted:
    if not polno_ime:
        st.error("Prosim, vnesite ime stranke.")
    else:
        valid = True
        for idx, res in enumerate(all_responses):
            vals = list(res.values())
            if vals.count("L") != 1 or vals.count("M") != 1 or len(set(vals)) != 4:
                st.error(f"Napaka v sklopu {idx+1}. Preverite pravila ocenjevanja.")
                valid = False
                break
        
        if valid:
            with st.spinner("Analiziram podatke in pišem profil v slogu Insights Discovery..."):
                scores = {c: sum([SCORE_MAP[r[c]] for r in all_responses]) / 15 for c in COLORS_MAP}
                
                # AI Generiranje po poglavjih
                prompt = f"Ustvari Insights profil za {polno_ime}. Rezultati kolesa: {scores}. Drži se strukture: PREGLED, OSEBNI STIL, INTERAKCIJA, ODLOČANJE, PREDNOSTI, SLABOSTI."
                response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": MASTER_SYSTEM_PROMPT}, {"role": "user", "content": prompt}])
                ai_text = response.choices[0].message.content

                # PDF Generiranje
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=20)
                
                # Naslovnica
                pdf.add_page()
                pdf.set_fill_color(0, 112, 192); pdf.rect(0, 0, 210, 297, 'F')
                pdf.set_font("Helvetica", "B", 35); pdf.set_text_color(255, 255, 255)
                pdf.set_y(100); pdf.cell(0, 20, "INSIGHTS DISCOVERY", align='C', ln=True)
                pdf.set_font("Helvetica", "", 20); pdf.cell(0, 15, "OSEBNI PROFIL", align='C', ln=True)
                pdf.ln(50); pdf.cell(0, 10, clean_chars(polno_ime), align='C', ln=True)

                # Razdelitev po straneh
                sections = ai_text.split('\n\n')
                for section in sections:
                    if len(section.strip()) > 10:
                        pdf.add_page()
                        pdf.set_fill_color(0, 112, 192); pdf.rect(0, 0, 210, 20, 'F')
                        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(255, 255, 255)
                        pdf.set_xy(10, 5); pdf.cell(0, 10, clean_chars(f"Insights Discovery: {polno_ime}"))
                        
                        pdf.set_text_color(0, 0, 0); pdf.set_xy(10, 30)
                        lines = section.split('\n')
                        pdf.set_font("Helvetica", "B", 16); pdf.cell(0, 12, clean_chars(lines[0]), ln=True)
                        pdf.set_font("Helvetica", "", 11); pdf.ln(5)
                        pdf.multi_cell(0, 7, clean_chars("\n".join(lines[1:])))

                st.success("Profil je pripravljen!")
                st.download_button("📥 Prenesi končno poročilo (PDF)", bytes(pdf.output()), f"Insights_Profil_{polno_ime}.pdf")
