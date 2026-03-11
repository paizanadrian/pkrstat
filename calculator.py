import streamlit as st
import streamlit.components.v1 as components
import random
from itertools import combinations

def do_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# ─── Constants ────────────────────────────────────────────────────────────────
SUITS     = ['♠', '♥', '♦', '♣']
SUIT_COLOR = {'♠': '#111', '♥': '#c00', '♦': '#c00', '♣': '#111'}
VALUES    = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VAL_RANK  = {v: i for i, v in enumerate(VALUES)}
HAND_NAMES = [
    'High Card', 'One Pair', 'Two Pair', 'Three of a Kind',
    'Straight', 'Flush', 'Full House', 'Four of a Kind', 'Straight Flush'
]

# ─── Hand evaluation ──────────────────────────────────────────────────────────
def rank5(hand):
    vals  = sorted([VAL_RANK[v] for v, _ in hand], reverse=True)
    suits = [s for _, s in hand]
    flush  = len(set(suits)) == 1
    is_str = max(vals) - min(vals) == 4 and len(set(vals)) == 5
    if sorted(vals) == [0, 1, 2, 3, 12]:
        is_str, vals = True, [3, 2, 1, 0, -1]
    cnts = sorted([vals.count(v) for v in set(vals)], reverse=True)
    if is_str and flush: return (8, vals)
    if cnts[0] == 4:     return (7, vals)
    if cnts[:2] == [3,2]:return (6, vals)
    if flush:            return (5, vals)
    if is_str:           return (4, vals)
    if cnts[0] == 3:     return (3, vals)
    if cnts[:2] == [2,2]:return (2, vals)
    if cnts[0] == 2:     return (1, vals)
    return (0, vals)

def best_rank(hole, board):
    return max(rank5(list(c)) for c in combinations(hole + board, 5))

def win_probability(my_hand, known_board, n_players, n_sim=300):
    all_cards = [(v, s) for s in SUITS for v in VALUES]
    used      = set(map(tuple, my_hand + known_board))
    remaining = [c for c in all_cards if tuple(c) not in used]
    opponents = n_players - 1
    if len(remaining) < (5 - len(known_board)) + opponents * 2:
        return None
    wins = ties = 0
    for _ in range(n_sim):
        deck      = remaining.copy()
        random.shuffle(deck)
        sim_board = known_board + deck[:5 - len(known_board)]
        deck      = deck[5 - len(known_board):]
        opp_hands = [[deck[i*2], deck[i*2+1]] for i in range(opponents)]
        my_r      = best_rank(my_hand, sim_board)
        best_o    = max(best_rank(h, sim_board) for h in opp_hands)
        if my_r > best_o:    wins += 1
        elif my_r == best_o: ties += 1
    return round((wins + ties * 0.5) / n_sim * 100, 1)

# ─── HTML helpers ─────────────────────────────────────────────────────────────
def card_html(v, s, w=62, h=88):
    c  = SUIT_COLOR[s]
    fs = max(10, int(w * 0.22))
    ss = max(16, int(w * 0.36))
    return (
        f'<div style="width:{w}px;height:{h}px;background:white;border-radius:8px;'
        f'border:1.5px solid #ccc;display:inline-block;margin:3px;'
        f'box-shadow:1px 2px 5px rgba(0,0,0,0.3);color:{c};font-weight:bold;'
        f'text-align:center;position:relative;vertical-align:top;">'
        f'<div style="position:absolute;top:3px;left:5px;font-size:{fs}px;line-height:1;">{v}</div>'
        f'<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);'
        f'font-size:{ss}px;line-height:1;">{s}</div>'
        f'<div style="position:absolute;bottom:3px;right:5px;font-size:{fs}px;'
        f'line-height:1;transform:rotate(180deg);">{v}</div>'
        f'</div>'
    )

def empty_slot_html(w=62, h=88):
    return (
        f'<div style="width:{w}px;height:{h}px;'
        f'background:rgba(255,255,255,0.06);'
        f'border-radius:8px;border:2px dashed rgba(255,255,255,0.22);'
        f'display:inline-block;margin:3px;vertical-align:top;'
        f'color:rgba(255,255,255,0.2);font-size:26px;'
        f'line-height:{h}px;text-align:center;">?</div>'
    )

def wp_badge_html(wp):
    if wp is None:
        return ""
    bc = "#2e7d32" if wp >= 55 else ("#e65100" if wp >= 30 else "#b71c1c")
    return (
        f'<div style="text-align:center;margin-top:10px;">'
        f'<span style="background:{bc};color:white;border-radius:20px;'
        f'padding:5px 18px;font-size:15px;font-weight:bold;'
        f'box-shadow:0 2px 6px rgba(0,0,0,0.4);">'
        f'{wp:.1f}% șanse de câștig</span></div>'
    )

def section_label(txt):
    return (
        f'<div style="color:rgba(255,255,255,0.5);font-size:11px;'
        f'letter-spacing:2px;text-transform:uppercase;'
        f'margin-bottom:4px;margin-top:2px;">{txt}</div>'
    )

# ─── App ──────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Poker Calculator", layout="wide", page_icon="♠")
st.markdown("""
<style>
.stApp { background: #145a20 !important; }
section[data-testid="stSidebar"] { background: #0d3d16 !important; }

/* Butoane card picker (mici, albe) */
div[data-testid="column"] .stButton > button {
    background: #ffffff !important;
    color: #111111;
    border: 1px solid rgba(0,0,0,0.2) !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    font-weight: bold !important;
    padding: 4px 2px !important;
    line-height: 1.4 !important;
    min-height: 0px !important;
    width: 100% !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: #fffde7 !important;
    border-color: #ffc107 !important;
    transform: scale(1.05);
}

/* Butoane actiune (reset, undo, sidebar) */
section[data-testid="stSidebar"] .stButton > button,
div[data-testid="stVerticalBlock"] > div:last-child .stButton > button {
    background: #1b5e20 !important;
    color: white !important;
    border: 2px solid #4caf50 !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: bold !important;
    padding: 8px !important;
}
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ♠ Calculator")
    n_players = st.slider("Jucători la masă", 2, 9, 6, key="calc_n")
    st.markdown("---")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.6);font-size:13px;line-height:1.8;'>"
        "1. Alege 2 cărți ale tale<br>"
        "2. Adaugă Flop (3 cărți)<br>"
        "3. Adaugă Turn (1 carte)<br>"
        "4. Adaugă River (1 carte)<br>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    if st.button("🔄 Reset complet", use_container_width=True, key="calc_reset"):
        st.session_state.sel = []
        st.session_state.wp_cache = {}
        do_rerun()

# ─── Init ─────────────────────────────────────────────────────────────────────
if 'sel' not in st.session_state:
    st.session_state.sel = []
if 'wp_cache' not in st.session_state:
    st.session_state.wp_cache = {}

sel  = st.session_state.sel          # list of (val, suit) tuples, max 7
n    = len(sel)
used = set(map(tuple, sel))

hole  = sel[:2]
flop  = sel[2:5]
turn  = sel[5:6]
river = sel[6:7]
board = sel[2:]

# ─── Win probability (cached) ─────────────────────────────────────────────────
wp = None
if len(hole) == 2:
    cache_key = (tuple(map(tuple, hole)), tuple(map(tuple, board)), n_players)
    if cache_key in st.session_state.wp_cache:
        wp = st.session_state.wp_cache[cache_key]
    else:
        wp = win_probability(hole, board, n_players)
        st.session_state.wp_cache[cache_key] = wp

# Best hand name (when >= 5 cards)
best_hand_name = ""
if len(hole) == 2 and len(board) >= 3:
    all7 = hole + board
    if len(all7) >= 5:
        r = max(rank5(list(c)) for c in combinations(all7, 5))
        best_hand_name = HAND_NAMES[r[0]]

# ─── Phase indicator ──────────────────────────────────────────────────────────
PHASES = [
    ("Alege prima carte a ta", "#81c784"),
    ("Alege a doua carte a ta", "#81c784"),
    ("Alege Flop — 1/3", "#64b5f6"),
    ("Alege Flop — 2/3", "#64b5f6"),
    ("Alege Flop — 3/3", "#64b5f6"),
    ("Alege Turn", "#ffb74d"),
    ("Alege River", "#ef9a9a"),
    ("Toate cărțile selectate ✓", "#a5d6a7"),
]
phase_txt, phase_color = PHASES[min(n, 7)]
st.markdown(
    f'<div style="text-align:center;margin-bottom:10px;">'
    f'<span style="background:rgba(0,0,0,0.3);color:{phase_color};'
    f'border-radius:20px;padding:5px 20px;font-size:15px;font-weight:bold;">'
    f'{phase_txt}</span></div>',
    unsafe_allow_html=True
)

# ─── Hand display ─────────────────────────────────────────────────────────────
col_hole, col_comm = st.columns([1, 2.8])

with col_hole:
    cards_h = ''.join(card_html(*c, 70, 98) for c in hole)
    cards_h += ''.join(empty_slot_html(70, 98) for _ in range(2 - len(hole)))
    cards_h += wp_badge_html(wp)
    if best_hand_name:
        cards_h += (
            f'<div style="text-align:center;margin-top:6px;">'
            f'<span style="color:#ffcc80;font-size:12px;">{best_hand_name}</span></div>'
        )
    st.markdown(
        f'<div style="background:rgba(0,90,0,0.55);border:2px solid #4caf50;'
        f'border-radius:12px;padding:12px;text-align:center;">'
        f'{section_label("Cărțile mele")}{cards_h}</div>',
        unsafe_allow_html=True
    )

with col_comm:
    # Flop
    flop_h  = ''.join(card_html(*c) for c in flop)
    flop_h += ''.join(empty_slot_html() for _ in range(3 - len(flop)))
    # Turn
    turn_h  = card_html(*turn[0]) if turn else empty_slot_html()
    # River
    river_h = card_html(*river[0]) if river else empty_slot_html()

    comm_html = (
        f'<div style="display:flex;align-items:flex-start;gap:18px;flex-wrap:wrap;">'
        f'<div>{section_label("Flop")}<div>{flop_h}</div></div>'
        f'<div>{section_label("Turn")}<div>{turn_h}</div></div>'
        f'<div>{section_label("River")}<div>{river_h}</div></div>'
        f'</div>'
    )
    st.markdown(
        f'<div style="background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.1);'
        f'border-radius:12px;padding:12px 16px;">{comm_html}</div>',
        unsafe_allow_html=True
    )

# ─── Card picker grid ─────────────────────────────────────────────────────────
if n < 7:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="color:rgba(255,255,255,0.6);font-size:13px;'
        'font-weight:bold;margin-bottom:8px;">Alege o carte:</div>',
        unsafe_allow_html=True
    )

    for suit in SUITS:
        is_red = suit in ('♥', '♦')
        cols = st.columns(13)
        for i, val in enumerate(VALUES):
            card = (val, suit)
            with cols[i]:
                if tuple(card) in used:
                    # Greyed out — not clickable
                    st.markdown(
                        f'<div style="text-align:center;padding:5px 0;'
                        f'color:rgba(255,255,255,0.15);font-size:12px;'
                        f'font-weight:bold;line-height:1.3;">'
                        f'{val}<br>{suit}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    txt_color = "#c00" if is_red else "#111"
                    # Inline style override via markdown trick for red suits
                    label = f"{val}\n{suit}"
                    btn_clicked = st.button(label, key=f"c_{val}_{suit}", use_container_width=True)
                    if btn_clicked:
                        st.session_state.sel.append(list(card))
                        do_rerun()

# ─── Undo button ──────────────────────────────────────────────────────────────
if sel:
    st.markdown("<br>", unsafe_allow_html=True)
    _, undo_col, _ = st.columns([3, 1.2, 3])
    with undo_col:
        if st.button("↩ Anulează ultima carte", use_container_width=True, key="calc_undo"):
            st.session_state.sel.pop()
            do_rerun()

# ─── Colorează simbolurile roșii pe butoanele de cărți ───────────────────────
components.html("""
<script>
(function () {
    function colorRedSuits() {
        var doc = window.parent.document;
        doc.querySelectorAll('button p').forEach(function (p) {
            var t = p.textContent || '';
            var btn = p.closest('button');
            var isCard = t.indexOf('\u2665') !== -1 || t.indexOf('\u2666') !== -1 ||
                         t.indexOf('\u2660') !== -1 || t.indexOf('\u2663') !== -1;
            if (!isCard) return;
            if (btn) {
                btn.style.setProperty('background', '#ffffff', 'important');
                btn.style.setProperty('background-color', '#ffffff', 'important');
                btn.style.setProperty('border', '1px solid rgba(0,0,0,0.2)', 'important');
            }
            if (t.indexOf('\u2665') !== -1 || t.indexOf('\u2666') !== -1) {
                p.style.setProperty('color', '#cc0000', 'important');
                if (btn) btn.style.setProperty('color', '#cc0000', 'important');
            } else {
                p.style.setProperty('color', '#111111', 'important');
                if (btn) btn.style.setProperty('color', '#111111', 'important');
            }
        });
    }
    colorRedSuits();
    setTimeout(colorRedSuits, 150);
    setTimeout(colorRedSuits, 500);
    new MutationObserver(colorRedSuits).observe(
        window.parent.document.body,
        { childList: true, subtree: true }
    );
})();
</script>
""", height=0)
