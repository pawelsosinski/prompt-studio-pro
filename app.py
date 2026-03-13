import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai

# 1. Konfiguracja strony (Midnight Slate)
st.set_page_config(page_title="Prompt Studio PRO V4.0", layout="centered")

# 2. Skrupulatna stylizacja wizualna
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #e2e8f0; }
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>textarea {
        background-color: #1e293b !important; color: #f1f5f9 !important; border: 1px solid #334155 !important;
    }
    .stButton>button { width: 100%; background-color: #475569; color: white; border: none; }
    .stButton>button:hover { background-color: #94a3b8; color: #0f172a; }
    </style>
    """, unsafe_allow_html=True)

# 3. Połączenie z Google Sheets (Twoja Baza)
# Pamiętaj: Link do arkusza wkleisz później w ustawieniach Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Pobieramy dane z zakładki "Baza"
    df = conn.read(worksheet="Baza")
    
    st.title("🚀 Prompt Studio V4.0")
    st.caption("Ewolucja w Pythonie | Baza: Google Sheets")

    # Sekcja wejściowa
    subject = st.text_input("Główny Obiekt", placeholder="Np. SaMASZ KDX 350 technical sketch...")

    # Dynamiczne listy z Twojego arkusza
    cols = st.columns(2)
    selections = {}
    
    # Tworzymy selektory na podstawie kolumn z arkusza
    for i, col_name in enumerate(df.columns):
        with cols[i % 2]:
            options = df[col_name].dropna().unique().tolist()
            selections[col_name] = st.selectbox(f"Wybierz {col_name}", [""] + options)

    # Budowanie bazowego promptu
    base_elements = [subject] + [val for val in selections.values() if val]
    final_base = ", ".join(filter(None, base_elements))

    st.divider()
    
    # Podgląd i AI
    user_prompt = st.text_area("Prompt (edytowalny)", value=final_base, height=120)

    if st.button("✨ Ulepsz przez Gemini 2.5"):
        # Tu w przyszłości dodamy klucz API w Secrets
        st.info("AI czeka na konfigurację klucza w Streamlit Cloud.")

except Exception as e:
    st.error(f"Czekam na połączenie z arkuszem... Błąd: {e}")
