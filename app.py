import streamlit as st
import pandas as pd
import hashlib
import folium
from streamlit_folium import st_folium
from datetime import datetime
import random
import json
import base64
import io
import math
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# ─────────────────────────────────────────────
# SAHIFA SOZLAMALARI
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CarbonVision | O'zbekiston Karbon Kredit Platformasi",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');
    .main { background-color: #f0f7f0; font-family: 'Inter', sans-serif; }
    .stMetric { background: white; border-radius: 14px; padding: 1.1rem 1.2rem;
                border: 1px solid #d4ecd4; box-shadow: 0 2px 12px rgba(0,80,0,0.06); }
    .stMetric label { color: #4a7c4a !important; font-size: 0.75rem !important;
                      text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; }
    .stMetric [data-testid="stMetricValue"] { color: #0f2d0f !important;
                                               font-size: 1.75rem !important; font-weight: 700 !important; }
    .ai-result-box {
        background: linear-gradient(135deg, #0a1f0a 0%, #0d2e1a 100%);
        border: 1px solid #2d6a2d; border-radius: 16px;
        padding: 1.25rem 1.5rem; color: #c8f0ca;
        font-family: 'Space Mono', monospace; font-size: 0.82rem; margin: 0.75rem 0;
    }
    .ai-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: linear-gradient(135deg, #0f2d0f, #1a4a1a);
        color: #52c45a; border: 1px solid #38a83d; border-radius: 20px;
        padding: 0.3rem 0.8rem; font-size: 0.75rem;
        font-family: 'Space Mono', monospace; font-weight: 700;
    }
    .fraud-alert {
        background: linear-gradient(135deg, #2d0a0a, #4a0f0f);
        border: 1.5px solid #e53e3e; border-radius: 12px;
        padding: 1rem 1.25rem; color: #fca5a5;
        font-family: 'Space Mono', monospace; font-size: 0.82rem;
    }
    .verified-box {
        background: linear-gradient(135deg, #0a2d0a, #0f4a1a);
        border: 1.5px solid #38a83d; border-radius: 12px;
        padding: 1rem 1.25rem; color: #86efac;
        font-family: 'Space Mono', monospace; font-size: 0.82rem;
    }
    .blockchain-badge {
        background: linear-gradient(135deg, #0a1f0a, #1a4a1a);
        color: #52c45a; padding: 0.4rem 0.9rem; border-radius: 8px;
        font-family: 'Space Mono', monospace; font-size: 0.77rem;
        word-break: break-all; border: 1px solid #2d5a2d;
    }
    .info-box { background: #f0fdf4; border-left: 4px solid #38a83d;
                padding: 0.75rem 1rem; border-radius: 0 10px 10px 0; margin: 0.5rem 0; }
    .warning-box { background: #fef3c7; border-left: 4px solid #d97706;
                   padding: 0.75rem 1rem; border-radius: 0 10px 10px 0; margin: 0.5rem 0; }
    .satellite-box {
        background: linear-gradient(135deg, #0a1f0a, #0f2d0f); color: #52c45a;
        border-radius: 12px; padding: 1rem 1.25rem;
        font-family: 'Space Mono', monospace; font-size: 0.82rem; border: 1px solid #1a4a1a;
    }
    .confidence-bar { height: 8px; border-radius: 4px; background: #e0f0e0; overflow: hidden; margin: 4px 0; }
    .confidence-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #38a83d, #52c45a); }
    .exif-tag { display: inline-block; background: #e8f5e9; border: 1px solid #a5d6a7;
                border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; color: #2e7d32;
                font-family: 'Space Mono', monospace; margin: 2px; }
    .no-exif-tag { display: inline-block; background: #ffebee; border: 1px solid #ef9a9a;
                   border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; color: #c62828;
                   font-family: 'Space Mono', monospace; margin: 2px; }
    .free-badge {
        background: linear-gradient(135deg, #1a3a5c, #1e4d8c);
        color: #90caf9; border: 1px solid #1e4d8c; border-radius: 20px;
        padding: 0.3rem 0.8rem; font-size: 0.75rem;
        font-family: 'Space Mono', monospace; font-weight: 700; display: inline-block;
    }
    div[data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, #0a1f0a 0%, #0f2d0f 50%, #071507 100%);
    }
    div[data-testid="stSidebarContent"] * { color: #c8f0ca !important; }
    .stButton button {
        background: linear-gradient(135deg, #25752d, #38a83d);
        color: white !important; border: none; border-radius: 10px;
        font-weight: 600; padding: 0.6rem 1.5rem; transition: all 0.2s;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #1e5c1e, #25752d);
        transform: translateY(-1px); box-shadow: 0 4px 12px rgba(56,168,61,0.35);
    }
    h1 { color: #0f2d0f !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    h2, h3 { color: #1a4a1a !important; font-family: 'Inter', sans-serif; }
    .smart-price-card {
        background: linear-gradient(135deg, #0a1f0a, #0f3a1a);
        border: 1px solid #2d6a2d; border-radius: 14px; padding: 1.25rem; color: #c8f0ca; margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KONSTANTLAR
# ─────────────────────────────────────────────
TREE_SPECIES = {
    "🌲 Archa (Juniper)":      {"co2": 22, "id": "archa"},
    "🌳 Terak (Poplar)":       {"co2": 48, "id": "terak"},
    "🌿 To'l (Willow)":        {"co2": 35, "id": "tol"},
    "🌳 Chinor (Plane Tree)":  {"co2": 56, "id": "chinor"},
    "🌰 Yong'oq (Walnut)":     {"co2": 40, "id": "yongoq"},
    "🍎 Olma (Apple)":         {"co2": 20, "id": "olma"},
    "🍑 Shaftoli (Peach)":     {"co2": 18, "id": "shaftoli"},
    "🌲 Shumto'l (Elm)":       {"co2": 30, "id": "shumtol"},
    "🌿 Qayin (Birch)":        {"co2": 25, "id": "qayin"},
    "🌳 Eman (Oak)":           {"co2": 48, "id": "eman"},
    "🍁 Zarang (Maple)":       {"co2": 32, "id": "zarang"},
    "🌿 Pista (Pistachio)":    {"co2": 15, "id": "pista"},
    "🌳 Mevali (Fruit mix)":   {"co2": 18, "id": "mevali"},
}
SPECIES_ID_TO_NAME = {v["id"]: k for k, v in TREE_SPECIES.items()}
CREDIT_PRICE_MIN = 40
CREDIT_PRICE_MAX = 80
CREDIT_PRICE_AVG = 65
UZS_RATE = 12700

# ─────────────────────────────────────────────
# YORDAMCHI FUNKSIYALAR
# ─────────────────────────────────────────────
def calculate_metrics(t_type, count, age):
    co2 = TREE_SPECIES.get(t_type, {}).get("co2", 20)
    co2_total = co2 * count * age
    kredit = co2_total / 1000
    return {
        "co2_per_year":    co2 * count,
        "co2_total_kg":    co2_total,
        "kredit":          kredit,
        "daromad_min":     kredit * CREDIT_PRICE_MIN,
        "daromad_max":     kredit * CREDIT_PRICE_MAX,
        "daromad_avg":     kredit * CREDIT_PRICE_AVG,
        "daromad_min_uzs": int(kredit * CREDIT_PRICE_MIN * UZS_RATE),
        "daromad_max_uzs": int(kredit * CREDIT_PRICE_MAX * UZS_RATE),
    }

def calculate_ai_metrics(t_type, count, age, height_m, diameter_cm, health_score=100):
    base = calculate_metrics(t_type, count, age)
    h_factor = min(height_m / max(age * 0.4 + 0.5, 0.1), 1.3)
    d_factor = min(diameter_cm / max(age * 0.8 + 2, 1),   1.3)
    mult = max(0.5, min(((h_factor + d_factor) / 2) * (health_score / 100), 1.4))
    k = base["kredit"] * mult
    return {**base,
            "co2_per_year":    round(base["co2_per_year"] * mult, 2),
            "kredit":          round(k, 6),
            "daromad_min":     round(k * CREDIT_PRICE_MIN, 4),
            "daromad_max":     round(k * CREDIT_PRICE_MAX, 4),
            "daromad_avg":     round(k * CREDIT_PRICE_AVG, 4),
            "daromad_min_uzs": int(k * CREDIT_PRICE_MIN * UZS_RATE),
            "daromad_max_uzs": int(k * CREDIT_PRICE_MAX * UZS_RATE),
            "ai_multiplier":   round(mult, 3)}

def generate_blockchain_hash(lat, lon, t_type, ts):
    raw = f"{lat}{lon}{t_type}{ts}{random.random()}"
    return "UZ-CC-" + hashlib.sha256(raw.encode()).hexdigest()[:24].upper()

def check_duplicate_location(lat, lon, existing_df, threshold_m=10):
    for _, row in existing_df.iterrows():
        dist = ((row['lat'] - lat)**2 + (row['lon'] - lon)**2)**0.5 * 111000
        if dist < threshold_m:
            return True, row['id']
    return False, None

def format_uzs(amount):
    return f"{int(amount):,} so'm".replace(",", " ")

# ─────────────────────────────────────────────
# EXIF TAHLIL
# ─────────────────────────────────────────────
def _dms_to_decimal(dms, ref):
    try:
        d, m, s = float(dms[0]), float(dms[1]), float(dms[2])
        dec = d + m / 60 + s / 3600
        return round(-dec if ref in ('S', 'W') else dec, 7)
    except Exception:
        return None

def extract_exif_data(image_bytes):
    result = {"has_exif": False, "has_gps": False, "gps_lat": None, "gps_lon": None,
              "camera_make": None, "camera_model": None, "datetime": None,
              "software": None, "is_likely_real": False, "real_score": 0, "flags": []}
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif_raw = img._getexif()
        if exif_raw is None:
            result["flags"].append("❌ EXIF ma'lumoti yo'q — internet rasmi bo'lishi mumkin")
            return result

        result["has_exif"] = True
        gps_info = None
        for tag_id, value in exif_raw.items():
            tag = TAGS.get(tag_id, "")
            if tag == "Make":           result["camera_make"]  = str(value).strip()
            elif tag == "Model":        result["camera_model"] = str(value).strip()
            elif tag == "DateTime":     result["datetime"]     = str(value)
            elif tag == "Software":     result["software"]     = str(value).strip()
            elif tag == "GPSInfo":
                gps_info = {GPSTAGS.get(k, k): v for k, v in value.items()}

        if gps_info and "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            lat = _dms_to_decimal(gps_info["GPSLatitude"],  gps_info.get("GPSLatitudeRef",  "N"))
            lon = _dms_to_decimal(gps_info["GPSLongitude"], gps_info.get("GPSLongitudeRef", "E"))
            result["has_gps"] = True
            result["gps_lat"] = lat
            result["gps_lon"] = lon
            result["flags"].append(f"✅ GPS: {lat:.5f}, {lon:.5f}")

        score = 0
        if result["camera_make"]:
            score += 30
            result["flags"].append(f"✅ Kamera: {result['camera_make']} {result['camera_model'] or ''}")
        else:
            result["flags"].append("⚠️ Kamera ma'lumoti yo'q")
        if result["has_gps"]:   score += 40
        else:                   result["flags"].append("⚠️ GPS ma'lumoti yo'q")
        if result["datetime"]:
            score += 15
            result["flags"].append(f"✅ Vaqt: {result['datetime']}")
        else:
            result["flags"].append("⚠️ Vaqt ma'lumoti yo'q")
        if result["has_exif"]:  score += 15
        if result["software"] and any(s in result["software"].lower()
                                       for s in ["photoshop","gimp","lightroom","canva","snapseed"]):
            score -= 25
            result["flags"].append(f"⚠️ Tahrirlash izi: {result['software']}")

        result["real_score"]     = max(0, min(score, 100))
        result["is_likely_real"] = result["real_score"] >= 50
    except Exception as e:
        result["flags"].append(f"⚠️ EXIF xato: {str(e)[:60]}")
    return result

# ─────────────────────────────────────────────
# BEPUL AI — Google Gemini
# ─────────────────────────────────────────────
def analyze_tree_with_gemini(image_bytes, api_key, mime_type="image/jpeg"):
    """
    Google Gemini 1.5 Flash — BEPUL (15 req/min, kuniga 1500 bepul)
    """
    if not api_key or len(api_key) < 10:
        return {"error": "Gemini API kalit kiritilmagan"}
    try:
        import google.generativeai as genai
    except ImportError:
        return {"error": "google-generativeai o'rnatilmagan. Terminal: pip install google-generativeai"}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        img_obj = Image.open(io.BytesIO(image_bytes))

        prompt = """Siz professional daraxt eksperti (arborist) va kompyuter ko'rish mutaxassisisiz.
Rasmni chuqur tahlil qiling va FAQAT JSON formatida javob bering. Boshqa hech narsa yozmang.

O'zbekistondagi mumkin bo'lgan turlar:
archa (juniper), terak (poplar), tol (willow), chinor (plane tree),
yongoq (walnut), olma (apple), shaftoli (peach), shumtol (elm),
qayin (birch), eman (oak), zarang (maple), pista (pistachio), mevali, noaniq

JSON (faqat JSON, boshqa hech narsa yo'q):
{
  "detected_species_uz": "o'zbek tilida tur nomi",
  "detected_species_id": "archa/terak/tol/chinor/yongoq/olma/shaftoli/shumtol/qayin/eman/zarang/pista/mevali/noaniq",
  "species_confidence": 0-100,
  "is_real_photo": true/false,
  "authenticity_score": 0-100,
  "authenticity_details": "nima ko'rindi",
  "is_ai_generated": true/false,
  "is_internet_image": true/false,
  "estimated_age_years": raqam,
  "estimated_height_m": raqam,
  "estimated_diameter_cm": raqam,
  "tree_health_label": "Sog'lom/O'rta/Kasal",
  "tree_health_score": 0-100,
  "visible_issues": "muammolar yoki null",
  "overall_verdict": "TASDIQLASH_MUMKIN/SHUBHALI/QABUL_QILINMAYDI",
  "verdict_reason": "yakuniy xulosa"
}"""

        response = model.generate_content([prompt, img_obj])
        raw = response.text.strip()

        # JSON tozalash
        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"): part = part[4:].strip()
                if part.startswith("{"):
                    raw = part
                    break
        raw = raw.strip()
        if raw.startswith("{"):
            return json.loads(raw)
        # Oxirgi urinish: { ... } ni topish
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
        return {"error": f"JSON topilmadi. Javob: {raw[:200]}"}

    except json.JSONDecodeError as e:
        return {"error": f"JSON xato: {str(e)[:80]}"}
    except Exception as e:
        err = str(e)
        if "API_KEY_INVALID" in err or "invalid" in err.lower():
            return {"error": "API kalit noto'g'ri. Gemini AI Studio dan yangi kalit oling."}
        if "quota" in err.lower() or "429" in err:
            return {"error": "Bepul limit tugadi (kuniga 1500). Ertaga qayta urining."}
        return {"error": f"Gemini xato: {err[:120]}"}


def smart_price_recommendation(total_credits):
    base   = CREDIT_PRICE_AVG
    demand = random.uniform(0.92, 1.12)
    season = 1.05 if datetime.now().month in [4, 5, 9, 10] else 0.97
    vol    = 1.02 if total_credits > 1 else 1.0
    rec    = round(max(CREDIT_PRICE_MIN, min(base * demand * season * vol, CREDIT_PRICE_MAX)), 2)
    return {
        "recommended_price": rec,
        "trend":        "📈 Oshmoqda" if demand > 1 else "📉 Tushmoqda",
        "season_label": "Yuqori sezon" if season > 1 else "Oddiy sezon",
        "best_time":    "Hozir sotish qulay!" if rec > CREDIT_PRICE_AVG else "Biroz kutish tavsiya etiladi",
    }

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for key, val in [
    ("tree_db", pd.DataFrame(columns=[
        "id","blockchain_id","turi","soni","yoshi","balandlik_m",
        "lat","lon","manzil","co2_yilik_kg","kredit",
        "daromad_min","daromad_max","daromad_avg",
        "holat","sertifikat_sana","ai_verified","ai_species",
        "exif_gps_lat","exif_gps_lon","authenticity_score"])),
    ("authenticated", False),
    ("current_user",  None),
    ("users_db",      {}),
    ("gemini_key",    ""),
    ("last_ai_result", None),
    ("last_exif",      None),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ══════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding:2.5rem 0 1.5rem'>
            <div style='font-size:4rem'>🌿</div>
            <h1 style='color:#0f2d0f !important; font-size:2.4rem; margin:0.2rem 0;
                        font-family:Inter,sans-serif; font-weight:800; letter-spacing:-0.02em'>
                CarbonVision
            </h1>
            <p style='color:#4a7c4a; font-size:0.95rem; margin-top:0.4rem'>
                O'zbekiston Karbon Kredit Platformasi
            </p>
            <div style='display:flex; gap:8px; justify-content:center; margin-top:0.75rem; flex-wrap:wrap'>
                <span class='free-badge'>🆓 Gemini AI (Bepul)</span>
                <span class='ai-badge'>🛰️ Satellite</span>
                <span class='ai-badge'>🔒 Blockchain</span>
            </div>
        </div>""", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        with tab1:
            email = st.text_input("Email", placeholder="email@example.com", key="le")
            pwd   = st.text_input("Parol", type="password", key="lp")
            if st.button("Kirish →", use_container_width=True):
                if email in st.session_state.users_db:
                    if st.session_state.users_db[email]["password"] == hashlib.md5(pwd.encode()).hexdigest():
                        st.session_state.authenticated = True
                        st.session_state.current_user  = st.session_state.users_db[email]
                        st.rerun()
                    else: st.error("❌ Parol noto'g'ri")
                else: st.error("❌ Foydalanuvchi topilmadi")

            st.divider()
            if st.button("🚀 Demo sifatida kirish", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.current_user  = {"name":"Demo Foydalanuvchi","email":"demo@cv.uz","region":"Toshkent"}
                if len(st.session_state.tree_db) == 0:
                    demo = [
                        {"id":"A1B2C3","blockchain_id":"UZ-CC-A1B2C3D4E5F6G7H8I9J0K1L2",
                         "turi":"🌳 Chinor (Plane Tree)","soni":2,"yoshi":10,"balandlik_m":8.0,
                         "lat":41.3111,"lon":69.2405,"manzil":"Chilonzor, bog'","co2_yilik_kg":112,
                         "kredit":1.12,"daromad_min":44.8,"daromad_max":89.6,"daromad_avg":72.8,
                         "holat":"✅ Tasdiqlangan","sertifikat_sana":"2024-01-15",
                         "ai_verified":True,"ai_species":"chinor",
                         "exif_gps_lat":41.3111,"exif_gps_lon":69.2405,"authenticity_score":88},
                        {"id":"D4E5F6","blockchain_id":"UZ-CC-D4E5F6G7H8I9J0K1L2M3N4",
                         "turi":"🌲 Archa (Juniper)","soni":3,"yoshi":5,"balandlik_m":3.5,
                         "lat":41.32,"lon":69.25,"manzil":"Yunusobod, hovli","co2_yilik_kg":66,
                         "kredit":0.33,"daromad_min":13.2,"daromad_max":26.4,"daromad_avg":21.45,
                         "holat":"✅ Tasdiqlangan","sertifikat_sana":"2024-03-20",
                         "ai_verified":True,"ai_species":"archa",
                         "exif_gps_lat":41.32,"exif_gps_lon":69.25,"authenticity_score":92},
                    ]
                    st.session_state.tree_db = pd.DataFrame(demo)
                st.rerun()

        with tab2:
            rn = st.text_input("To'liq ism", key="rn")
            re = st.text_input("Email",      key="re")
            rr = st.selectbox("Viloyat", ["Toshkent","Samarqand","Buxoro","Namangan","Andijon",
                                           "Farg'ona","Qashqadaryo","Surxondaryo","Xorazm",
                                           "Sirdaryo","Jizzax","Navoiy","Qoraqalpog'iston"])
            rp  = st.text_input("Parol", type="password", key="rp")
            rp2 = st.text_input("Parolni takrorlang", type="password", key="rp2")
            if st.button("Ro'yxatdan o'tish →", use_container_width=True):
                if not rn or not re or not rp: st.error("❌ Barcha maydonlarni to'ldiring")
                elif rp != rp2:                st.error("❌ Parollar mos kelmaydi")
                elif len(rp) < 6:              st.error("❌ Kamida 6 belgi")
                elif re in st.session_state.users_db: st.error("❌ Bu email ro'yxatda bor")
                else:
                    user = {"name":rn,"email":re,"region":rr,
                            "password":hashlib.md5(rp.encode()).hexdigest()}
                    st.session_state.users_db[re] = user
                    st.session_state.authenticated = True
                    st.session_state.current_user  = user
                    st.rerun()

# ══════════════════════════════════════════════
#  ASOSIY ILOVA
# ══════════════════════════════════════════════
def main_app():
    user = st.session_state.current_user
    df   = st.session_state.tree_db

    total_trees   = int(df['soni'].sum())   if len(df) > 0 else 0
    total_credits = df['kredit'].sum()       if len(df) > 0 else 0
    ai_v_count    = int(df['ai_verified'].sum()) if len(df) > 0 and 'ai_verified' in df.columns else 0
    api_ok        = len(st.session_state.gemini_key) > 10

    # SIDEBAR
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding:1.2rem 0 0.5rem'>
            <div style='font-size:2.5rem'>🌿</div>
            <div style='font-size:1.2rem; font-weight:800; color:#c8f0ca'>CarbonVision</div>
            <div style='font-size:0.7rem; color:#6abf6a; margin-top:2px; font-family:monospace'>
                GEMINI AI · BLOCKCHAIN · SATELLITE
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"**👤 {user.get('name','Foydalanuvchi')}**")
        st.markdown(f"📍 {user.get('region','Toshkent')}")
        st.divider()

        menu = st.radio("Bo'limlar:", [
            "📊 Dashboard",
            "🌳 Daraxt Sertifikatlash",
            "🗂️ Mening Daraxtlarim",
            "🗺️ Xarita",
            "🧮 Kalkulyator",
            "💰 Bozor (Marketplace)",
            "🏆 Reyting",
            "⚙️ AI Sozlamalari (Bepul)",
            "ℹ️ Tizim haqida",
        ])
        st.divider()
        st.markdown(f"🌳 **{total_trees}** ta daraxt")
        st.markdown(f"♻️ **{total_credits:.4f}** kredit")
        st.markdown(f"🤖 **{ai_v_count}** ta AI tasdiqlangan")
        st.markdown(f"💰 **${total_credits*CREDIT_PRICE_AVG:.2f}** potensial")
        st.divider()
        st.markdown("🟢 **Gemini AI: Faol**" if api_ok else "🔴 **AI: Sozlanmagan** → ⚙️ ga boring")
        st.divider()
        if st.button("🚪 Chiqish", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user  = None
            st.rerun()

    # ══════════════════════════════════════════
    #  DASHBOARD
    # ══════════════════════════════════════════
    if menu == "📊 Dashboard":
        st.title("📊 Boshqaruv Paneli")
        st.markdown(f"Salom, **{user.get('name','')}** 👋")

        total_co2      = df['co2_yilik_kg'].sum() if len(df) > 0 else 0
        total_earn_avg = df['daromad_avg'].sum()   if len(df) > 0 else 0
        total_earn_min = df['daromad_min'].sum()   if len(df) > 0 else 0
        total_earn_max = df['daromad_max'].sum()   if len(df) > 0 else 0
        verified_cnt   = len(df[df['holat']=='✅ Tasdiqlangan']) if len(df) > 0 else 0

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("🌳 Daraxtlar",      f"{total_trees} ta")
        c2.metric("♻️ Kreditlar",      f"{total_credits:.4f}")
        c3.metric("💨 CO₂/yil",        f"{total_co2:.0f} kg")
        c4.metric("💰 Potensial",       f"${total_earn_avg:.2f}")
        c5.metric("🤖 AI tasdiqlangan", f"{ai_v_count} ta")

        st.divider()
        ca, cb = st.columns(2)
        with ca:
            st.subheader("📋 Turlari bo'yicha")
            if len(df) > 0:
                sp = df.groupby('turi').agg({'soni':'sum','kredit':'sum'}).reset_index()
                sp.columns = ['Tur','Soni','Kredit']
                st.dataframe(sp, use_container_width=True, hide_index=True)
            else: st.info("Hali daraxt qo'shilmagan")
        with cb:
            st.subheader("📊 Statistika")
            avg_auth = df['authenticity_score'].mean() if len(df)>0 and 'authenticity_score' in df.columns else 0
            st.markdown(f"""
            <div style='display:grid; gap:0.6rem'>
                <div style='background:#f0fdf4;border-radius:10px;padding:.7rem 1rem;display:flex;justify-content:space-between'>
                    <span style='color:#4a7c4a'>✅ Tasdiqlangan</span><strong style='color:#15803d'>{verified_cnt} ta</strong>
                </div>
                <div style='background:#fef3c7;border-radius:10px;padding:.7rem 1rem;display:flex;justify-content:space-between'>
                    <span style='color:#92400e'>⏳ Kutilmoqda</span><strong style='color:#b45309'>{len(df)-verified_cnt} ta</strong>
                </div>
                <div style='background:#eff6ff;border-radius:10px;padding:.7rem 1rem;display:flex;justify-content:space-between'>
                    <span style='color:#1d4ed8'>🛡️ O'rtacha autentiklik</span><strong style='color:#1d4ed8'>{avg_auth:.0f}/100</strong>
                </div>
                <div style='background:#f0fdf4;border-radius:10px;padding:.7rem 1rem;display:flex;justify-content:space-between'>
                    <span style='color:#4a7c4a'>💰 Daromad diapazoni</span><strong style='color:#15803d'>${total_earn_min:.2f}–${total_earn_max:.2f}</strong>
                </div>
            </div>""", unsafe_allow_html=True)

        st.divider()
        st.subheader("📍 Xarita")
        if len(df) > 0:
            m_map = folium.Map(location=[41.3111,69.2405], zoom_start=11)
            for _, row in df.iterrows():
                color = 'green' if row['holat']=='✅ Tasdiqlangan' else 'orange'
                folium.Marker([row['lat'],row['lon']],
                    popup=folium.Popup(f"<b>{row['turi']}</b><br>{row['soni']} ta | {row['kredit']:.4f} kredit", max_width=200),
                    tooltip=f"{row['turi']} — {row['kredit']:.4f}",
                    icon=folium.Icon(color=color, icon='leaf', prefix='fa')
                ).add_to(m_map)
            st_folium(m_map, width=None, height=380, use_container_width=True)
        else: st.info("Xaritada ko'rsatish uchun daraxt qo'shing")

        st.markdown("""
        <div class='satellite-box'>
            🆓 GEMINI AI: Bepul (Google) | 🛰️ Satellite: Faol | 🔒 Blockchain: Faol<br>
            📸 EXIF GPS tekshiruvi | 🛡️ Anti-fraud: 10m radius | ♻️ Double-counting himoya
        </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  SERTIFIKATLASH
    # ══════════════════════════════════════════
    elif menu == "🌳 Daraxt Sertifikatlash":
        st.title("🌳 Yangi Daraxtni Sertifikatlash")
        st.markdown("**Gemini AI** (bepul) daraxt turini rasmdan aniqlaydi va soxtalikni tekshiradi")

        if not api_ok:
            st.warning("⚠️ AI uchun **⚙️ AI Sozlamalari** bo'limiga borib **bepul** Gemini API kalitini kiriting.")

        st.subheader("📸 1-qadam: Daraxt rasmini yuklang")
        photo = st.file_uploader("Daraxt rasmi (jpg/png/jpeg):", type=['jpg','png','jpeg'])

        ai_result   = None
        exif_result = None
        ai_species_id = None

        if photo is not None:
            image_bytes = photo.read()
            mime_type   = "image/jpeg" if photo.name.lower().endswith(("jpg","jpeg")) else "image/png"
            c_img, c_info = st.columns([1,1])

            with c_img:
                st.image(Image.open(io.BytesIO(image_bytes)), caption=f"📷 {photo.name}", use_container_width=True)

            with c_info:
                st.markdown("**🔍 EXIF / Metadata tahlili**")
                with st.spinner("EXIF tekshirilmoqda…"):
                    exif_result = extract_exif_data(image_bytes)
                    st.session_state.last_exif = exif_result

                rs = exif_result.get("real_score", 0)
                bar_c = "#38a83d" if rs>=60 else ("#f59e0b" if rs>=35 else "#ef4444")
                st.markdown(f"""
                <div style='margin-bottom:.75rem'>
                    <div style='display:flex;justify-content:space-between;font-size:.82rem;margin-bottom:4px'>
                        <span>📊 Haqiqiylik bahosi</span>
                        <strong style='color:{bar_c}'>{rs}/100</strong>
                    </div>
                    <div class='confidence-bar'>
                        <div class='confidence-fill' style='width:{rs}%;background:{bar_c}'></div>
                    </div>
                </div>""", unsafe_allow_html=True)

                for flag in exif_result.get("flags", []):
                    cls = "exif-tag" if flag.startswith("✅") else "no-exif-tag"
                    st.markdown(f"<span class='{cls}'>{flag}</span>", unsafe_allow_html=True)
                if exif_result.get("has_gps"):
                    st.success(f"📍 GPS: {exif_result['gps_lat']:.5f}, {exif_result['gps_lon']:.5f}")

            # GEMINI AI TAHLIL
            st.divider()
            if api_ok:
                with st.spinner("🤖 Gemini AI rasm tahlili — daraxt turi, autentiklik, parametrlar…"):
                    ai_result = analyze_tree_with_gemini(image_bytes, st.session_state.gemini_key, mime_type)
                    st.session_state.last_ai_result = ai_result

                if "error" in ai_result:
                    st.error(f"🤖 Gemini xatosi: {ai_result['error']}")
                    ai_result = None
                else:
                    verdict   = ai_result.get("overall_verdict", "SHUBHALI")
                    auth_sc   = ai_result.get("authenticity_score", 0)
                    is_real   = ai_result.get("is_real_photo", False)
                    is_ai_gen = ai_result.get("is_ai_generated", False)
                    box_cls   = "verified-box" if verdict=="TASDIQLASH_MUMKIN" else "fraud-alert"
                    v_icon    = {"TASDIQLASH_MUMKIN":"✅","SHUBHALI":"⚠️","QABUL_QILINMAYDI":"❌"}.get(verdict,"⚠️")

                    st.markdown(f"""
                    <div class='{box_cls}'>
                        <div style='font-size:1rem;font-weight:700;margin-bottom:.6rem'>
                            {v_icon} GEMINI AI XULOSA: {verdict.replace("_"," ")}
                        </div>
                        <div>🌳 Aniqlangan tur: <strong>{ai_result.get('detected_species_uz','—')}</strong>
                             (ishonch: {ai_result.get('species_confidence',0)}%)</div>
                        <div>📸 Haqiqiy rasm: {'✅ Ha' if is_real else "❌ Yo'q/Shubhali"} |
                             AI generatsiya: {'⚠️ Ehtimol' if is_ai_gen else '✅ Emas'}</div>
                        <div>🛡️ Autentiklik: {auth_sc}/100</div>
                        <div>📏 Taxminiy: {ai_result.get('estimated_age_years','?')} yil |
                             {ai_result.get('estimated_height_m','?')} m |
                             {ai_result.get('estimated_diameter_cm','?')} sm</div>
                        <div>💚 Sog'liq: {ai_result.get('tree_health_label','?')}
                             ({ai_result.get('tree_health_score',0)}/100)</div>
                        <div style='margin-top:.5rem;opacity:.8;font-size:.78rem'>
                            💬 {ai_result.get('verdict_reason','—')}
                        </div>
                    </div>""", unsafe_allow_html=True)

                    if ai_result.get("visible_issues"):
                        st.markdown(f"<div class='warning-box'>⚠️ {ai_result['visible_issues']}</div>", unsafe_allow_html=True)
                    ai_species_id = ai_result.get("detected_species_id")
            else:
                st.info("🤖 AI o'chirilgan. ⚙️ AI Sozlamalari ga boring.")

        st.divider()

        # FORMA
        with st.form("tree_form"):
            st.subheader("2️⃣ Daraxt ma'lumotlari")
            species_list = list(TREE_SPECIES.keys())
            def_idx = 0
            if ai_species_id and ai_species_id != "noaniq":
                matched = SPECIES_ID_TO_NAME.get(ai_species_id)
                if matched and matched in species_list:
                    def_idx = species_list.index(matched)

            col1,col2,col3 = st.columns(3)
            with col1:
                t_type = st.selectbox("Daraxt turi:", species_list, index=def_idx)
                co2_v  = TREE_SPECIES[t_type]["co2"]
                if ai_species_id and ai_species_id != "noaniq":
                    ai_nm = SPECIES_ID_TO_NAME.get(ai_species_id,"")
                    if ai_nm and ai_nm != t_type:
                        st.caption(f"🤖 AI tavsiya: **{ai_nm}**")
                    else:
                        st.caption("🤖 AI: tur ✅ tasdiqlandi")
                st.caption(f"ℹ️ Yiliga **{co2_v} kg** CO₂")

            with col2:
                ai_age = int(ai_result.get("estimated_age_years",5)) if ai_result and "error" not in ai_result else 5
                t_count = st.number_input("Soni:",       min_value=1,   max_value=1000,  value=1)
                t_age   = st.number_input("Yoshi (yil):",min_value=1,   max_value=200,   value=ai_age)

            with col3:
                ai_h = float(ai_result.get("estimated_height_m",  2.0)) if ai_result and "error" not in ai_result else 2.0
                ai_d = float(ai_result.get("estimated_diameter_cm",20))  if ai_result and "error" not in ai_result else 20
                t_height   = st.number_input("Balandlik (m):", min_value=0.1, max_value=100.0, value=ai_h, step=0.1)
                t_diameter = st.number_input("Diametr (sm):",  min_value=1,   max_value=500,   value=int(ai_d))
                if ai_result and "error" not in ai_result:
                    st.caption(f"🤖 AI: {ai_h}m / {int(ai_d)}sm")

            st.subheader("3️⃣ Joylashuv")
            exif_lat = exif_result["gps_lat"] if exif_result and exif_result.get("has_gps") else 41.2995
            exif_lon = exif_result["gps_lon"] if exif_result and exif_result.get("has_gps") else 69.2401
            gps_src  = "📍 GPS rasmdan avtomatik" if exif_result and exif_result.get("has_gps") else "✏️ Qo'lda kiritish"
            st.caption(f"Joylashuv: **{gps_src}**")

            c5,c6 = st.columns(2)
            with c5: lat = st.number_input("Kenglik:",  value=exif_lat, format="%.6f", min_value=37.0, max_value=46.0)
            with c6: lon = st.number_input("Uzunlik:", value=exif_lon, format="%.6f", min_value=55.0, max_value=75.0)
            location_name = st.text_input("Manzil nomi:", placeholder="masalan: Chilonzor-12, hovlim")

            # Hisob-kitob
            health_score = ai_result.get("tree_health_score",100) if ai_result and "error" not in ai_result else 100
            if ai_result and "error" not in ai_result:
                metrics = calculate_ai_metrics(t_type, t_count, t_age, t_height, t_diameter, health_score)
                mult_note = f" (AI korreksiya: ×{metrics.get('ai_multiplier',1)})"
            else:
                metrics   = calculate_metrics(t_type, t_count, t_age)
                mult_note = " (standart formula)"

            st.divider()
            st.subheader(f"📊 Hisob-kitob{mult_note}")
            pc1,pc2,pc3 = st.columns(3)
            pc1.metric("CO₂/yil",  f"{metrics['co2_per_year']:.1f} kg")
            pc2.metric("Kredit",   f"{metrics['kredit']:.6f}")
            pc3.metric("Daromad",  f"${metrics['daromad_avg']:.4f}")

            submitted = st.form_submit_button("🚀 Sertifikatlash va Kredit olish", use_container_width=True)

            if submitted:
                if ai_result and "error" not in ai_result:
                    if ai_result.get("overall_verdict") == "QABUL_QILINMAYDI":
                        st.error("❌ AI ANTI-FRAUD: Rasm soxta. Sertifikatlash rad etildi!")
                        st.stop()
                    if ai_result.get("is_ai_generated"):
                        st.error("❌ AI ANTI-FRAUD: Rasm AI tomonidan yaratilgan!")
                        st.stop()
                if len(st.session_state.tree_db) > 0:
                    is_dup, dup_id = check_duplicate_location(lat, lon, st.session_state.tree_db)
                    if is_dup:
                        st.error(f"⚠️ ANTI-FRAUD: Bu joylashuvda daraxt bor! (ID: #{dup_id})")
                        st.stop()

                ts = datetime.now()
                blockchain_id = generate_blockchain_hash(lat, lon, t_type, ts)
                short_id      = hashlib.sha256(f"{lat}{lon}{ts}".encode()).hexdigest()[:6].upper()
                holat = ("✅ Tasdiqlangan"
                         if ai_result and "error" not in ai_result
                            and ai_result.get("overall_verdict")=="TASDIQLASH_MUMKIN"
                            and ai_result.get("authenticity_score",0) >= 60
                         else "⏳ Tekshirilmoqda")

                new_data = {
                    "id": short_id, "blockchain_id": blockchain_id,
                    "turi": t_type, "soni": t_count, "yoshi": t_age, "balandlik_m": t_height,
                    "lat": lat, "lon": lon, "manzil": location_name or "Ko'rsatilmagan",
                    "co2_yilik_kg": metrics["co2_per_year"], "kredit": metrics["kredit"],
                    "daromad_min": metrics["daromad_min"], "daromad_max": metrics["daromad_max"],
                    "daromad_avg": metrics["daromad_avg"], "holat": holat,
                    "sertifikat_sana": ts.strftime("%Y-%m-%d"),
                    "ai_verified": bool(ai_result and "error" not in ai_result),
                    "ai_species": ai_result.get("detected_species_id","") if ai_result else "",
                    "exif_gps_lat": exif_result.get("gps_lat") if exif_result else None,
                    "exif_gps_lon": exif_result.get("gps_lon") if exif_result else None,
                    "authenticity_score": (
                        ai_result.get("authenticity_score",0) if ai_result and "error" not in ai_result
                        else exif_result.get("real_score",0) if exif_result else 0),
                }
                st.session_state.tree_db = pd.concat(
                    [st.session_state.tree_db, pd.DataFrame([new_data])], ignore_index=True)
                st.balloons()
                st.success(f"✅ Sertifikatlandi! ID: #{short_id} | {holat}")
                st.markdown(f"""
                <div class='blockchain-badge'>🔒 {blockchain_id}</div>
                <div class='info-box' style='margin-top:.5rem'>
                    {t_count} ta {t_type} | CO₂: {metrics['co2_per_year']:.1f} kg/yil |
                    Kredit: {metrics['kredit']:.6f} | Daromad: ${metrics['daromad_min']:.4f}–${metrics['daromad_max']:.4f}
                </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  MENING DARAXTLARIM
    # ══════════════════════════════════════════
    elif menu == "🗂️ Mening Daraxtlarim":
        st.title("🗂️ Mening Daraxtlarim")
        if len(df) == 0:
            st.info("🌱 Hali daraxt qo'shilmagan!")
            return
        search = st.text_input("🔍 Qidirish:", placeholder="Archa, Chinor…")
        dff = df.copy()
        if search:
            dff = dff[dff['turi'].str.contains(search,case=False,na=False) |
                      dff['manzil'].str.contains(search,case=False,na=False)]
        c1,c2,c3 = st.columns(3)
        c1.metric("Jami",   int(dff['soni'].sum()))
        c2.metric("Kredit", f"{dff['kredit'].sum():.6f}")
        c3.metric("Daromad",f"${dff['daromad_avg'].sum():.4f}")
        st.divider()
        cols = ['id','turi','soni','yoshi','manzil','co2_yilik_kg','kredit','daromad_min','daromad_max','holat','sertifikat_sana']
        if 'ai_verified'       in dff.columns: cols.append('ai_verified')
        if 'authenticity_score' in dff.columns: cols.append('authenticity_score')
        disp = dff[cols].copy()
        rename = ['ID','Tur','Soni','Yoshi','Manzil','CO₂/yil','Kredit','Min($)','Maks($)','Holat','Sana']
        if 'ai_verified'        in cols: rename.append('AI✓')
        if 'authenticity_score' in cols: rename.append('Autentiklik')
        disp.columns = rename
        st.dataframe(disp, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("🔒 Blockchain Sertifikatlar")
        for _, row in df.iterrows():
            with st.expander(f"{row['turi']} — #{row['id']} | {row['holat']}"):
                b1,b2 = st.columns(2)
                with b1:
                    st.markdown(f"**Tur:** {row['turi']}")
                    st.markdown(f"**Soni:** {row['soni']} | **Yoshi:** {row['yoshi']} yil")
                    st.markdown(f"**Manzil:** {row['manzil']}")
                    st.markdown(f"**Koordinata:** {row['lat']:.6f}, {row['lon']:.6f}")
                with b2:
                    st.markdown(f"**CO₂/yil:** {row['co2_yilik_kg']:.1f} kg")
                    st.markdown(f"**Kredit:** {row['kredit']:.6f}")
                    st.markdown(f"**Daromad:** ${row['daromad_min']:.4f}–${row['daromad_max']:.4f}")
                    st.markdown(f"**AI:** {'✅' if row.get('ai_verified') else '—'} | "
                                f"**Autentiklik:** {row.get('authenticity_score','—')}/100")
                st.markdown(f"<div class='blockchain-badge'>🔒 {row['blockchain_id']}</div>",
                            unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  XARITA
    # ══════════════════════════════════════════
    elif menu == "🗺️ Xarita":
        st.title("🗺️ Barcha Daraxtlar Xaritasi")
        m_map = folium.Map(location=[41.2995,64.5853], zoom_start=6)
        if len(df) > 0:
            for _, row in df.iterrows():
                color = 'green' if row['holat']=='✅ Tasdiqlangan' else 'orange'
                folium.Marker([row['lat'],row['lon']],
                    popup=folium.Popup(
                        f"<b>{row['turi']}</b><br>{row['manzil']}<br>"
                        f"{row['soni']} ta | {row['kredit']:.4f} kredit<br>"
                        f"Autentiklik: {row.get('authenticity_score','—')}/100", max_width=250),
                    tooltip=f"{row['turi']} | {row['kredit']:.4f}",
                    icon=folium.Icon(color=color, icon='leaf', prefix='fa')
                ).add_to(m_map)
        st_folium(m_map, width=None, height=550, use_container_width=True)

    # ══════════════════════════════════════════
    #  KALKULYATOR
    # ══════════════════════════════════════════
    elif menu == "🧮 Kalkulyator":
        st.title("🧮 Karbon Kredit Kalkulyatori")
        c1,c2,c3 = st.columns(3)
        with c1: k_type = st.selectbox("Daraxt turi:", list(TREE_SPECIES.keys()), key="ck")
        with c2:
            k_count  = st.number_input("Soni:",       min_value=1,   max_value=10000, value=1,  key="cc")
            k_age    = st.number_input("Yoshi (yil):",min_value=1,   max_value=200,   value=5,  key="ca")
        with c3:
            k_height = st.number_input("Balandlik (m):",min_value=0.1,max_value=100.0,value=3.0,step=0.1,key="ch")
            k_diam   = st.number_input("Diametr (sm):", min_value=1,  max_value=500,  value=20, key="cd")
            k_health = st.slider("Sog'liq (%):", min_value=10, max_value=100, value=100, key="hs")

        m_std = calculate_metrics(k_type, k_count, k_age)
        m_ai  = calculate_ai_metrics(k_type, k_count, k_age, k_height, k_diam, k_health)
        st.divider()
        cs,ca = st.columns(2)
        with cs:
            st.subheader("📐 Standart")
            st.metric("CO₂/yil", f"{m_std['co2_per_year']} kg")
            st.metric("Kredit",  f"{m_std['kredit']:.6f}")
            st.metric("Daromad", f"${m_std['daromad_avg']:.4f}")
        with ca:
            st.subheader(f"🤖 AI formula (×{m_ai.get('ai_multiplier',1)})")
            st.metric("CO₂/yil", f"{m_ai['co2_per_year']} kg", delta=f"{m_ai['co2_per_year']-m_std['co2_per_year']:+.1f}")
            st.metric("Kredit",  f"{m_ai['kredit']:.6f}",      delta=f"{m_ai['kredit']-m_std['kredit']:+.6f}")
            st.metric("Daromad", f"${m_ai['daromad_avg']:.4f}",delta=f"${m_ai['daromad_avg']-m_std['daromad_avg']:+.4f}")

        st.markdown(f"""
        <div class='smart-price-card'>
            <div style='font-size:.75rem;opacity:.7;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.6rem'>
                AI Daromad diapazoni
            </div>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:.75rem'>
                <div style='background:rgba(255,255,255,.07);border-radius:10px;padding:.85rem'>
                    <div style='font-size:.7rem;opacity:.7'>Min ($40/t)</div>
                    <div style='font-size:1.4rem;font-weight:700;color:#52c45a'>${m_ai['daromad_min']:.4f}</div>
                    <div style='font-size:.75rem;opacity:.6'>{format_uzs(m_ai['daromad_min_uzs'])}</div>
                </div>
                <div style='background:rgba(255,255,255,.07);border-radius:10px;padding:.85rem'>
                    <div style='font-size:.7rem;opacity:.7'>Maks ($80/t)</div>
                    <div style='font-size:1.4rem;font-weight:700;color:#f0c040'>${m_ai['daromad_max']:.4f}</div>
                    <div style='font-size:.75rem;opacity:.6'>{format_uzs(m_ai['daromad_max_uzs'])}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  MARKETPLACE
    # ══════════════════════════════════════════
    elif menu == "💰 Bozor (Marketplace)":
        st.title("💰 Aqlli Karbon Kreditlar Bozori")
        price_rec = smart_price_recommendation(total_credits)
        st.markdown(f"**Balans:** `{total_credits:.6f}` kredit = **${total_credits*CREDIT_PRICE_AVG:.4f}**")
        st.markdown(f"""
        <div class='ai-result-box'>
            🤖 GEMINI AI NARX TAHLILI<br><br>
            📊 Tavsiya etilgan: <strong style='color:#52c45a;font-size:1.1rem'>${price_rec['recommended_price']}/t</strong><br>
            {price_rec['trend']} | {price_rec['season_label']}<br>
            💡 {price_rec['best_time']}
        </div>""", unsafe_allow_html=True)

        st.divider()
        st.subheader("🏢 Xaridorlar")
        st.dataframe(pd.DataFrame({
            "Xaridor":    ["🚗 Tesla","🔍 Google","🍎 Apple","🏭 UzAuto","⚡ UzbekEnergo","🏗️ Qurilish UZ"],
            "Narx":       ["$75","$68","$72","$55","$50","$45"],
            "Talab":      ["500+","200+","300+","50+","100+","20+"],
            "Holat":      ["🟢 Ochiq"]*3 + ["🟡 Kutilmoqda","🟢 Ochiq","🟢 Ochiq"],
            "AI talab":   ["✅ AI Verified","✅ AI+Blockchain","✅ AI+Satellite","—","—","—"],
        }), use_container_width=True, hide_index=True)

        st.divider()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("O'rtacha", f"${CREDIT_PRICE_AVG}/t")
        c2.metric("AI tavsiya", f"${price_rec['recommended_price']}/t", delta=f"${price_rec['recommended_price']-CREDIT_PRICE_AVG:+.2f}")
        c3.metric("Min", f"${CREDIT_PRICE_MIN}/t")
        c4.metric("Maks", f"${CREDIT_PRICE_MAX}/t")

        st.divider()
        st.subheader("🔄 Kredit sotish")
        if total_credits > 0:
            sell_amount = st.number_input("Kredit miqdori:", min_value=0.0001, max_value=float(total_credits),
                                          value=min(0.001,float(total_credits)), format="%.6f")
            sell_price  = st.selectbox("Narx:", [
                f"${price_rec['recommended_price']}/t (AI tavsiya ⭐)",
                f"${CREDIT_PRICE_MIN}/t (min)", f"${CREDIT_PRICE_AVG}/t (o'rtacha)", f"${CREDIT_PRICE_MAX}/t (maks)"])
            pv = (price_rec['recommended_price'] if "AI" in sell_price
                  else CREDIT_PRICE_MIN if "min" in sell_price
                  else CREDIT_PRICE_MAX if "maks" in sell_price else CREDIT_PRICE_AVG)
            earn = sell_amount * pv
            st.markdown(f"**Tushum:** ${earn:.4f} = {format_uzs(earn*UZS_RATE)}")
            if st.button("💰 Sotish buyurtmasi", use_container_width=True):
                st.success(f"✅ {sell_amount:.6f} kredit → ${earn:.4f}. Xaridor bilan bog'lanasiz.")
        else:
            st.info("Avval daraxt qo'shing")

    # ══════════════════════════════════════════
    #  REYTING
    # ══════════════════════════════════════════
    elif menu == "🏆 Reyting":
        st.title("🏆 Foydalanuvchilar Reytingi")
        st.dataframe(pd.DataFrame([
            {"#":"🥇","Ism":"Abdullayev Jamshid","Viloyat":"Toshkent","Daraxt":142,"Kredit":4.832,"$":314.08,"AI✓":"✅"},
            {"#":"🥈","Ism":"Karimova Malika","Viloyat":"Samarqand","Daraxt":98,"Kredit":3.211,"$":208.72,"AI✓":"✅"},
            {"#":"🥉","Ism":"Toshmatov Dilshod","Viloyat":"Farg'ona","Daraxt":87,"Kredit":2.954,"$":192.0,"AI✓":"✅"},
            {"#":"4","Ism":"Yusupova Nilufar","Viloyat":"Buxoro","Daraxt":65,"Kredit":1.876,"$":121.9,"AI✓":"✅"},
            {"#":"5","Ism":"Mirzayev Bobur","Viloyat":"Namangan","Daraxt":54,"Kredit":1.542,"$":100.2,"AI✓":"—"},
            {"#":"…","Ism":f"👤 {user.get('name','Siz')}","Viloyat":user.get('region','Toshkent'),
             "Daraxt":total_trees,"Kredit":round(total_credits,6),
             "$":round(total_credits*CREDIT_PRICE_AVG,2),
             "AI✓":"✅" if ai_v_count>0 else "—"},
        ]), use_container_width=True, hide_index=True)

    # ══════════════════════════════════════════
    #  AI SOZLAMALARI (BEPUL)
    # ══════════════════════════════════════════
    elif menu == "⚙️ AI Sozlamalari (Bepul)":
        st.title("⚙️ Bepul AI Sozlamalari")
        st.markdown("""
        <div class='ai-result-box'>
            🆓 Google Gemini 1.5 Flash — <strong style='color:#52c45a'>TO'LIQICHA BEPUL!</strong><br><br>
            • ⚡ Sekundiga 15 so'rov | Kuniga 1,500 bepul so'rov<br>
            • 🌳 Daraxt turini rasmdan aniqlash<br>
            • 📸 Rasm autentikligini tekshirish (internet/AI generatsiya)<br>
            • 📏 Balandlik, diametr, yosh taxmini<br>
            • 💚 Daraxt sog'lig'ini baholash<br>
            • 💳 Karta kerak emas!
        </div>""", unsafe_allow_html=True)

        st.subheader("🔑 Gemini API Kalitini olish (5 daqiqa)")
        st.markdown("""
        **Qadamlar:**
        1. 🌐 [aistudio.google.com](https://aistudio.google.com) ga kiring (Google akkauntingiz bilan)
        2. **"Get API key"** tugmasini bosing
        3. **"Create API key"** tugmasini bosing
        4. Kalitni nusxalab quyidagi maydonga joylashtiring

        > 💡 **Hech qanday karta yoki to'lov talab qilinmaydi!**
        """)

        api_key_input = st.text_input(
            "Gemini API kalit:",
            value=st.session_state.gemini_key,
            type="password",
            placeholder="AIzaSy…",
            help="aistudio.google.com dan bepul oling"
        )

        c_save, c_test = st.columns(2)
        with c_save:
            if st.button("💾 Saqlash", use_container_width=True):
                st.session_state.gemini_key = api_key_input
                if len(api_key_input) > 10:
                    st.success("✅ API kalit saqlandi!")
                else:
                    st.warning("⚠️ Kalit juda qisqa")
        with c_test:
            if st.button("🧪 Test qilish", use_container_width=True):
                if len(api_key_input) < 10:
                    st.error("API kalit kiritilmagan")
                else:
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=api_key_input)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        resp  = model.generate_content("Say: Gemini AI ready for CarbonVision!")
                        st.success(f"✅ Gemini ulandi: {resp.text.strip()[:80]}")
                    except Exception as e:
                        err = str(e)
                        if "API_KEY_INVALID" in err or "invalid" in err.lower():
                            st.error("❌ API kalit noto'g'ri. aistudio.google.com dan yangi kalit oling.")
                        else:
                            st.error(f"❌ Xato: {err[:120]}")

        st.divider()
        st.subheader("📦 O'rnatish")
        st.code("pip install google-generativeai Pillow streamlit-folium folium", language="bash")

        st.divider()
        st.subheader("🆓 Bepul limitlar")
        st.markdown("""
        | Plan | Sekundiga | Kuniga | Oyiga | Narx |
        |------|-----------|--------|-------|------|
        | **Gemini 1.5 Flash** | 15 so'rov | 1,500 so'rov | 45,000 | **Bepul** |
        | Gemini 1.5 Pro | 2 so'rov | 50 so'rov | 1,500 | Bepul |

        > CarbonVision **Gemini 1.5 Flash** ishlatadi — eng tez va bepul variant.
        """)

    # ══════════════════════════════════════════
    #  TIZIM HAQIDA
    # ══════════════════════════════════════════
    elif menu == "ℹ️ Tizim haqida":
        st.title("ℹ️ CarbonVision haqida")
        st.markdown("""
        ## 🌿 CarbonVision — O'zbekiston AI Karbon Kredit Platformasi

        > *"G'arbda Tesla milliardlab dollar ishlatayotgan tizimni, biz O'zbekistonda oddiy aholiga ochiq qilamiz."*

        ---

        ### 🤖 AI qatlami — **Google Gemini 1.5 Flash (BEPUL)**
        | Funksiya | Tavsif |
        |----------|--------|
        | Daraxt turi aniqlash | Rasmdan avtomatik tur tanish |
        | Rasm autentikligi | Internet/AI generatsiya bloklash |
        | Parametr taxmini | Yosh, balandlik, diametr, sog'liq |
        | EXIF tekshiruvi | GPS, kamera modeli, vaqt tamg'asi |
        | Aqlli narx | Talab/taklif va sezon tahlili |

        ### 📐 Formulalar
        ```
        CO₂ (kg/yil)  = koeffitsient × soni
        AI_korreksiya = (h_factor + d_factor) / 2 × sog'liq%
        Kredit        = CO₂_kg × yosh × AI_korreksiya / 1000
        Daromad ($)   = kredit × $40–$80
        ```
        """)
        sp_df = pd.DataFrame([{"Tur":k,"CO₂/yil(kg)":v["co2"],"ID":v["id"]} for k,v in TREE_SPECIES.items()])
        st.dataframe(sp_df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if not st.session_state.authenticated:
    auth_page()
else:
    main_app()
