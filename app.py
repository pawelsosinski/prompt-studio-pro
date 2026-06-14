import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import base64

st.set_page_config(
    page_title="Matryca Decyzyjna",
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
    background-color: #1e293b !important; color: #f1f5f9 !important;
    border: 1px solid #334155 !important; border-radius: 6px !important;
}
div[data-baseweb="select"] > div { background-color: #1e293b !important; border-color: #334155 !important; color: #f1f5f9 !important; }
div[data-baseweb="select"] * { color: #f1f5f9 !important; }
div[data-baseweb="popover"] div { background-color: #1e293b !important; }
.stButton > button { background-color: #334155; color: #f1f5f9; border: 1px solid #475569; border-radius: 6px; font-weight: 500; }
.stButton > button:hover { background-color: #3b82f6; border-color: #3b82f6; color: white; }
.stCheckbox label { color: #94a3b8 !important; }
hr { border-color: #334155 !important; }
.stCaption, [data-testid="stCaptionContainer"] { color: #94a3b8 !important; }
.streamlit-expanderHeader { background-color: #1e293b !important; border-color: #334155 !important; }
.stDataFrame { border: 1px solid #334155; border-radius: 8px; }
.stNumberInput > div > div > input { background-color: #1e293b !important; color: #f1f5f9 !important; border: 1px solid #334155 !important; }
@media print {
    header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stButton { display: none !important; }
    .stApp, .stApp * { background-color: white !important; color: #1a1a1a !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────

QUESTIONS = [
    {"label": "Częstotliwość", "help": "Jak często wykonujesz to zadanie?",
     "options": [("— wybierz —", 0), ("Rzadko / nieregularnie", 1), ("Kilka razy w miesiącu", 2), ("Kilka razy w tygodniu", 3), ("Codziennie lub częściej", 4)]},
    {"label": "Powtarzalność", "help": "Jak powtarzalna jest struktura tego zadania?",
     "options": [("— wybierz —", 0), ("Każde wykonanie jest inne", 1), ("Podobna struktura, różne dane", 2), ("Ten sam schemat, małe warianty", 3), ("Identyczne za każdym razem", 4)]},
    {"label": "Czas trwania", "help": "Ile czasu zajmuje jedno pełne wykonanie?",
     "options": [("— wybierz —", 0), ("Kilka minut", 1), ("15–30 minut", 2), ("30–60 minut", 3), ("Ponad godzina", 4)]},
    {"label": "Osąd w trakcie", "help": "Ile osądu wymaga wykonanie W TRAKCIE kroków (nie na wejściu/wyjściu)?",
     "options": [("— wybierz —", 0), ("Dużo — większość kroków wymaga decyzji", 1), ("Umiarkowanie — kilka decyzji po drodze", 2), ("Mało — głównie przetwarzanie danych", 3), ("Minimalnie / mechaniczne — dane wchodzą, format wychodzi", 4)]},
    {"label": "Liczba narzędzi", "help": "Ile różnych narzędzi / systemów używasz przy tym zadaniu?",
     "options": [("— wybierz —", 0), ("Jedno narzędzie", 1), ("Dwa narzędzia", 2), ("Trzy narzędzia", 3), ("Cztery lub więcej narzędzi", 4)]},
]

LEVELS = [
    None,
    {"num": 1, "name": "Poziom 1: Prompt", "short": "Prompt", "range": "5–8 pkt",
     "color": "#3b82f6", "bg": "#0c2a4a", "icon": "💬",
     "recommendation": "Wystarczy dobrze skonstruowany prompt.",
     "tools": "ChatGPT · Claude · Gemini · Copilot · Perplexity"},
    {"num": 2, "name": "Poziom 2: Asystent AI", "short": "Asystent AI", "range": "9–12 pkt",
     "color": "#8b5cf6", "bg": "#1e1040", "icon": "🤖",
     "recommendation": "Skonfiguruj dedykowanego asystenta z instrukcjami i bazą wiedzy.",
     "tools": "Custom GPT · Claude Project · Gem · Copilot Agent"},
    {"num": 3, "name": "Poziom 3: Automatyzacja", "short": "Automatyzacja", "range": "13–16 pkt",
     "color": "#f59e0b", "bg": "#2a1f00", "icon": "⚙️",
     "recommendation": "Zbuduj automatyzację łączącą narzędzia bez ręcznego wysiłku.",
     "tools": "Make.com · Zapier · n8n · Power Automate"},
    {"num": 4, "name": "Poziom 4: Agent AI", "short": "Agent AI", "range": "17–20 pkt",
     "color": "#ef4444", "bg": "#2a0a0a", "icon": "🦾",
     "recommendation": "Rozważ agenta — najpierw zapytaj: czy nie wystarczy Poziom 3?",
     "tools": "LangChain · Crew AI · Copilot Studio · AutoGen"},
]

CURRENT_LEVELS = [
    ("— wybierz —", -1), ("Brak AI", 0),
    ("Prompt ręczny (ChatGPT od zera, bez szablonu)", 1),
    ("Asystent AI (Custom GPT, Gem, Claude Project...)", 2),
    ("Automatyzacja (Make.com, Zapier, n8n...)", 3),
    ("Agent AI", 4),
]

ROLE_EXAMPLES = {
    "Marketing": [
        {"name": "Tygodniowy raport z kampanii", "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "cl": 1},
        {"name": "Pisanie briefów dla grafików", "q1": 3, "q2": 2, "q3": 2, "q4": 2, "q5": 1, "cl": 1},
        {"name": "Podsumowanie wyników dla klienta", "q1": 2, "q2": 3, "q3": 3, "q4": 2, "q5": 2, "cl": 0},
    ],
    "HR / Kadry": [
        {"name": "Podsumowania rozmów rekrutacyjnych", "q1": 3, "q2": 2, "q3": 2, "q4": 2, "q5": 1, "cl": 1},
        {"name": "Odpowiedzi na powtarzalne pytania od pracowników", "q1": 4, "q2": 4, "q3": 2, "q4": 4, "q5": 1, "cl": 1},
        {"name": "Dokumentacja onboardingu nowego pracownika", "q1": 1, "q2": 3, "q3": 4, "q4": 2, "q5": 3, "cl": 0},
    ],
    "Sprzedaż": [
        {"name": "Follow-up po spotkaniach z klientami", "q1": 3, "q2": 2, "q3": 2, "q4": 2, "q5": 2, "cl": 1},
        {"name": "Tworzenie ofert i propozycji handlowych", "q1": 3, "q2": 2, "q3": 3, "q4": 2, "q5": 2, "cl": 1},
        {"name": "Raport pipeline sprzedażowego", "q1": 3, "q2": 4, "q3": 3, "q4": 3, "q5": 3, "cl": 0},
    ],
    "Operacje": [
        {"name": "Zbieranie statusów projektów od zespołu", "q1": 4, "q2": 3, "q3": 2, "q4": 2, "q5": 3, "cl": 0},
        {"name": "Weryfikacja list kontrolnych i procedur", "q1": 3, "q2": 4, "q3": 2, "q4": 4, "q5": 1, "cl": 1},
        {"name": "Tygodniowy raport dla zarządu", "q1": 3, "q2": 3, "q3": 3, "q4": 2, "q5": 3, "cl": 1},
    ],
    "Właściciel firmy": [
        {"name": "Monitoring oferty konkurencji", "q1": 2, "q2": 2, "q3": 3, "q4": 2, "q5": 2, "cl": 0},
        {"name": "Podsumowania spotkań dla zespołu", "q1": 3, "q2": 3, "q3": 2, "q4": 2, "q5": 1, "cl": 1},
        {"name": "Follow-up po spotkaniach biznesowych", "q1": 3, "q2": 2, "q3": 2, "q4": 2, "q5": 2, "cl": 1},
    ],
    "Support / Obsługa klienta": [
        {"name": "Odpowiedzi na powtarzalne tickety", "q1": 4, "q2": 4, "q3": 2, "q4": 4, "q5": 1, "cl": 1},
        {"name": "Aktualizacja bazy wiedzy i FAQ", "q1": 2, "q2": 2, "q3": 3, "q4": 2, "q5": 2, "cl": 0},
        {"name": "Eskalacje i obsługa reklamacji", "q1": 2, "q2": 1, "q3": 3, "q4": 1, "q5": 2, "cl": 1},
    ],
}

Q_SHORT = ["Częst.", "Powtarz.", "Czas", "Osąd", "Narzędzia"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def level_for_score(s):
    if s < 5: return None
    return LEVELS[1 if s <= 8 else 2 if s <= 12 else 3 if s <= 16 else 4]

def q_value(ti, qi):
    lbl = st.session_state.get(f"t{ti}_q{qi}", "— wybierz —")
    return next((v for l, v in QUESTIONS[qi-1]["options"] if l == lbl), 0)

def cl_value(ti):
    lbl = st.session_state.get(f"cl_{ti}", "— wybierz —")
    return next((v for l, v in CURRENT_LEVELS if l == lbl), -1)

def gap_info(current, rec_num):
    if current < 0 or rec_num is None: return None
    d = rec_num - current
    if d > 0:
        return {"type": "under", "magnitude": d, "color": "#ef4444",
                "label": f"⬆️ Niedoinżynieria ({d} poziom{'y' if d > 1 else ''})",
                "message": f"Tracisz czas — możesz przejść z poziomu {current} do Poziomu {rec_num}."}
    if d < 0:
        m = abs(d)
        return {"type": "over", "magnitude": m, "color": "#f59e0b",
                "label": f"⬇️ Przetechnologizowanie ({m} poziom{'y' if m > 1 else ''})",
                "message": f"Planujesz Poziom {current}, ale wystarczy Poziom {rec_num}. Uprość."}
    return {"type": "match", "magnitude": 0, "color": "#22c55e",
            "label": "✅ Brak luki",
            "message": "Aktualny poziom technologii jest optymalny dla tego zadania."}

def sec_header(n, title):
    c = {1: "#3b82f6", 2: "#8b5cf6", 3: "#f59e0b"}.get(n, "#64748b")
    return (f"<div style='margin:28px 0 14px;padding:14px 18px;"
            f"background:linear-gradient(90deg,{c}18 0%,transparent 70%);"
            f"border-left:4px solid {c};border-radius:0 8px 8px 0'>"
            f"<div style='color:{c};font-size:10px;font-weight:800;letter-spacing:.18em;text-transform:uppercase'>"
            f"SEKCJA {n}</div>"
            f"<div style='color:#e2e8f0;font-size:22px;font-weight:700;margin-top:3px'>{title}</div></div>")

def score_profile(vals):
    if not any(vals): return ""
    bars = ""
    for lbl, val in zip(Q_SHORT, vals):
        pct = val / 4 * 100
        clr = "#3b82f6" if val <= 1 else "#8b5cf6" if val == 2 else "#f59e0b" if val == 3 else "#ef4444"
        bars += (f"<div style='display:flex;align-items:center;gap:6px;margin:3px 0'>"
                 f"<div style='width:62px;font-size:11px;color:#94a3b8'>{lbl}</div>"
                 f"<div style='flex:1;background:#334155;border-radius:3px;height:7px'>"
                 f"<div style='width:{pct}%;background:{clr};height:7px;border-radius:3px'></div></div>"
                 f"<div style='width:14px;font-size:11px;color:#e2e8f0;text-align:right'>{val}</div></div>")
    return (f"<div style='margin-top:10px;padding:10px;background:#0f172a;border-radius:6px'>"
            f"<div style='font-size:10px;color:#64748b;margin-bottom:6px;text-transform:uppercase;letter-spacing:.1em'>Profil zadania</div>"
            f"{bars}</div>")

def score_card_html(score, lv, vals):
    if not lv:
        return ("<div style='background:#1e293b;border:1px dashed #334155;border-radius:10px;"
                "padding:14px;text-align:center;margin-top:12px;color:#64748b;font-size:13px'>"
                "Uzupełnij pytania, aby zobaczyć wynik</div>")
    return (f"<div style='background:{lv['bg']};border:2px solid {lv['color']};border-radius:10px;padding:14px;margin-top:12px'>"
            f"<div style='text-align:center'>"
            f"<div style='font-size:32px;font-weight:800;color:{lv['color']}'>{score}"
            f"<span style='font-size:16px;color:#94a3b8'>/20</span></div>"
            f"<div style='color:{lv['color']};font-weight:700;font-size:15px;margin:6px 0'>{lv['icon']} {lv['name']}</div>"
            f"<div style='font-size:12px;color:#94a3b8'>{lv['range']}</div>"
            f"<div style='font-size:12px;color:#cbd5e1;margin-top:8px;font-style:italic'>{lv['recommendation']}</div>"
            f"<div style='font-size:11px;color:#64748b;margin-top:6px'>{lv['tools']}</div>"
            f"</div>{score_profile(vals)}</div>")

def gap_card_html(gap):
    if not gap:
        return ("<div style='background:#1e293b;border:1px dashed #334155;border-radius:8px;"
                "padding:10px;margin-top:6px;color:#64748b;font-size:12px'>"
                "Wybierz obecny poziom, aby zobaczyć lukę</div>")
    return (f"<div style='background:{gap['color']}18;border:1px solid {gap['color']};"
            f"border-radius:8px;padding:10px 12px;margin-top:6px'>"
            f"<div style='color:{gap['color']};font-weight:700;font-size:14px'>{gap['label']}</div>"
            f"<div style='color:#cbd5e1;font-size:12px;margin-top:6px'>{gap['message']}</div></div>")

def encode_state():
    s = {}
    for i in range(3):
        s[f"n{i}"] = st.session_state.get(f"task_name_{i}", "")
        for q in range(1, 6):
            lbl = st.session_state.get(f"t{i}_q{q}", "— wybierz —")
            s[f"q{i}{q}"] = next((j for j, (l, _) in enumerate(QUESTIONS[q-1]["options"]) if l == lbl), 0)
        cl_lbl = st.session_state.get(f"cl_{i}", "— wybierz —")
        s[f"c{i}"] = next((j for j, (l, _) in enumerate(CURRENT_LEVELS) if l == cl_lbl), 0)
    return base64.urlsafe_b64encode(json.dumps(s, ensure_ascii=False).encode()).decode()

def decode_state(encoded):
    try:
        s = json.loads(base64.urlsafe_b64decode(encoded.encode()).decode())
        for i in range(3):
            if f"n{i}" in s: st.session_state[f"task_name_{i}"] = s[f"n{i}"]
            for q in range(1, 6):
                k = f"q{i}{q}"
                if k in s:
                    idx = int(s[k])
                    opts = QUESTIONS[q-1]["options"]
                    if 0 <= idx < len(opts): st.session_state[f"t{i}_q{q}"] = opts[idx][0]
            ck = f"c{i}"
            if ck in s:
                ci = int(s[ck])
                if 0 <= ci < len(CURRENT_LEVELS): st.session_state[f"cl_{i}"] = CURRENT_LEVELS[ci][0]
    except Exception:
        pass

def generate_html(td, task_names):
    roi_h = st.session_state.get("roi_hours", 1.0)
    roi_t = st.session_state.get("roi_times", 2)
    roi_p = st.session_state.get("roi_pct", 60)
    wh = roi_h * roi_t * (roi_p / 100)
    fw_idx = st.session_state.get("fw_task_select", 0)
    fw_name = task_names[fw_idx] if fw_idx < len(task_names) else "—"

    tasks_html = ""
    q_full = ["Częstotliwość", "Powtarzalność", "Czas trwania", "Osąd w trakcie", "Liczba narzędzi"]
    for i, (d, name) in enumerate(zip(td, task_names)):
        lv = d["level"]
        gp = d["gap"]
        lv_c = lv["color"] if lv else "#64748b"
        lv_n = lv["name"] if lv else "—"
        gp_c = gp["color"] if gp else "#64748b"
        gp_l = gp["label"] if gp else "—"
        cl_l = next((l for l, v in CURRENT_LEVELS if v == d["cl"]), "—") if d["cl"] >= 0 else "—"
        rows = "".join(
            f"<tr><td style='color:#666;padding:3px 8px'>{ql}</td>"
            f"<td style='padding:3px 8px'>{next((l for l, v in QUESTIONS[qi-1]['options'] if v == d['vals'][qi-1]), '—') if d['vals'][qi-1] > 0 else '—'}</td>"
            f"<td style='text-align:center;font-weight:bold;padding:3px 8px'>{d['vals'][qi-1]}/4</td></tr>"
            for qi, ql in enumerate(q_full, 1)
        )
        tasks_html += (f"<div style='border:2px solid {lv_c};border-radius:8px;padding:16px;margin:12px 0;page-break-inside:avoid'>"
                       f"<h3 style='margin:0 0 10px'>Zadanie {i+1}: {name}</h3>"
                       f"<table style='width:100%;border-collapse:collapse;font-size:13px'>{rows}</table>"
                       f"<div style='display:flex;gap:12px;margin-top:12px;flex-wrap:wrap'>"
                       f"<div style='background:{lv_c}22;border:1px solid {lv_c};border-radius:6px;padding:8px 12px;flex:1;min-width:120px'>"
                       f"<div style='font-size:10px;color:#666;text-transform:uppercase'>Wynik</div>"
                       f"<div style='font-size:20px;font-weight:800;color:{lv_c}'>{d['score']}/20</div>"
                       f"<div style='font-size:12px;font-weight:600;color:{lv_c}'>{lv_n}</div></div>"
                       f"<div style='background:#f8f9fa;border:1px solid #dee2e6;border-radius:6px;padding:8px 12px;flex:1;min-width:120px'>"
                       f"<div style='font-size:10px;color:#666;text-transform:uppercase'>Obecny poziom</div>"
                       f"<div style='font-size:12px;font-weight:600;margin-top:4px'>{cl_l}</div></div>"
                       f"<div style='background:{gp_c}22;border:1px solid {gp_c};border-radius:6px;padding:8px 12px;flex:2;min-width:160px'>"
                       f"<div style='font-size:10px;color:#666;text-transform:uppercase'>Luka</div>"
                       f"<div style='font-size:12px;font-weight:600;color:{gp_c};margin-top:4px'>{gp_l}</div></div>"
                       f"</div></div>")

    return f"""<!DOCTYPE html><html lang="pl"><head><meta charset="UTF-8">
<title>Matryca Decyzyjna AI</title>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:Arial,sans-serif; color:#1a1a1a; padding:30px; max-width:900px; margin:0 auto; }}
h1 {{ font-size:26px; border-bottom:4px solid #3b82f6; padding-bottom:10px; margin-bottom:18px; }}
h2 {{ font-size:15px; color:#3b82f6; text-transform:uppercase; letter-spacing:.1em; margin:24px 0 10px; border-left:4px solid #3b82f6; padding-left:10px; }}
.fw {{ border:1px solid #e2e8f0; border-radius:8px; padding:18px; }}
.fl {{ margin:10px 0; }}
.fll {{ font-size:10px; color:#666; text-transform:uppercase; letter-spacing:.08em; }}
.flv {{ font-size:13px; margin-top:3px; padding:6px 8px; background:#f8f9fa; border-radius:4px; min-height:26px; }}
.roi {{ background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:14px; margin-top:12px; display:flex; gap:20px; align-items:center; }}
.rn {{ font-size:22px; font-weight:800; color:#16a34a; }}
.rl {{ font-size:11px; color:#666; }}
@media print {{ h2 {{ page-break-before:always; }} h2:first-of-type {{ page-break-before:avoid; }} }}
</style></head><body>
<h1>Matryca Decyzyjna AI</h1>
<h2>Sekcja 1 + 2 — Audyt i analiza luki</h2>
{tasks_html}
<h2>Sekcja 3 — First Win Card</h2>
<div class="fw">
  <div style="font-size:14px;font-weight:700;margin-bottom:14px">Zadanie: {fw_name}</div>
  <div class="fl"><div class="fll">Opis luki — jak wykonujesz to zadanie dziś</div><div class="flv">{st.session_state.get('fw_gap','') or '—'}</div></div>
  <div class="fl"><div class="fll">Co zbuduję — minimalna działająca wersja</div><div class="flv">{st.session_state.get('fw_build','') or '—'}</div></div>
  <div style="display:flex;gap:14px;margin-top:8px">
    <div class="fl" style="flex:1"><div class="fll">Kiedy zacznę</div><div class="flv">{st.session_state.get('fw_start','') or '—'}</div></div>
    <div class="fl" style="flex:1"><div class="fll">Kto to zauważy</div><div class="flv">{st.session_state.get('fw_who','') or '—'}</div></div>
  </div>
  <div class="roi">
    <div style="text-align:center"><div class="rn">{wh:.1f}h</div><div class="rl">/ tydzień</div></div>
    <div style="text-align:center"><div class="rn">{wh*4.3:.0f}h</div><div class="rl">/ miesiąc</div></div>
    <div style="text-align:center"><div class="rn">{wh*52:.0f}h</div><div class="rl">/ rok</div></div>
    <div style="flex:1;font-size:12px;color:#666;padding-left:8px">
      Szacowana oszczędność przy {roi_h}h × {roi_t}×/tydz. × {roi_p}% automatyzacji
    </div>
  </div>
</div>
</body></html>"""

# ── URL state loading ─────────────────────────────────────────────────────────

if "url_loaded" not in st.session_state:
    st.session_state.url_loaded = True
    if "d" in st.query_params:
        decode_state(st.query_params["d"])

# ── Pre-compute ───────────────────────────────────────────────────────────────

td = []
for i in range(3):
    vals = [q_value(i, q) for q in range(1, 6)]
    sc = sum(vals)
    lv = level_for_score(sc)
    cl = cl_value(i)
    gp = gap_info(cl, lv["num"] if lv else None)
    td.append({"score": sc, "level": lv, "cl": cl, "gap": gp, "vals": vals})

task_names = [st.session_state.get(f"task_name_{i}", "") or f"Zadanie {i+1}" for i in range(3)]
biggest = max(range(3), key=lambda i: td[i]["gap"]["magnitude"] if td[i]["gap"] else 0)

# ── HEADER ────────────────────────────────────────────────────────────────────

col_t, col_b = st.columns([4, 1])
with col_t:
    st.markdown("# Matryca Decyzyjna")
    st.caption("Znajdź właściwy poziom wdrożenia AI dla swoich zadań")
with col_b:
    st.markdown("<div style='padding-top:22px'>", unsafe_allow_html=True)
    if st.button("🖨️ Drukuj", key="btn_print", help="Otwiera okno drukowania"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
    st.download_button("⬇️ Pobierz raport", data=generate_html(td, task_names).encode("utf-8"),
                       file_name="matryca_decyzyjna.html", mime="text/html", key="btn_dl")
    st.markdown("</div>", unsafe_allow_html=True)

col_role, col_load, col_clear, col_share = st.columns([2, 1.1, 0.9, 1.3])
with col_role:
    selected_role = st.selectbox("Rola", options=list(ROLE_EXAMPLES.keys()),
                                 key="role_selector", label_visibility="collapsed")
with col_load:
    if st.button("📚 Wczytaj przykład", key="btn_ex"):
        for i, ex in enumerate(ROLE_EXAMPLES[st.session_state.get("role_selector", "Marketing")]):
            st.session_state[f"task_name_{i}"] = ex["name"]
            for qi in range(1, 6):
                st.session_state[f"t{i}_q{qi}"] = QUESTIONS[qi-1]["options"][ex[f"q{qi}"]][0]
            st.session_state[f"cl_{i}"] = next(l for l, v in CURRENT_LEVELS if v == ex["cl"])
        st.rerun()
with col_clear:
    if st.button("🗑️ Wyczyść", key="btn_clear"):
        for i in range(3):
            st.session_state[f"task_name_{i}"] = ""
            for qi in range(1, 6): st.session_state[f"t{i}_q{qi}"] = "— wybierz —"
            st.session_state[f"cl_{i}"] = "— wybierz —"
        for k in ["fw_gap", "fw_build", "fw_savings", "fw_start", "fw_who"]:
            st.session_state[k] = ""
        st.query_params.clear()
        st.rerun()
with col_share:
    if st.button("🔗 Udostępnij wyniki", key="btn_share"):
        st.query_params["d"] = encode_state()
        st.success("Skopiuj URL z paska przeglądarki!", icon="✅")

st.divider()

# ── SEKCJA 1 ─────────────────────────────────────────────────────────────────

st.markdown(sec_header(1, "Audyt zadań"), unsafe_allow_html=True)
st.caption("Każde pytanie to 1–4 punkty. Łączna punktacja (5–20) wskazuje rekomendowany poziom wdrożenia AI.")

with st.expander("Legenda poziomów Matrycy", expanded=False):
    lcols = st.columns(4)
    for li, lv in enumerate(LEVELS[1:], 1):
        with lcols[li-1]:
            st.markdown(f"""<div style='background:{lv["bg"]};border:1px solid {lv["color"]};border-radius:10px;
                        padding:14px;text-align:center;height:100%'>
                <div style='font-size:26px'>{lv["icon"]}</div>
                <div style='color:{lv["color"]};font-weight:700;margin:6px 0;font-size:14px'>{lv["name"]}</div>
                <div style='font-size:12px;color:#94a3b8'>{lv["range"]}</div>
                <hr style='border-color:#334155;margin:8px 0'>
                <div style='font-size:11px;color:#cbd5e1;line-height:1.6'>{lv["tools"]}</div>
            </div>""", unsafe_allow_html=True)

st.markdown("")
for i, col in enumerate(st.columns(3)):
    with col:
        st.markdown(
            f"<div style='background:#1e293b;border-radius:8px 8px 0 0;padding:8px 12px;"
            f"border-bottom:2px solid #3b82f6;margin-bottom:8px'>"
            f"<span style='color:#94a3b8;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase'>"
            f"ZADANIE {i+1}</span></div>", unsafe_allow_html=True)
        st.text_input("Nazwa zadania", placeholder="Np. Tygodniowy raport z kampanii...",
                      key=f"task_name_{i}", label_visibility="collapsed")
        for qi, q in enumerate(QUESTIONS, 1):
            st.selectbox(q["label"], options=[o[0] for o in q["options"]], key=f"t{i}_q{qi}", help=q["help"])
        st.markdown(score_card_html(td[i]["score"], td[i]["level"], td[i]["vals"]), unsafe_allow_html=True)

# Chart
if any(td[i]["score"] > 0 for i in range(3)):
    q_labels = ["Częstotliwość", "Powtarzalność", "Czas trwania", "Osąd w trakcie", "Liczba narzędzi"]
    clrs = ["#3b82f6", "#8b5cf6", "#f59e0b"]
    fig = go.Figure()
    for i in range(3):
        if td[i]["score"] > 0:
            v = td[i]["vals"]
            fig.add_trace(go.Scatterpolar(
                r=v + [v[0]], theta=q_labels + [q_labels[0]],
                fill="toself", name=task_names[i],
                line=dict(color=clrs[i], width=2), fillcolor=clrs[i] + "33"))
    fig.update_layout(
        polar=dict(bgcolor="#1e293b",
                   radialaxis=dict(visible=True, range=[0, 4], tickvals=[1, 2, 3, 4],
                                   tickfont=dict(color="#94a3b8", size=10), gridcolor="#334155", linecolor="#334155"),
                   angularaxis=dict(tickfont=dict(color="#e2e8f0", size=11), gridcolor="#334155")),
        showlegend=True, legend=dict(font=dict(color="#e2e8f0"), bgcolor="#1e293b", bordercolor="#334155"),
        paper_bgcolor="#0f172a", margin=dict(t=30, b=30, l=60, r=60), height=370)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── SEKCJA 2 ─────────────────────────────────────────────────────────────────

st.markdown(sec_header(2, "Analiza luki"), unsafe_allow_html=True)
st.caption("Wybierz, jak wykonujesz to zadanie DZIŚ. Matryca pokaże, czy jesteś pod- czy przetechnologizowany.")

for i, col in enumerate(st.columns(3)):
    with col:
        lv = td[i]["level"]
        st.markdown(f"**{task_names[i]}**")
        if lv:
            st.markdown(f"<small>Rekomendacja: <span style='color:{lv['color']}'>{lv['icon']} {lv['name']}</span></small>",
                        unsafe_allow_html=True)
        else:
            st.markdown("<small style='color:#64748b'>Uzupełnij Sekcję 1</small>", unsafe_allow_html=True)
        st.selectbox("Obecny poziom technologii", options=[o[0] for o in CURRENT_LEVELS],
                     key=f"cl_{i}", help="Jak dziś wykonujesz to zadanie?")
        st.markdown(gap_card_html(td[i]["gap"]), unsafe_allow_html=True)

st.divider()

# ── SEKCJA 3 ─────────────────────────────────────────────────────────────────

st.markdown(sec_header(3, "First Win Card"), unsafe_allow_html=True)
st.caption("Wybierz zadanie z największą luką i zaplanuj pierwsze wdrożenie na ten tydzień.")

if "fw_task_select" not in st.session_state:
    st.session_state["fw_task_select"] = biggest

fw_l, fw_r = st.columns([1, 2])
with fw_l:
    st.markdown("<div style='font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px'>Zadanie do wdrożenia</div>",
                unsafe_allow_html=True)
    sel = st.selectbox("Zadanie", options=[0, 1, 2], format_func=lambda x: task_names[x],
                       key="fw_task_select", label_visibility="collapsed")
    fw_lv, fw_gap = td[sel]["level"], td[sel]["gap"]
    if fw_lv:
        st.markdown(f"""<div style='background:{fw_lv["bg"]};border:1px solid {fw_lv["color"]};border-radius:8px;padding:12px;margin-top:8px'>
            <div style='color:{fw_lv["color"]};font-weight:700'>{fw_lv["icon"]} {fw_lv["name"]}</div>
            <div style='font-size:12px;color:#94a3b8;margin-top:4px'>Narzędzia:</div>
            <div style='font-size:12px;color:#cbd5e1;margin-top:2px'>{fw_lv["tools"]}</div>
        </div>""", unsafe_allow_html=True)
    if fw_gap and fw_gap["type"] != "match":
        st.markdown(f"""<div style='background:{fw_gap["color"]}18;border:1px solid {fw_gap["color"]};border-radius:8px;padding:10px;margin-top:8px'>
            <div style='color:{fw_gap["color"]};font-weight:700'>{fw_gap["label"]}</div>
            <div style='font-size:12px;color:#cbd5e1;margin-top:4px'>{fw_gap["message"]}</div>
        </div>""", unsafe_allow_html=True)
    if biggest != sel:
        st.markdown(f"<small style='color:#94a3b8'>💡 Największa luka: <b>{task_names[biggest]}</b></small>", unsafe_allow_html=True)

with fw_r:
    st.markdown("<div style='font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px'>Plan wdrożenia</div>",
                unsafe_allow_html=True)
    st.text_area("Opis luki — jak wykonujesz to zadanie DZIŚ?",
                 placeholder='Np. "Ręcznie wpisuję dane do ChatGPT od zera za każdym razem..."',
                 height=80, key="fw_gap")
    st.text_area("Co zbuduję — minimalna działająca wersja (MVP)",
                 placeholder='Np. "Asystent AI w Claude Project z instrukcjami i szablonem raportu"',
                 height=80, key="fw_build")
    c1, c2 = st.columns(2)
    with c1: st.text_input("Szacowana oszczędność / tydzień", placeholder="Np. 2 godziny", key="fw_savings")
    with c2: st.text_input("Kiedy zacznę", placeholder="Np. Poniedziałek 16.06", key="fw_start")
    st.text_input("Kto to zauważy jako pierwszy?",
                  placeholder="Np. Mój manager / klient / zespół marketingu", key="fw_who")

# ROI
st.markdown("")
st.markdown("<div style='background:#1e293b;border:1px solid #334155;border-radius:10px;padding:18px'>",
            unsafe_allow_html=True)
st.markdown("<div style='font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px'>Kalkulator ROI</div>",
            unsafe_allow_html=True)
rc1, rc2, rc3, rc4 = st.columns([1.2, 1.2, 1.5, 2])
with rc1: roi_h = st.number_input("Czas na 1 wykonanie (godz.)", min_value=0.1, max_value=40.0, value=1.0, step=0.5, key="roi_hours")
with rc2: roi_t = st.number_input("Wykonań / tydzień", min_value=1, max_value=50, value=2, step=1, key="roi_times")
with rc3: roi_p = st.slider("Oszczędność po wdrożeniu (%)", min_value=10, max_value=90, value=60, step=10, key="roi_pct")
with rc4:
    wh = roi_h * roi_t * (roi_p / 100)
    st.markdown(f"""<div style='display:flex;gap:20px;padding-top:28px'>
        <div style='text-align:center'><div style='font-size:22px;font-weight:800;color:#22c55e'>{wh:.1f}h</div><div style='font-size:11px;color:#94a3b8'>/ tydzień</div></div>
        <div style='text-align:center'><div style='font-size:22px;font-weight:800;color:#3b82f6'>{wh*4.3:.0f}h</div><div style='font-size:11px;color:#94a3b8'>/ miesiąc</div></div>
        <div style='text-align:center'><div style='font-size:22px;font-weight:800;color:#8b5cf6'>{wh*52:.0f}h</div><div style='font-size:11px;color:#94a3b8'>/ rok</div></div>
    </div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ── WALIDACJA ─────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("<div style='font-size:16px;font-weight:700;margin-bottom:10px'>Lista kontrolna przed wdrożeniem</div>",
            unsafe_allow_html=True)
checks = [
    "Wszystkie 3 zadania pochodzą z mojej realnej pracy (nie tylko z przykładów)",
    "Pytanie o osąd oceniałem/-am w trakcie kroków (nie na wejściu/wyjściu)",
    "Wybrane rozwiązanie wdrożę samodzielnie w kilka godzin bez wsparcia IT",
    "Jeśli wynik 17–20: zapytałem/-am siebie 'Czy naprawdę nie wystarczy Poziom 3?'",
    "Plan nie zakłada agenta, gdy Matryca rekomenduje Poziom 2 lub 3",
]
ck1, ck2 = st.columns(2)
for idx, lbl in enumerate(checks):
    with (ck1 if idx % 2 == 0 else ck2):
        st.checkbox(lbl, key=f"chk_{idx}")

# ── PODSUMOWANIE ──────────────────────────────────────────────────────────────

if all(d["level"] is not None for d in td):
    st.markdown("---")
    st.markdown("<div style='font-size:16px;font-weight:700;margin-bottom:10px'>Podsumowanie Matrycy</div>",
                unsafe_allow_html=True)
    rows = []
    for i, d in enumerate(td):
        lv, gp = d["level"], d["gap"]
        cl_l = next((l for l, v in CURRENT_LEVELS if v == d["cl"]), "—") if d["cl"] >= 0 else "—"
        rows.append({"Zadanie": task_names[i], "Wynik": f"{d['score']}/20",
                     "Rekomendacja": f"{lv['icon']} {lv['name']}",
                     "Obecny poziom": cl_l, "Luka": gp["label"] if gp else "—"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Matryca Decyzyjna · Zapisz wyniki — kliknij ⬇️ Pobierz raport lub 🖨️ Drukuj")
