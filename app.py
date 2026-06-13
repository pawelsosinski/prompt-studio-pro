import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI LAB: Matryca Decyzyjna",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp { background-color: #0f172a; color: #e2e8f0; }
.stApp header { background-color: #0f172a !important; }
.stTextInput > div > div > input,
.stTextArea > div > textarea {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}
div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    border-color: #334155 !important;
    color: #f1f5f9 !important;
}
div[data-baseweb="select"] * { color: #f1f5f9 !important; }
div[data-baseweb="popover"] div { background-color: #1e293b !important; }
.stButton > button {
    background-color: #334155;
    color: #f1f5f9;
    border: 1px solid #475569;
    border-radius: 6px;
    font-weight: 500;
}
.stButton > button:hover { background-color: #3b82f6; border-color: #3b82f6; color: white; }
.stCheckbox label { color: #94a3b8 !important; }
hr { border-color: #334155 !important; }
.stCaption, [data-testid="stCaptionContainer"] { color: #94a3b8 !important; }
.streamlit-expanderHeader { background-color: #1e293b !important; border-color: #334155 !important; }
.stDataFrame { border: 1px solid #334155; border-radius: 8px; }
@media print {
    header, footer,
    [data-testid="stSidebar"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    .stButton { display: none !important; }
    .stApp, .stApp * { background-color: white !important; color: #1a1a1a !important; }
    .stTextInput > div > div > input,
    .stTextArea > div > textarea {
        background: #f8f9fa !important;
        border-color: #ccc !important;
        color: #1a1a1a !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────

QUESTIONS = [
    {
        "label": "📅 Częstotliwość",
        "help": "Jak często wykonujesz to zadanie?",
        "options": [
            ("— wybierz —", 0),
            ("Rzadko / nieregularnie", 1),
            ("Kilka razy w miesiącu", 2),
            ("Kilka razy w tygodniu", 3),
            ("Codziennie lub częściej", 4),
        ],
    },
    {
        "label": "🔄 Powtarzalność",
        "help": "Jak powtarzalna jest struktura tego zadania?",
        "options": [
            ("— wybierz —", 0),
            ("Każde wykonanie jest inne", 1),
            ("Podobna struktura, różne dane", 2),
            ("Ten sam schemat, małe warianty", 3),
            ("Identyczne za każdym razem", 4),
        ],
    },
    {
        "label": "⏱️ Czas trwania",
        "help": "Ile czasu zajmuje jedno pełne wykonanie?",
        "options": [
            ("— wybierz —", 0),
            ("Kilka minut", 1),
            ("15–30 minut", 2),
            ("30–60 minut", 3),
            ("Ponad godzina", 4),
        ],
    },
    {
        "label": "🧠 Osąd w trakcie",
        "help": "Ile eksperckiego osądu wymaga wykonanie W TRAKCIE kroków? (nie na wejściu/wyjściu — w trakcie)",
        "options": [
            ("— wybierz —", 0),
            ("Dużo — większość kroków wymaga decyzji", 1),
            ("Umiarkowanie — kilka decyzji po drodze", 2),
            ("Mało — głównie przetwarzanie danych", 3),
            ("Minimalnie / mechaniczne — dane wchodzą, format wychodzi", 4),
        ],
    },
    {
        "label": "🛠️ Liczba narzędzi",
        "help": "Ile różnych narzędzi / systemów używasz przy tym zadaniu?",
        "options": [
            ("— wybierz —", 0),
            ("Jedno narzędzie", 1),
            ("Dwa narzędzia", 2),
            ("Trzy narzędzia", 3),
            ("Cztery lub więcej narzędzi", 4),
        ],
    },
]

LEVELS = [
    None,
    {
        "num": 1, "name": "Poziom 1: Prompt", "short": "Prompt", "range": "5–8 pkt",
        "color": "#3b82f6", "bg": "#0c2a4a", "icon": "💬",
        "recommendation": "Wystarczy dobrze skonstruowany prompt.",
        "tools": "ChatGPT · Claude · Gemini · Copilot · Perplexity",
    },
    {
        "num": 2, "name": "Poziom 2: Asystent AI", "short": "Asystent AI", "range": "9–12 pkt",
        "color": "#8b5cf6", "bg": "#1e1040", "icon": "🤖",
        "recommendation": "Skonfiguruj dedykowanego asystenta z instrukcjami i bazą wiedzy.",
        "tools": "Custom GPT · Claude Project · Gem · Copilot Agent",
    },
    {
        "num": 3, "name": "Poziom 3: Automatyzacja", "short": "Automatyzacja", "range": "13–16 pkt",
        "color": "#f59e0b", "bg": "#2a1f00", "icon": "⚙️",
        "recommendation": "Zbuduj automatyzację łączącą narzędzia bez ręcznego wysiłku.",
        "tools": "Make.com · Zapier · n8n · Power Automate",
    },
    {
        "num": 4, "name": "Poziom 4: Agent AI", "short": "Agent AI", "range": "17–20 pkt",
        "color": "#ef4444", "bg": "#2a0a0a", "icon": "🦾",
        "recommendation": "Rozważ agenta — najpierw zapytaj: czy nie wystarczy Poziom 3?",
        "tools": "LangChain · Crew AI · Copilot Studio · AutoGen",
    },
]

CURRENT_LEVELS = [
    ("— wybierz —", -1),
    ("Brak AI", 0),
    ("Prompt ręczny (ChatGPT od zera, bez szablonu)", 1),
    ("Asystent AI (Custom GPT, Gem, Claude Project...)", 2),
    ("Automatyzacja (Make.com, Zapier, n8n...)", 3),
    ("Agent AI", 4),
]

EXAMPLES = [
    {"name": "Tygodniowy raport z kampanii",
     "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "cl": 1},
    {"name": "Odpowiedzi na powtarzalne pytania od pracowników",
     "q1": 4, "q2": 4, "q3": 2, "q4": 4, "q5": 1, "cl": 1},
    {"name": "Follow-up po spotkaniach z klientami",
     "q1": 3, "q2": 2, "q3": 2, "q4": 2, "q5": 2, "cl": 1},
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def level_for_score(score):
    if score < 5:
        return None
    return LEVELS[1 if score <= 8 else 2 if score <= 12 else 3 if score <= 16 else 4]

def q_value(task_idx, q_idx):
    label = st.session_state.get(f"t{task_idx}_q{q_idx}", "— wybierz —")
    return next((v for lbl, v in QUESTIONS[q_idx - 1]["options"] if lbl == label), 0)

def task_score(task_idx):
    return sum(q_value(task_idx, q) for q in range(1, 6))

def cl_value(task_idx):
    label = st.session_state.get(f"cl_{task_idx}", "— wybierz —")
    return next((v for lbl, v in CURRENT_LEVELS if lbl == label), -1)

def gap_info(current, recommended_num):
    if current < 0 or recommended_num is None:
        return None
    diff = recommended_num - current
    if diff > 0:
        m = diff
        return {"type": "under", "magnitude": m, "color": "#ef4444",
                "label": f"⬆️ Niedoinżynieria ({m} poziom{'y' if m > 1 else ''})",
                "message": f"Tracisz czas — możesz przejść z poziomu {current} do Poziomu {recommended_num}."}
    if diff < 0:
        m = abs(diff)
        return {"type": "over", "magnitude": m, "color": "#f59e0b",
                "label": f"⬇️ Przetechnologizowanie ({m} poziom{'y' if m > 1 else ''})",
                "message": f"Planujesz Poziom {current}, ale wystarczy Poziom {recommended_num}. Uprość."}
    return {"type": "match", "magnitude": 0, "color": "#22c55e",
            "label": "✅ Brak luki",
            "message": "Aktualny poziom technologii jest optymalny dla tego zadania."}

def score_card(score, lv):
    if not lv:
        return """<div style='background:#1e293b;border:1px dashed #334155;border-radius:10px;
                    padding:14px;text-align:center;margin-top:12px;color:#64748b;font-size:13px'>
                    Uzupełnij pytania, aby zobaczyć wynik</div>"""
    return f"""<div style='background:{lv["bg"]};border:2px solid {lv["color"]};border-radius:10px;
                padding:14px;text-align:center;margin-top:12px'>
        <div style='font-size:32px;font-weight:800;color:{lv["color"]}'>{score}
            <span style='font-size:16px;color:#94a3b8'>/20</span></div>
        <div style='color:{lv["color"]};font-weight:700;font-size:15px;margin:6px 0'>
            {lv["icon"]} {lv["name"]}</div>
        <div style='font-size:12px;color:#94a3b8'>{lv["range"]}</div>
        <div style='font-size:12px;color:#cbd5e1;margin-top:8px;font-style:italic'>{lv["recommendation"]}</div>
        <div style='font-size:11px;color:#64748b;margin-top:6px'>{lv["tools"]}</div>
    </div>"""

def gap_card(gap):
    if not gap:
        return """<div style='background:#1e293b;border:1px dashed #334155;border-radius:8px;
                    padding:10px;margin-top:6px;color:#64748b;font-size:12px'>
                    Wybierz obecny poziom, aby zobaczyć lukę</div>"""
    return f"""<div style='background:{gap["color"]}18;border:1px solid {gap["color"]};
                border-radius:8px;padding:10px 12px;margin-top:6px'>
        <div style='color:{gap["color"]};font-weight:700;font-size:14px'>{gap["label"]}</div>
        <div style='color:#cbd5e1;font-size:12px;margin-top:6px'>{gap["message"]}</div>
    </div>"""

# ── Pre-compute ───────────────────────────────────────────────────────────────

td = []
for i in range(3):
    sc = task_score(i)
    lv = level_for_score(sc)
    cl = cl_value(i)
    gp = gap_info(cl, lv["num"] if lv else None)
    td.append({"score": sc, "level": lv, "cl": cl, "gap": gp})

biggest = max(range(3), key=lambda i: td[i]["gap"]["magnitude"] if td[i]["gap"] else 0)

# ── HEADER ────────────────────────────────────────────────────────────────────

col_t, col_b = st.columns([4, 1])
with col_t:
    st.markdown("# 🧠 AI LAB: Matryca Decyzyjna")
    st.caption("Umiejętności Jutra AI 3.0 · Znajdź właściwy poziom wdrożenia AI dla swoich zadań")
with col_b:
    st.markdown("<div style='padding-top:22px'>", unsafe_allow_html=True)
    if st.button("🖨️ Drukuj do PDF", key="btn_print", help="Otwiera okno drukowania — wybierz 'Zapisz jako PDF'"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

col_ex, col_cl, col_desc = st.columns([1.3, 1, 3])
with col_ex:
    if st.button("📚 Wczytaj przykłady z lekcji", key="btn_ex"):
        for i, ex in enumerate(EXAMPLES):
            st.session_state[f"task_name_{i}"] = ex["name"]
            for qi in range(1, 6):
                st.session_state[f"t{i}_q{qi}"] = QUESTIONS[qi - 1]["options"][ex[f"q{qi}"]][0]
            st.session_state[f"cl_{i}"] = next(lbl for lbl, v in CURRENT_LEVELS if v == ex["cl"])
        st.rerun()
with col_cl:
    if st.button("🗑️ Wyczyść dane", key="btn_clear"):
        for i in range(3):
            st.session_state[f"task_name_{i}"] = ""
            for qi in range(1, 6):
                st.session_state[f"t{i}_q{qi}"] = "— wybierz —"
            st.session_state[f"cl_{i}"] = "— wybierz —"
        for k in ["fw_gap", "fw_build", "fw_savings", "fw_start", "fw_who"]:
            st.session_state[k] = ""
        st.rerun()
with col_desc:
    st.caption("Wpisz 3 regularne zadania z Twojej pracy → odpowiedz na 5 pytań → odkryj lukę technologiczną.")

st.divider()

# ── SEKCJA 1: AUDYT ──────────────────────────────────────────────────────────

st.markdown("## 📊 Sekcja 1: Audyt zadań")
st.caption("Każde pytanie to 1–4 punkty. Łączna punktacja (5–20) wskazuje rekomendowany poziom wdrożenia AI.")

with st.expander("ℹ️ Legenda poziomów Matrycy", expanded=False):
    lcols = st.columns(4)
    for li, lv in enumerate(LEVELS[1:], 1):
        with lcols[li - 1]:
            st.markdown(f"""
            <div style='background:{lv["bg"]};border:1px solid {lv["color"]};border-radius:10px;
                        padding:14px;text-align:center;height:100%'>
                <div style='font-size:26px'>{lv["icon"]}</div>
                <div style='color:{lv["color"]};font-weight:700;margin:6px 0;font-size:14px'>{lv["name"]}</div>
                <div style='font-size:12px;color:#94a3b8'>{lv["range"]}</div>
                <hr style='border-color:#334155;margin:8px 0'>
                <div style='font-size:11px;color:#cbd5e1;line-height:1.6'>{lv["tools"]}</div>
            </div>""", unsafe_allow_html=True)

st.markdown("")

task_cols = st.columns(3)
for i, col in enumerate(task_cols):
    with col:
        st.markdown(f"### Zadanie {i + 1}")
        st.text_input("Nazwa zadania", placeholder="Np. Tygodniowy raport z kampanii...",
                      key=f"task_name_{i}")
        for qi, q in enumerate(QUESTIONS, 1):
            st.selectbox(q["label"], options=[o[0] for o in q["options"]],
                         key=f"t{i}_q{qi}", help=q["help"])
        st.markdown(score_card(td[i]["score"], td[i]["level"]), unsafe_allow_html=True)

st.divider()

# ── SEKCJA 2: LUKA ───────────────────────────────────────────────────────────

st.markdown("## 🔍 Sekcja 2: Analiza luki")
st.caption("Wybierz, jak wykonujesz to zadanie DZIŚ. Matryca pokaże, czy jesteś pod- czy przetechnologizowany.")

gap_cols = st.columns(3)
for i, col in enumerate(gap_cols):
    with col:
        lv = td[i]["level"]
        name = st.session_state.get(f"task_name_{i}", "") or f"Zadanie {i + 1}"
        st.markdown(f"**{name}**")
        if lv:
            st.markdown(f"<small>Rekomendacja: <span style='color:{lv['color']}'>"
                        f"{lv['icon']} {lv['name']}</span></small>", unsafe_allow_html=True)
        else:
            st.markdown("<small style='color:#64748b'>Uzupełnij Sekcję 1</small>", unsafe_allow_html=True)
        st.selectbox("Obecny poziom technologii", options=[o[0] for o in CURRENT_LEVELS],
                     key=f"cl_{i}", help="Jak dziś wykonujesz to zadanie?")
        if td[i]["gap"]:
            st.markdown(gap_card(td[i]["gap"]), unsafe_allow_html=True)
        else:
            st.markdown(gap_card(None), unsafe_allow_html=True)

st.divider()

# ── SEKCJA 3: FIRST WIN CARD ──────────────────────────────────────────────────

st.markdown("## 🏆 Sekcja 3: First Win Card")
st.caption("Wybierz zadanie z największą luką i zaplanuj pierwsze wdrożenie na ten tydzień.")

task_names = [st.session_state.get(f"task_name_{i}", "") or f"Zadanie {i + 1}" for i in range(3)]

fw_left, fw_right = st.columns([1, 2])

with fw_left:
    st.markdown("#### Zadanie do wdrożenia")

    # Only set default from biggest if key not yet in session state
    if "fw_task_select" not in st.session_state:
        st.session_state["fw_task_select"] = biggest

    sel = st.selectbox("Wybierz zadanie", options=[0, 1, 2],
                       format_func=lambda x: task_names[x], key="fw_task_select",
                       help="Aplikacja wstępnie wybrała zadanie z największą luką")

    fw_lv = td[sel]["level"]
    fw_gap = td[sel]["gap"]

    if fw_lv:
        st.markdown(f"""
        <div style='background:{fw_lv["bg"]};border:1px solid {fw_lv["color"]};
                    border-radius:8px;padding:12px;margin-top:8px'>
            <div style='color:{fw_lv["color"]};font-weight:700'>{fw_lv["icon"]} {fw_lv["name"]}</div>
            <div style='font-size:12px;color:#94a3b8;margin-top:4px'>Narzędzia:</div>
            <div style='font-size:12px;color:#cbd5e1;margin-top:2px'>{fw_lv["tools"]}</div>
        </div>""", unsafe_allow_html=True)

    if fw_gap and fw_gap["type"] != "match":
        st.markdown(f"""
        <div style='background:{fw_gap["color"]}18;border:1px solid {fw_gap["color"]};
                    border-radius:8px;padding:10px;margin-top:8px'>
            <div style='color:{fw_gap["color"]};font-weight:700'>{fw_gap["label"]}</div>
            <div style='font-size:12px;color:#cbd5e1;margin-top:4px'>{fw_gap["message"]}</div>
        </div>""", unsafe_allow_html=True)

    if biggest != sel:
        biggest_name = task_names[biggest]
        st.markdown(f"<small style='color:#94a3b8'>💡 Największa luka: <b>{biggest_name}</b></small>",
                    unsafe_allow_html=True)

with fw_right:
    st.markdown("#### Plan wdrożenia")
    st.text_area("📌 Opis luki — jak wykonujesz to zadanie DZIŚ?",
                 placeholder='Np. "Ręcznie wpisuję dane do ChatGPT od zera, za każdym razem od początku..."',
                 height=80, key="fw_gap")
    st.text_area("🔨 Co zbuduję — minimalna działająca wersja (MVP)",
                 placeholder='Np. "Asystent AI w Claude Project z instrukcjami i szablonem raportu"',
                 height=80, key="fw_build")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("⏱️ Szacowana oszczędność / tydzień",
                      placeholder="Np. 2 godziny", key="fw_savings")
    with c2:
        st.text_input("📅 Kiedy zacznę", placeholder="Np. Poniedziałek 16.06", key="fw_start")
    st.text_input("👤 Kto to zauważy jako pierwszy?",
                  placeholder="Np. Mój manager / klient / cały zespół marketingu", key="fw_who")

# ── WALIDACJA ─────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### ✔️ Lista kontrolna przed wdrożeniem")

checks = [
    "Wszystkie 3 zadania pochodzą z mojej realnej pracy (nie tylko z przykładów z lekcji)",
    "Pytanie o osąd oceniałem/-am w trakcie kroków (nie na wejściu/wyjściu)",
    "Wybrane rozwiązanie wdrożę samodzielnie w kilka godzin bez wsparcia IT",
    "Jeśli wynik 17–20: zapytałem/-am siebie 'Czy naprawdę nie wystarczy Poziom 3?'",
    "Plan nie zakłada agenta, gdy Matryca rekomenduje Poziom 2 lub 3",
]
ck1, ck2 = st.columns(2)
for idx, label in enumerate(checks):
    with (ck1 if idx % 2 == 0 else ck2):
        st.checkbox(label, key=f"chk_{idx}")

# ── PODSUMOWANIE ──────────────────────────────────────────────────────────────

all_scored = all(d["level"] is not None for d in td)
if all_scored:
    st.markdown("---")
    st.markdown("### 📋 Podsumowanie Matrycy")
    rows = []
    for i, d in enumerate(td):
        name = st.session_state.get(f"task_name_{i}", "") or f"Zadanie {i + 1}"
        lv = d["level"]
        gp = d["gap"]
        cl_label = next((lbl for lbl, v in CURRENT_LEVELS if v == d["cl"]), "—") if d["cl"] >= 0 else "—"
        rows.append({
            "Zadanie": name,
            "Wynik": f"{d['score']}/20",
            "Rekomendacja": f"{lv['icon']} {lv['name']}",
            "Obecny poziom": cl_label,
            "Luka": gp["label"] if gp else "—",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("AI LAB: Matryca Decyzyjna · Umiejętności Jutra AI 3.0 · Zapisz wyniki — kliknij 🖨️ Drukuj do PDF")
