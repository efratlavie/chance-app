import pandas as pd
import streamlit as st

# ====== הגדרות ======
INPUT_XLSX = "chance_last_5000_by_days_v2.xlsx"  # אם אצלך v3 - תשני כאן
DAY_ORDER = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]

st.set_page_config(page_title="Chance | צ'אנס", layout="centered")

# ====== עיצוב: בלי HTML להצגת צירופים בכלל ======
st.markdown(
    """
    <style>
    body, .stApp { direction: rtl; text-align: right; }
    h1,h2,h3,h4,h5,p,div,span,label { direction: rtl; text-align: right; }

    /* כותרות ותגיות וידג'טים מודגש */
    label[data-testid="stWidgetLabel"]{
        font-weight: 950 !important;
        font-size: 1.05rem !important;
    }

    /* מסגרת יפה סביב כל וידג'ט */
    div[data-testid="stSelectbox"],
    div[data-testid="stSlider"]{
        border: 1px solid rgba(49,51,63,0.20);
        background: rgba(255,255,255,0.03);
        padding: 10px 10px 6px 10px;
        border-radius: 14px;
    }

    /* כרטיס אזור בחירה */
    .filters{
        border-radius: 18px;
        padding: 14px;
        border: 2px solid rgba(255,215,0,0.55);
        background:
          radial-gradient(circle at 10% 20%, rgba(255,215,0,0.18), transparent 45%),
          radial-gradient(circle at 90% 80%, rgba(192,192,192,0.14), transparent 45%),
          rgba(255,255,255,0.02);
        box-shadow: 0 16px 34px rgba(0,0,0,0.08);
        margin-bottom: 14px;
    }
    .filters-title{
        font-weight: 950;
        font-size: 1.12rem;
        margin-bottom: 10px;
    }

    /* כרטיס צירוף (ללא HTML) */
    .combo-card{
        border-radius: 18px;
        padding: 14px;
        border: 2px solid rgba(255,215,0,0.55);
        background:
          radial-gradient(circle at 15% 20%, rgba(255,215,0,0.16), transparent 45%),
          radial-gradient(circle at 85% 80%, rgba(192,192,192,0.12), transparent 45%),
          rgba(255,255,255,0.02);
        box-shadow: 0 18px 40px rgba(0,0,0,0.06);
        margin: 10px 0;
    }
    .combo-title{
        font-weight: 950;
        font-size: 1.02rem;
        margin-bottom: 8px;
        opacity: .95;
    }

    /* שורת הצירוף - גדולה ובולטת */
    .combo-line{
        font-size: 1.55rem;
        font-weight: 950;
        letter-spacing: .2px;
        direction: ltr;              /* חשוב: סדר קבוע משמאל לימין */
        text-align: left;
        white-space: nowrap;
        overflow-x: auto;
        padding-bottom: 2px;
    }

    /* צבעים לסמלים */
    .spade   { color:#111827; }
    .heart   { color:#e11d48; }
    .diamond { color:#2563eb; }
    .club    { color:#16a34a; }

    /* כותרת ראשית */
    .hero{
        border-radius: 18px;
        padding: 14px;
        border: 1px solid rgba(49,51,63,0.22);
        background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02));
        margin-bottom: 12px;
    }
    .hero-title{
        font-size: 1.35rem;
        font-weight: 950;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="כל ההגרלות")

    needed = ["הגרלה", "תאריך", "יום", "עלה", "לב", "יהלום", "תלתן"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"חסרות עמודות בקובץ: {missing}")

    # צירוף פנימי: עלה-לב-יהלום-תלתן
    df["צירוף"] = (
        df["עלה"].astype(str).str.strip() + "-" +
        df["לב"].astype(str).str.strip() + "-" +
        df["יהלום"].astype(str).str.strip() + "-" +
        df["תלתן"].astype(str).str.strip()
    )

    return df

def stats_for_day(df: pd.DataFrame, day: str) -> pd.DataFrame:
    day_df = df[df["יום"] == day]
    stats = day_df["צירוף"].value_counts().reset_index()
    stats.columns = ["צירוף", "כמות"]
    return stats

def diverse_pick(stats: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    בוחר צירופים יחסית מגוונים (לא חובה, אבל נעים).
    """
    chosen = []
    used = [set(), set(), set(), set()]
    for _, row in stats.iterrows():
        parts = str(row["צירוף"]).split("-")
        if len(parts) != 4:
            continue
        ok = True
        for i, p in enumerate(parts):
            if p in used[i]:
                ok = False
                break
        if ok:
            chosen.append(row)
            for i, p in enumerate(parts):
                used[i].add(p)
        if len(chosen) == n:
            break
    return pd.DataFrame(chosen) if chosen else stats.head(n)

def render_combo_line(combo: str) -> str:
    """
    מחזיר מחרוזת להצגה – ללא שום תגיות HTML.
    סדר קבוע: ♠ עלה → ♥ לב → ♦ יהלום → ♣ תלתן
    """
    parts = str(combo).split("-")
    if len(parts) != 4:
        return f"{combo}"
    spade, heart, diamond, club = parts
    # שורה LTR כדי לשמור סדר משמאל לימין
    return f"♠ {spade}   ♥ {heart}   ♦ {diamond}   ♣ {club}"

# ====== UI ======
st.markdown(
    """
    <div class="hero">
      <div class="hero-title">💰 Chance – צירופים חמים + כל ההגרלות לפי יום</div>
    </div>
    """,
    unsafe_allow_html=True
)

try:
    df = load_data(INPUT_XLSX)
except FileNotFoundError:
    st.error(f"לא מצאתי את הקובץ: {INPUT_XLSX}\nשימי אותו בתיקיית הפרויקט או תשני את INPUT_XLSX.")
    st.stop()
except Exception as e:
    st.error(f"שגיאה בקריאת הקובץ: {e}")
    st.stop()

tab_hot, tab_draws = st.tabs(["🔥 צירופים חמים", "📅 כל ההגרלות ליום"])

# =========================
# TAB 1: צירופים חמים (רק קטגוריה אחת!)
# =========================
with tab_hot:
    st.markdown('<div class="filters"><div class="filters-title">קטגוריות (בחירה מהירה)</div>', unsafe_allow_html=True)

    day = st.selectbox("בחירת יום", DAY_ORDER, index=0)

    c1, c2, c3 = st.columns(3)
    with c1:
        mode = st.selectbox("סגנון", ["הכי שכיחים", "מגוונים"], index=0)
    with c2:
        min_count = st.slider("מינימום חזרות", 1, 30, 2, 1)
    with c3:
        show_n = st.slider("כמה צירופים להציג", 5, 50, 15, 1)

    st.markdown("</div>", unsafe_allow_html=True)

    stats = stats_for_day(df, day)
    if stats.empty:
        st.info("אין נתונים ליום הזה.")
        st.stop()

    stats2 = stats[stats["כמות"] >= min_count].copy()
    if stats2.empty:
        st.info("אין צירופים שעברו את הסינון.")
        st.stop()

    chosen = diverse_pick(stats2, show_n) if mode == "מגוונים" else stats2.head(show_n)

    st.subheader(f"🔥 צירופים חמים ליום {day}")

    for i, row in enumerate(chosen.itertuples(index=False), start=1):
        combo_text = render_combo_line(row.צירוף)

        # כרטיס מעוצב (העיצוב פה הוא CSS, אבל התוכן עצמו בלי שום תגיות HTML!)
        st.markdown(
            f"""
            <div class="combo-card">
              <div class="combo-title">🏆 צירוף #{i}</div>
              <div class="combo-line">
                <span class="spade">♠</span> {str(row.צירוף).split("-")[0]}
                &nbsp;&nbsp;
                <span class="heart">♥</span> {str(row.צירוף).split("-")[1]}
                &nbsp;&nbsp;
                <span class="diamond">♦</span> {str(row.צירוף).split("-")[2]}
                &nbsp;&nbsp;
                <span class="club">♣</span> {str(row.צירוף).split("-")[3]}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # הורדת CSV (ללא רעש על המסך)
    csv_bytes = chosen.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button("⬇️ הורדת CSV", data=csv_bytes, file_name=f"chance_{day}_hot.csv", mime="text/csv")

# =========================
# TAB 2: כל ההגרלות ליום
# =========================
with tab_draws:
    st.markdown('<div class="filters"><div class="filters-title">צפייה בכל ההגרלות לפי יום</div>', unsafe_allow_html=True)

    day2 = st.selectbox("בחירת יום", DAY_ORDER, index=0, key="day2")
    c1, c2 = st.columns(2)
    with c1:
        show_rows = st.slider("כמה שורות להציג", 20, 500, 80, 20)
    with c2:
        search_draw = st.text_input("חיפוש לפי מספר הגרלה (אופציונלי)")
    st.markdown("</div>", unsafe_allow_html=True)

    day_df = df[df["יום"] == day2].copy().sort_values("הגרלה", ascending=False)

    if search_draw.strip():
        try:
            num = int(search_draw.strip())
            day_df = day_df[day_df["הגרלה"] == num]
        except ValueError:
            st.warning("בחיפוש מספר הגרלה יש להקליד מספר בלבד.")

    view_cols = ["הגרלה", "תאריך", "יום", "עלה", "לב", "יהלום", "תלתן", "צירוף"]
    st.dataframe(day_df[view_cols].head(show_rows), use_container_width=True, height=560)

    csv_all = day_df[view_cols].to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button("⬇️ הורדת כל ההגרלות של היום (CSV)", data=csv_all, file_name=f"chance_draws_{day2}.csv", mime="text/csv")

# =========================
# 💬 צ'אט חי – Chance VIP
# =========================

from supabase import create_client
import os

st.markdown("---")
st.header("💬 צ'אט חי – חוכמת ההמונים")

# חיבור ל-Supabase דרך Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# טופס שליחת הודעה
with st.form("chat_form", clear_on_submit=True):
    username = st.text_input("שם / כינוי")
    message = st.text_input("כתוב הודעה")
    submitted = st.form_submit_button("שלח")

    if submitted and message:
        supabase.table("chat_messages").insert({
            "username": username if username else "אורח",
            "message": message,
            "channel": "general"
        }).execute()
        st.success("ההודעה נשלחה!")

# הצגת ההודעות
st.markdown("### 🗨️ הודעות אחרונות")
messages = (
    supabase
    .table("chat_messages")
    .select("*")
    .order("created_at", desc=True)
    .limit(50)
    .execute()
)

for row in reversed(messages.data):
    st.markdown(f"**{row['username']}**: {row['message']}")

