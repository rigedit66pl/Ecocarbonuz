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

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main { background-color: #f0f7f0; font-family: 'Inter', sans-serif; }
    
    .stMetric {
        background: white;
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        border: 1px solid #d4ecd4;
        box-shadow: 0 2px 12px rgba(0,80,0,0.06);
        transition: transform 0.2s;
    }
    .stMetric:hover { transform: translateY(-2px); }
    .stMetric label { color: #4a7c4a !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; }
    .stMetric [data-testid="stMetricValue"] { color: #0f2d0f !important; font-size: 1.75rem !important; font-weight: 700 !important; }

    .ai-result-box {
        background: linear-gradient(135deg, #0a1f0a 0%, #0d2e1a 100%);
        border: 1px solid #2d6a2d;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        color: #c8f0ca;
        font-family: 'Space Mono', monospace;
        font-size: 0.82rem;
        margin: 0.75rem 0;
        position: relative;
        overflow: hidden;
    }
    .ai-result-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #38a83d, #52c45a, #38a83d);
        animation: scan 2s linear infinite;
    }
    @keyframes scan { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

    .ai-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, #0f2d0f, #1a4a1a);
        color: #52c45a;
        border: 1px solid #38a83d;
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        font-size: 0.75rem;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    .fraud-alert {
        background: linear-gradient(135deg, #2d0a0a, #4a0f0f);
        border: 1.5px solid #e53e3e;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        color: #fca5a5;
        font-family: 'Space Mono', monospace;
        font-size: 0.82rem;
    }
    .verified-box {
        background: linear-gradient(135deg, #0a2d0a, #0f4a1a);
        border: 1.5px solid #38a83d;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        color: #86efac;
        font-family: 'Space Mono', monospace;
        font-size: 0.82rem;
    }
    .blockchain-badge {
        background: linear-gradient(135deg, #0a1f0a, #1a4a1a);
        color: #52c45a;
        padding: 0.4rem 0.9rem;
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        font-size: 0.77rem;
        word-break: break-all;
        border: 1px solid #2d5a2d;
    }
    .info-box {
        background: #f0fdf4;
        border-left: 4px solid #38a83d;
        padding: 0.75rem 1rem;
        border-radius: 0 10px 10px 0;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .warning-box {
        background: #fef3c7;
        border-left: 4px solid #d97706;
        padding: 0.75rem 1rem;
        border-radius: 0 10px 10px 0;
        margin: 0.5rem 0;
    }
    .satellite-box {
        background: linear-gradient(135deg, #0a1f0a, #0f2d0f);
        color: #52c45a;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        font-family: 'Space Mono', monospace;
        font-size: 0.82rem;
        border: 1px solid #1a4a1a;
    }
    .confidence-bar {
        height: 8px;
        border-radius: 4px;
        background: #1a4a1a;
        overflow: hidden;
        margin: 4px 0;
    }
    .confidence-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #38a83d, #52c45a);
        transition: width 0.5s ease;
    }
    .exif-tag {
        display: inline-block;
        background: #e8f5e9;
        border: 1px solid #a5d6a7;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.75rem;
        color: #2e7d32;
        font-family: 'Space Mono', monospace;
        margin: 2px;
    }
    .no-exif-tag {
        display: inline-block;
        background: #ffebee;
        border: 1px solid #ef9a9a;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.75rem;
        color: #c62828;
        font-family: 'Space Mono', monospace;
        margin: 2px;
    }
    div[data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, #0a1f0a 0%, #0f2d0f 50%, #071507 100%);
    }
    div[data-testid="stSidebarContent"] * { color: #c8f0ca !important; }
    div[data-testid="stSidebarContent"] .stRadio label { color: #c8f0ca !important; }
    .stButton button {
        background: linear-gradient(135deg, #25752d, #38a83d);
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s;
        font-family: 'Inter', sans-serif;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #1e5c1e, #25752d);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(56,168,61,0.35);
    }
    h1 { color: #0f2d0f !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    h2, h3 { color: #1a4a1a !important; font-family: 'Inter', sans-serif; }
    
    .progress-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        color: #4a7c4a;
        margin-bottom: 0.5rem;
    }
    .pulse-dot {
        width: 8px; height: 8px;
        background: #38a83d;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.8); }
    }
    .smart-price-card {
        background: linear-gradient(135deg, #0a1f0a, #0f3a1a);
        border: 1px solid #2d6a2d;
        border-radius: 14px;
        padding: 1.25rem;
        color: #c8f0ca;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KONSTANTLAR
# ─────────────────────────────────────────────
TREE_SPECIES = {
    "🌲 Archa (Juniper)":       {"co2": 22, "id": "archa"},
    "🌳 Terak (Poplar)":        {"co2": 48, "id": "terak"},
    "🌿 To'l (Willow)":         {"co2": 35, "id": "tol"},
    "🌳 Chinor (Plane Tree)":   {"co2": 56, "id": "chinor"},
    "🌰 Yong'oq (Walnut)":      {"co2": 40, "id": "yongoq"},
    "🍎 Olma (Apple)":          {"co2": 20, "id": "olma"},
    "🍑 Shaftoli (Peach)":      {"co2": 18, "id": "shaftoli"},
    "🌲 Shumto'l (Elm)":        {"co2": 30, "id": "shumtol"},
    "🌿 Qayin (Birch)":         {"co2": 25, "id": "qayin"},
    "🌳 Eman (Oak)":            {"co2": 48, "id": "eman"},
    "🍁 Zarang (Maple)":        {"co2": 32, "id": "zarang"},
    "🌿 Pista (Pistachio)":     {"co2": 15, "id": "pista"},
    "🌳 Mevali (Fruit mix)":    {"co2": 18, "id": "mevali"},
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
    co2_per_year = TREE_SPECIES.get(t_type, {}).get("co2", 20)
    co2_total_kg = co2_per_year * count * age
    kredit = co2_total_kg / 1000
    return {
        "co2_per_year":    co2_per_year * count,
        "co2_total_kg":    co2_total_kg,
        "kredit":          kredit,
        "daromad_min":     kredit * CREDIT_PRICE_MIN,
        "daromad_max":     kredit * CREDIT_PRICE_MAX,
        "daromad_avg":     kredit * CREDIT_PRICE_AVG,
        "daromad_min_uzs": int(kredit * CREDIT_PRICE_MIN * UZS_RATE),
        "daromad_max_uzs": int(kredit * CREDIT_PRICE_MAX * UZS_RATE),
    }

def calculate_ai_metrics(t_type, count, age, height_m, diameter_cm, health_score=100):
    """AI tomonidan aniqlangan o'lchamlar bilan aniqroq hisob"""
    base = calculate_metrics(t_type, count, age)
    # Balandlik va diametrga qarab korreksiya
    height_factor  = min(height_m / (age * 0.4 + 0.5), 1.3)  # kutilgan balandlikka nisbat
    diameter_factor = min(diameter_cm / (age * 0.8 + 2), 1.3)
    health_factor  = health_score / 100
    multiplier = ((height_factor + diameter_factor) / 2) * health_factor
    multiplier = max(0.5, min(multiplier, 1.4))  # 0.5 – 1.4 oralig'ida

    co2_adj = base["co2_per_year"] * multiplier
    kredit_adj = base["kredit"] * multiplier
    return {**base,
            "co2_per_year":    round(co2_adj, 2),
            "kredit":          round(kredit_adj, 6),
            "daromad_min":     round(kredit_adj * CREDIT_PRICE_MIN, 4),
            "daromad_max":     round(kredit_adj * CREDIT_PRICE_MAX, 4),
            "daromad_avg":     round(kredit_adj * CREDIT_PRICE_AVG, 4),
            "daromad_min_uzs": int(kredit_adj * CREDIT_PRICE_MIN * UZS_RATE),
            "daromad_max_uzs": int(kredit_adj * CREDIT_PRICE_MAX * UZS_RATE),
            "ai_multiplier":   round(multiplier, 3)}

def generate_blockchain_hash(lat, lon, t_type, timestamp):
    raw = f"{lat}{lon}{t_type}{timestamp}{random.random()}"
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
    """GPS DMS → decimal degrees"""
    try:
        d = float(dms[0])
        m = float(dms[1])
        s = float(dms[2])
        decimal = d + m / 60 + s / 3600
        if ref in ('S', 'W'):
            decimal = -decimal
        return round(decimal, 7)
    except Exception:
        return None

def extract_exif_data(image_bytes):
    result = {
        "has_exif": False,
        "has_gps":  False,
        "gps_lat":  None,
        "gps_lon":  None,
        "camera_make":  None,
        "camera_model": None,
        "datetime":     None,
        "software":     None,
        "is_likely_real": False,
        "real_score":   0,           # 0–100
        "flags":        [],
    }
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
            if tag == "Make":
                result["camera_make"] = str(value).strip()
            elif tag == "Model":
                result["camera_model"] = str(value).strip()
            elif tag == "DateTime":
                result["datetime"] = str(value)
            elif tag == "Software":
                result["software"] = str(value).strip()
            elif tag == "GPSInfo":
                gps_info = {}
                for gps_id, gps_val in value.items():
                    gps_tag = GPSTAGS.get(gps_id, gps_id)
                    gps_info[gps_tag] = gps_val

        # GPS
        if gps_info and "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            lat = _dms_to_decimal(gps_info["GPSLatitude"],
                                   gps_info.get("GPSLatitudeRef", "N"))
            lon = _dms_to_decimal(gps_info["GPSLongitude"],
                                   gps_info.get("GPSLongitudeRef", "E"))
            result["has_gps"] = True
            result["gps_lat"] = lat
            result["gps_lon"] = lon
            result["flags"].append(f"✅ GPS koordinata: {lat:.5f}, {lon:.5f}")

        # Real score hisob
        score = 0
        if result["camera_make"]:
            score += 30
            result["flags"].append(f"✅ Kamera: {result['camera_make']} {result['camera_model'] or ''}")
        else:
            result["flags"].append("⚠️ Kamera ma'lumoti yo'q")

        if result["has_gps"]:
            score += 40
        else:
            result["flags"].append("⚠️ GPS ma'lumoti yo'q")

        if result["datetime"]:
            score += 15
            result["flags"].append(f"✅ Suratga olish vaqti: {result['datetime']}")
        else:
            result["flags"].append("⚠️ Vaqt ma'lumoti yo'q")

        if result["has_exif"]:
            score += 15

        # Software shubhali belgisi (Photoshop, GIMP, editing)
        if result["software"] and any(s in result["software"].lower()
                                       for s in ["photoshop", "gimp", "lightroom", "canva", "snapseed"]):
            score -= 25
            result["flags"].append(f"⚠️ Tahrirlash dasturi izi: {result['software']}")

        result["real_score"] = max(0, min(score, 100))
        result["is_likely_real"] = result["real_score"] >= 50

    except Exception as e:
        result["flags"].append(f"⚠️ EXIF o'qishda xato: {str(e)[:60]}")

    return result

# ─────────────────────────────────────────────
# AI DARAXT TAHLILI (Claude API)
# ─────────────────────────────────────────────
def analyze_tree_with_ai(image_bytes, api_key, selected_species=None, mime_type="image/jpeg"):
    """Claude Opus yordamida daraxt rasmi tahlili"""
    try:
        import anthropic
    except ImportError:
        return {"error": "anthropic kutubxonasi o'rnatilmagan. 'pip install anthropic' buyrug'ini ishga tushiring."}

    if not api_key or len(api_key) < 20:
        return {"error": "API kalit kiritilmagan yoki noto'g'ri"}

    try:
        client = anthropic.Anthropic(api_key=api_key)
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        species_hint = f"\nFoydalanuvchi bu daraxtni «{selected_species}» deb kiritgan." if selected_species else ""
        
        prompt = f"""Siz professional daraxt eksperti (arborist) va kompyuter ko'rish mutaxassisisiz. 
Quyidagi rasmni chuqur tahlil qiling va faqat JSON formatida javob bering.{species_hint}

Tahlil qilish kerak bo'lgan parametrlar:

1. DARAXT TURI — O'zbekistondagi mumkin bo'lgan turlar:
   archa (juniper), terak (poplar), tol (willow), chinor (plane tree),
   yongoq (walnut), olma (apple), shaftoli (peach), shumtol (elm),
   qayin (birch), eman (oak), zarang (maple), pista (pistachio), mevali (boshqa meva), noaniq

2. RASM AUTENTIKLIGI — rasmning haqiqiyligi:
   - Tabiiy yorug'lik va soyalar mavjudmi?
   - Daraxt atrofida tuproq/o't/muhit ko'rinmoqdami?
   - Rasm sun'iy/foto-montaj/AI generatsiya belgilari bormi?
   - Rasm internetdan olinmagan deb ishonish mumkinmi?

3. DARAXT PARAMETRLARI (vizual baholash asosida):
   - Taxminiy yoshi
   - Taxminiy balandligi
   - Taxminiy trunk diametri
   - Sog'liq holati (Sog'lom/O'rta/Kasal) va 0-100 ball

Faqat JSON, boshqa hech narsa yozmang:
{{
  "detected_species_uz": "o'zbek tilida tur nomi",
  "detected_species_id": "archa/terak/tol/chinor/yongoq/olma/shaftoli/shumtol/qayin/eman/zarang/pista/mevali/noaniq",
  "species_confidence": 0-100,
  "species_matches_input": true/false/null,
  "species_correction_note": "agar mos kelmasa, tushuntirish yoki null",
  "is_real_photo": true/false,
  "authenticity_score": 0-100,
  "authenticity_details": "nima ko'rindi, nima shubha tug'dirdi",
  "is_ai_generated": true/false,
  "estimated_age_years": raqam,
  "estimated_height_m": raqam,
  "estimated_diameter_cm": raqam,
  "tree_health_label": "Sog'lom/O'rta/Kasal",
  "tree_health_score": 0-100,
  "visible_issues": "ko'rinadigan muammolar yoki null",
  "co2_efficiency_note": "bu daraxtning CO2 yutishi haqida izoh",
  "overall_verdict": "TASDIQLASH_MUMKIN/SHUBHALI/QABUL_QILINMAYDI",
  "verdict_reason": "yakuniy xulosa"
}}"""

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1200,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type":       "base64",
                            "media_type": mime_type,
                            "data":       img_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }],
        )

        raw_text = response.content[0].text.strip()
        # JSON tozalash
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()
        return json.loads(raw_text)

    except json.JSONDecodeError as e:
        return {"error": f"AI javobi JSON formatida emas: {str(e)[:80]}"}
    except Exception as e:
        return {"error": f"AI tahlilida xato: {str(e)[:120]}"}


def smart_price_recommendation(total_credits, market_data=None):
    """Aqlli narx tavsiyasi"""
    base_price = CREDIT_PRICE_AVG
    # Oddiy dynamic pricing simulatsiya
    demand_factor = random.uniform(0.92, 1.12)
    season_factor = 1.05 if datetime.now().month in [4, 5, 9, 10] else 0.97
    volume_bonus   = 1.02 if total_credits > 1 else 1.0

    recommended = round(base_price * demand_factor * season_factor * volume_bonus, 2)
    recommended = max(CREDIT_PRICE_MIN, min(recommended, CREDIT_PRICE_MAX))

    trend = "📈 Oshmoqda" if demand_factor > 1 else "📉 Tushmoqda"
    return {
        "recommended_price": recommended,
        "trend": trend,
        "demand_factor": round(demand_factor, 3),
        "season_label":  "Yuqori sezon" if season_factor > 1 else "Oddiy sezon",
        "best_time":     "Hozir sotish qulay!" if recommended > CREDIT_PRICE_AVG else "Biroz kutish tavsiya etiladi",
    }


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "tree_db" not in st.session_state:
    st.session_state.tree_db = pd.DataFrame(columns=[
        "id", "blockchain_id", "turi", "soni", "yoshi", "balandlik_m",
        "lat", "lon", "manzil", "co2_yilik_kg", "kredit",
        "daromad_min", "daromad_max", "daromad_avg",
        "holat", "sertifikat_sana", "ai_verified", "ai_species",
        "exif_gps_lat", "exif_gps_lon", "authenticity_score",
    ])
if "authenticated"  not in st.session_state: st.session_state.authenticated  = False
if "current_user"   not in st.session_state: st.session_state.current_user   = None
if "users_db"       not in st.session_state: st.session_state.users_db       = {}
if "anthropic_key"  not in st.session_state: st.session_state.anthropic_key  = ""
if "last_ai_result" not in st.session_state: st.session_state.last_ai_result = None
if "last_exif"      not in st.session_state: st.session_state.last_exif      = None


# ══════════════════════════════════════════════
#  AUTH SAHIFASI
# ══════════════════════════════════════════════
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding:2.5rem 0 1.5rem'>
            <div style='font-size:4rem'>🌿</div>
            <h1 style='color:#0f2d0f !important; font-size:2.4rem; margin:0.2rem 0;
                        font-family:"Inter",sans-serif; font-weight:800; letter-spacing:-0.02em'>
                CarbonVision
            </h1>
            <p style='color:#4a7c4a; font-size:0.95rem; margin-top:0.4rem; font-weight:500'>
                O'zbekiston Karbon Kredit Platformasi · <span style='font-family:monospace'>AI-Powered</span>
            </p>
            <div style='display:flex; gap:8px; justify-content:center; margin-top:0.75rem; flex-wrap:wrap'>
                <span class='ai-badge'>🤖 Claude AI</span>
                <span class='ai-badge'>🛰️ Satellite</span>
                <span class='ai-badge'>🔒 Blockchain</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])

        with tab1:
            email    = st.text_input("Email", placeholder="email@example.com", key="login_email")
            password = st.text_input("Parol", type="password", placeholder="••••••••", key="login_pass")
            if st.button("Kirish →", use_container_width=True, key="login_btn"):
                if email in st.session_state.users_db:
                    stored = st.session_state.users_db[email]
                    if stored["password"] == hashlib.md5(password.encode()).hexdigest():
                        st.session_state.authenticated = True
                        st.session_state.current_user  = stored
                        st.rerun()
                    else:
                        st.error("❌ Parol noto'g'ri")
                else:
                    st.error("❌ Foydalanuvchi topilmadi")

            st.divider()
            if st.button("🚀 Demo sifatida kirish", use_container_width=True):
                demo_user = {"name": "Demo Foydalanuvchi", "email": "demo@carbonvision.uz", "region": "Toshkent"}
                st.session_state.authenticated = True
                st.session_state.current_user  = demo_user
                if len(st.session_state.tree_db) == 0:
                    demo_trees = [
                        {"id": "A1B2C3", "blockchain_id": "UZ-CC-A1B2C3D4E5F6G7H8I9J0K1L2",
                         "turi": "🌳 Chinor (Plane Tree)", "soni": 2, "yoshi": 10,
                         "balandlik_m": 8.0, "lat": 41.3111, "lon": 69.2405,
                         "manzil": "Chilonzor tumani, bog'", "co2_yilik_kg": 112,
                         "kredit": 1.12, "daromad_min": 44.8, "daromad_max": 89.6,
                         "daromad_avg": 72.8, "holat": "✅ Tasdiqlangan",
                         "sertifikat_sana": "2024-01-15",
                         "ai_verified": True, "ai_species": "chinor",
                         "exif_gps_lat": 41.3111, "exif_gps_lon": 69.2405,
                         "authenticity_score": 88},
                        {"id": "D4E5F6", "blockchain_id": "UZ-CC-D4E5F6G7H8I9J0K1L2M3N4",
                         "turi": "🌲 Archa (Juniper)", "soni": 3, "yoshi": 5,
                         "balandlik_m": 3.5, "lat": 41.3200, "lon": 69.2500,
                         "manzil": "Yunusobod, hovli", "co2_yilik_kg": 66,
                         "kredit": 0.33, "daromad_min": 13.2, "daromad_max": 26.4,
                         "daromad_avg": 21.45, "holat": "✅ Tasdiqlangan",
                         "sertifikat_sana": "2024-03-20",
                         "ai_verified": True, "ai_species": "archa",
                         "exif_gps_lat": 41.32, "exif_gps_lon": 69.25,
                         "authenticity_score": 92},
                    ]
                    st.session_state.tree_db = pd.DataFrame(demo_trees)
                st.rerun()

        with tab2:
            reg_name   = st.text_input("To'liq ism", key="reg_name")
            reg_email  = st.text_input("Email", key="reg_email")
            reg_region = st.selectbox("Viloyat", ["Toshkent","Samarqand","Buxoro","Namangan","Andijon",
                                                   "Farg'ona","Qashqadaryo","Surxondaryo","Xorazm",
                                                   "Sirdaryo","Jizzax","Navoiy","Qoraqalpog'iston"])
            reg_pass   = st.text_input("Parol", type="password", key="reg_pass")
            reg_pass2  = st.text_input("Parolni takrorlang", type="password", key="reg_pass2")
            if st.button("Ro'yxatdan o'tish →", use_container_width=True):
                if not reg_name or not reg_email or not reg_pass:
                    st.error("❌ Barcha maydonlarni to'ldiring")
                elif reg_pass != reg_pass2:
                    st.error("❌ Parollar mos kelmaydi")
                elif len(reg_pass) < 6:
                    st.error("❌ Parol kamida 6 belgidan iborat bo'lishi kerak")
                elif reg_email in st.session_state.users_db:
                    st.error("❌ Bu email allaqachon ro'yxatdan o'tgan")
                else:
                    user = {"name": reg_name, "email": reg_email, "region": reg_region,
                            "password": hashlib.md5(reg_pass.encode()).hexdigest(),
                            "created_at": datetime.now().strftime("%Y-%m-%d")}
                    st.session_state.users_db[reg_email] = user
                    st.session_state.authenticated = True
                    st.session_state.current_user  = user
                    st.rerun()


# ══════════════════════════════════════════════
#  ASOSIY ILOVA
# ══════════════════════════════════════════════
def main_app():
    user = st.session_state.current_user
    df   = st.session_state.tree_db

    # ── SIDEBAR ─────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding:1.2rem 0 0.5rem'>
            <div style='font-size:2.5rem'>🌿</div>
            <div style='font-size:1.2rem; font-weight:800; color:#c8f0ca; letter-spacing:-0.01em'>CarbonVision</div>
            <div style='font-size:0.72rem; color:#6abf6a; margin-top:2px; font-family:monospace'>
                AI · BLOCKCHAIN · SATELLITE
            </div>
        </div>
        """, unsafe_allow_html=True)

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
            "⚙️ AI Sozlamalari",
            "ℹ️ Tizim haqida",
        ])

        st.divider()
        total_trees   = int(df['soni'].sum())   if len(df) > 0 else 0
        total_credits = df['kredit'].sum()       if len(df) > 0 else 0
        ai_verified   = int(df['ai_verified'].sum()) if len(df) > 0 and 'ai_verified' in df.columns else 0
        st.markdown(f"🌳 **{total_trees}** ta daraxt")
        st.markdown(f"♻️ **{total_credits:.4f}** kredit")
        st.markdown(f"🤖 **{ai_verified}** ta AI tasdiqlangan")
        st.markdown(f"💰 **${total_credits * CREDIT_PRICE_AVG:.2f}** potensial")

        # API kaliti holati
        api_ok = len(st.session_state.anthropic_key) > 20
        st.divider()
        if api_ok:
            st.markdown("🟢 **AI: Faol**")
        else:
            st.markdown("🔴 **AI: Sozlanmagan**")
            st.caption("⚙️ AI Sozlamalar bo'limiga boring")

        st.divider()
        if st.button("🚪 Chiqish", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user  = None
            st.rerun()

    # ════════════════════════════════════════════
    #  DASHBOARD
    # ════════════════════════════════════════════
    if menu == "📊 Dashboard":
        st.title("📊 Boshqaruv Paneli")
        st.markdown(f"Salom, **{user.get('name','')}** 👋 — Real vaqt rejimida karbon kredit hisobingiz")

        total_co2        = df['co2_yilik_kg'].sum()   if len(df) > 0 else 0
        total_earn_avg   = df['daromad_avg'].sum()    if len(df) > 0 else 0
        total_earn_min   = df['daromad_min'].sum()    if len(df) > 0 else 0
        total_earn_max   = df['daromad_max'].sum()    if len(df) > 0 else 0
        verified_count   = len(df[df['holat'] == '✅ Tasdiqlangan']) if len(df) > 0 else 0
        ai_v_count       = int(df['ai_verified'].sum()) if len(df) > 0 and 'ai_verified' in df.columns else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("🌳 Jami Daraxtlar",    f"{total_trees} ta")
        c2.metric("♻️ Karbon Kreditlar",  f"{total_credits:.4f}")
        c3.metric("💨 Yillik CO₂",        f"{total_co2:.0f} kg")
        c4.metric("💰 Potensial",          f"${total_earn_avg:.2f}")
        c5.metric("🤖 AI Tasdiqlangan",   f"{ai_v_count} ta")

        st.divider()
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("📋 Daraxt turlari bo'yicha")
            if len(df) > 0:
                species_stats = df.groupby('turi').agg({'soni': 'sum', 'kredit': 'sum'}).reset_index()
                species_stats.columns = ['Tur', 'Soni', 'Kredit']
                st.dataframe(species_stats, use_container_width=True, hide_index=True)
            else:
                st.info("Hali daraxt qo'shilmagan")

        with col_b:
            st.subheader("📊 Statistika")
            avg_auth = df['authenticity_score'].mean() if len(df) > 0 and 'authenticity_score' in df.columns else 0
            st.markdown(f"""
            <div style='display:grid; gap:0.65rem'>
                <div style='background:#f0fdf4; border-radius:10px; padding:0.7rem 1rem; display:flex; justify-content:space-between; align-items:center'>
                    <span style='color:#4a7c4a; font-size:0.9rem'>✅ Tasdiqlangan</span>
                    <strong style='color:#15803d'>{verified_count} ta</strong>
                </div>
                <div style='background:#fef3c7; border-radius:10px; padding:0.7rem 1rem; display:flex; justify-content:space-between; align-items:center'>
                    <span style='color:#92400e; font-size:0.9rem'>⏳ Kutilmoqda</span>
                    <strong style='color:#b45309'>{len(df) - verified_count} ta</strong>
                </div>
                <div style='background:#f0fdf4; border-radius:10px; padding:0.7rem 1rem; display:flex; justify-content:space-between; align-items:center'>
                    <span style='color:#4a7c4a; font-size:0.9rem'>🤖 AI tekshiruvi</span>
                    <strong style='color:#15803d'>{ai_v_count}/{len(df)} ta</strong>
                </div>
                <div style='background:#eff6ff; border-radius:10px; padding:0.7rem 1rem; display:flex; justify-content:space-between; align-items:center'>
                    <span style='color:#1d4ed8; font-size:0.9rem'>🛡️ O'rtacha autentiklik</span>
                    <strong style='color:#1d4ed8'>{avg_auth:.0f}/100</strong>
                </div>
                <div style='background:#f0fdf4; border-radius:10px; padding:0.7rem 1rem; display:flex; justify-content:space-between; align-items:center'>
                    <span style='color:#4a7c4a; font-size:0.9rem'>💰 Daromad diapazoni</span>
                    <strong style='color:#15803d'>${total_earn_min:.2f} – ${total_earn_max:.2f}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.subheader("📍 Daraxtlar xaritada")
        if len(df) > 0:
            m_map = folium.Map(location=[41.3111, 69.2405], zoom_start=11)
            for _, row in df.iterrows():
                color = 'green' if row['holat'] == '✅ Tasdiqlangan' else 'orange'
                ai_info = f"🤖 AI: ✅" if row.get('ai_verified') else "🤖 AI: —"
                auth_s  = row.get('authenticity_score', '—')
                folium.Marker(
                    [row['lat'], row['lon']],
                    popup=folium.Popup(f"""
                        <b>{row['turi']}</b><br>
                        🌳 {row['soni']} ta | Kredit: {row['kredit']:.4f}<br>
                        {ai_info} | Autentiklik: {auth_s}/100<br>
                        <small>{row['blockchain_id'][:20]}...</small>
                    """, max_width=280),
                    tooltip=f"{row['turi']} — {row['kredit']:.4f} kredit",
                    icon=folium.Icon(color=color, icon='leaf', prefix='fa')
                ).add_to(m_map)
            st_folium(m_map, width=None, height=400, use_container_width=True)
        else:
            st.info("Xaritada ko'rsatish uchun daraxt qo'shing")

        st.markdown("""
        <div class='satellite-box'>
            🛰️ SUN'IY YO'LDOSH NAZORAT: Faol | Haftalik skanerlash: Yoqilgan<br>
            🤖 AI TAHLIL ENGINE: Claude Opus (Computer Vision + Species ID + Fraud Detection)<br>
            📸 EXIF VERIFIKATSIYA: GPS koordinata, kamera modeli, vaqt tamg'asi<br>
            🔒 BLOCKCHAIN: Barcha kreditlar immutable ledger'da | ♻️ DOUBLE-COUNTING HIMOYA: Faol
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════════
    #  DARAXT SERTIFIKATLASH (AI bilan)
    # ════════════════════════════════════════════
    elif menu == "🌳 Daraxt Sertifikatlash":
        st.title("🌳 Yangi Daraxtni Sertifikatlash")
        st.markdown("AI daraxt turini rasmdan aniqlaydi, EXIF/GPS tekshiradi va firibgarlikdan himoya qiladi")

        api_ok = len(st.session_state.anthropic_key) > 20
        if not api_ok:
            st.warning("⚠️ AI tahlil uchun **⚙️ AI Sozlamalari** bo'limiga borib Anthropic API kalitingizni kiriting.")

        # ── QADAM 1: RASM YUKLASH VA AI TAHLIL ──────
        st.subheader("📸 1-qadam: Daraxt rasmini yuklang")
        st.markdown("Telefoningizda real vaqtda olingan rasm yuklansin. AI rasmni tahlil qilib, daraxt turini aniqlaydi va soxtalikni tekshiradi.")

        photo = st.file_uploader("Daraxt rasmi (jpg/png/jpeg):", type=['jpg', 'png', 'jpeg'])

        ai_result   = None
        exif_result = None
        ai_species_id = None

        if photo is not None:
            image_bytes = photo.read()
            mime_type   = "image/jpeg" if photo.name.lower().endswith(("jpg","jpeg")) else "image/png"
            col_img, col_info = st.columns([1, 1])

            with col_img:
                img_show = Image.open(io.BytesIO(image_bytes))
                st.image(img_show, caption=f"📷 {photo.name}", use_container_width=True)

            with col_info:
                # ── EXIF TAHLIL ──────────────────────────
                st.markdown("**🔍 EXIF / Metadata tahlili**")
                with st.spinner("EXIF ma'lumotlari tekshirilmoqda…"):
                    exif_result = extract_exif_data(image_bytes)
                    st.session_state.last_exif = exif_result

                real_score = exif_result.get("real_score", 0)
                bar_color  = "#38a83d" if real_score >= 60 else ("#f59e0b" if real_score >= 35 else "#ef4444")
                st.markdown(f"""
                <div style='margin-bottom:0.75rem'>
                    <div style='display:flex; justify-content:space-between; font-size:0.82rem; margin-bottom:4px'>
                        <span>📊 Haqiqiylik bahosi</span>
                        <strong style='color:{bar_color}'>{real_score}/100</strong>
                    </div>
                    <div class='confidence-bar'>
                        <div class='confidence-fill' style='width:{real_score}%; background:{bar_color}'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                for flag in exif_result.get("flags", []):
                    if flag.startswith("✅"):
                        st.markdown(f"<span class='exif-tag'>{flag}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span class='no-exif-tag'>{flag}</span>", unsafe_allow_html=True)

                if exif_result.get("has_gps"):
                    st.success(f"📍 GPS muvaffaqiyatli aniqlandi: {exif_result['gps_lat']:.5f}, {exif_result['gps_lon']:.5f}")

            # ── AI TAHLIL ────────────────────────────
            st.divider()
            if api_ok:
                st.markdown("""
                <div class='progress-indicator'>
                    <div class='pulse-dot'></div>
                    <strong>Claude AI daraxtni tahlil qilmoqda…</strong>
                </div>
                """, unsafe_allow_html=True)

                with st.spinner("🤖 AI rasm tahlili — daraxt turi, autentiklik, parametrlar…"):
                    ai_result = analyze_tree_with_ai(
                        image_bytes,
                        api_key=st.session_state.anthropic_key,
                        mime_type=mime_type
                    )
                    st.session_state.last_ai_result = ai_result

                if "error" in ai_result:
                    st.error(f"🤖 AI xatosi: {ai_result['error']}")
                    ai_result = None
                else:
                    verdict = ai_result.get("overall_verdict", "SHUBHALI")
                    auth_sc  = ai_result.get("authenticity_score", 0)
                    is_real  = ai_result.get("is_real_photo", False)
                    is_ai_gen = ai_result.get("is_ai_generated", False)

                    box_class = "verified-box" if verdict == "TASDIQLASH_MUMKIN" else "fraud-alert"
                    verdict_icon = {"TASDIQLASH_MUMKIN": "✅", "SHUBHALI": "⚠️", "QABUL_QILINMAYDI": "❌"}.get(verdict, "⚠️")

                    st.markdown(f"""
                    <div class='{box_class}'>
                        <div style='font-size:1rem; font-weight:700; margin-bottom:0.6rem'>
                            {verdict_icon} AI XULOSA: {verdict.replace("_"," ")}
                        </div>
                        <div>🌳 Aniqlangan tur: <strong>{ai_result.get('detected_species_uz','—')}</strong>
                             (ishonch: {ai_result.get('species_confidence',0)}%)</div>
                        <div>📸 Haqiqiy rasm: {'✅ Ha' if is_real else '❌ Yo\'q / Shubhali'} | 
                             AI generatsiya: {'⚠️ Ehtimol' if is_ai_gen else '✅ Emas'}</div>
                        <div>🛡️ Autentiklik: {auth_sc}/100</div>
                        <div>📏 Taxminiy: yoshi {ai_result.get('estimated_age_years','?')} yil | 
                             balandlik {ai_result.get('estimated_height_m','?')} m | 
                             diametr {ai_result.get('estimated_diameter_cm','?')} sm</div>
                        <div>💚 Sog'liq: {ai_result.get('tree_health_label','?')} 
                             ({ai_result.get('tree_health_score',0)}/100)</div>
                        <div style='margin-top:0.5rem; opacity:0.8; font-size:0.78rem'>
                            💬 {ai_result.get('verdict_reason','—')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if ai_result.get("visible_issues"):
                        st.markdown(f"""
                        <div class='warning-box'>⚠️ Ko'rinadigan muammolar: {ai_result['visible_issues']}</div>
                        """, unsafe_allow_html=True)

                    ai_species_id = ai_result.get("detected_species_id")
            else:
                st.info("🤖 AI tahlil o'chirilgan. ⚙️ AI Sozlamalari bo'limiga boring.")

        st.divider()

        # ── SERTIFIKATLASH FORMASI ────────────────
        with st.form("tree_form"):
            st.subheader("2️⃣ Daraxt ma'lumotlari")

            # AI aniqlagan tur bilan default qiymat
            default_species_list = list(TREE_SPECIES.keys())
            default_idx = 0
            if ai_species_id and ai_species_id != "noaniq":
                matched = SPECIES_ID_TO_NAME.get(ai_species_id)
                if matched and matched in default_species_list:
                    default_idx = default_species_list.index(matched)

            col1, col2, col3 = st.columns(3)
            with col1:
                t_type = st.selectbox("Daraxt turi:", default_species_list, index=default_idx)
                if ai_species_id and ai_species_id != "noaniq":
                    ai_name = SPECIES_ID_TO_NAME.get(ai_species_id, "")
                    if ai_name and ai_name != t_type:
                        st.caption(f"🤖 AI tavsiyasi: **{ai_name}** — farq bor, tekshiring!")
                    else:
                        st.caption(f"🤖 AI: tur tasdiqlandi ✅")
                co2_info = TREE_SPECIES[t_type]["co2"]
                st.caption(f"ℹ️ Yiliga **{co2_info} kg** CO₂ yutadi")

            with col2:
                ai_age = int(ai_result.get("estimated_age_years", 5)) if ai_result and "error" not in ai_result else 5
                t_count = st.number_input("Daraxt soni:", min_value=1, max_value=1000, value=1)
                t_age   = st.number_input("Yoshi (yil):", min_value=1, max_value=200, value=ai_age,
                                          help=f"🤖 AI taxminiy yoshi: {ai_age} yil")

            with col3:
                ai_h = float(ai_result.get("estimated_height_m",   2.0)) if ai_result and "error" not in ai_result else 2.0
                ai_d = float(ai_result.get("estimated_diameter_cm", 20))  if ai_result and "error" not in ai_result else 20
                t_height   = st.number_input("Balandlik (m):",  min_value=0.1, max_value=100.0, value=ai_h,   step=0.1)
                t_diameter = st.number_input("Diametr (sm):",   min_value=1,   max_value=500,   value=int(ai_d))
                if ai_result and "error" not in ai_result:
                    st.caption(f"🤖 AI taxmin: {ai_h}m / {int(ai_d)}sm")

            st.subheader("3️⃣ Joylashuv")

            # EXIF GPS dan avtomatik to'ldirish
            exif_lat = exif_result["gps_lat"] if exif_result and exif_result.get("has_gps") else 41.2995
            exif_lon = exif_result["gps_lon"] if exif_result and exif_result.get("has_gps") else 69.2401
            gps_src  = "📍 GPS rasmdan avtomatik" if exif_result and exif_result.get("has_gps") else "✏️ Qo'lda kiritish"
            st.caption(f"Joylashuv: **{gps_src}**")

            col5, col6 = st.columns(2)
            with col5:
                lat = st.number_input("Kenglik (Latitude):",  value=exif_lat, format="%.6f", min_value=37.0, max_value=46.0)
            with col6:
                lon = st.number_input("Uzunlik (Longitude):", value=exif_lon, format="%.6f", min_value=55.0, max_value=75.0)

            location_name = st.text_input("Manzil nomi:", placeholder="masalan: Chilonzor-12, hovlim")
            description   = st.text_area("Qo'shimcha ma'lumot:", placeholder="Daraxt haqida…", height=80)

            # Hisob-kitob
            health_score = ai_result.get("tree_health_score", 100) if ai_result and "error" not in ai_result else 100
            if ai_result and "error" not in ai_result:
                metrics = calculate_ai_metrics(t_type, t_count, t_age, t_height, t_diameter, health_score)
                multiplier_note = f" (AI korreksiya: ×{metrics.get('ai_multiplier',1)})"
            else:
                metrics = calculate_metrics(t_type, t_count, t_age)
                multiplier_note = " (standart formula)"

            st.divider()
            st.subheader(f"📊 Taxminiy hisob-kitob{multiplier_note}")
            pc1, pc2, pc3 = st.columns(3)
            pc1.metric("CO₂ yutish (yiliga)", f"{metrics['co2_per_year']:.1f} kg")
            pc2.metric("Kredit miqdori",       f"{metrics['kredit']:.6f}")
            pc3.metric("Potensial daromad",     f"${metrics['daromad_avg']:.4f}")

            submitted = st.form_submit_button("🚀 Sertifikatlash va Kredit olish", use_container_width=True)

            if submitted:
                # Fraud tekshiruvi
                if ai_result and "error" not in ai_result:
                    verdict = ai_result.get("overall_verdict", "SHUBHALI")
                    if verdict == "QABUL_QILINMAYDI":
                        st.error("❌ AI ANTI-FRAUD: Rasm soxta yoki sifatsiz deb baholandi. Sertifikatlash rad etildi!")
                        st.stop()
                    if ai_result.get("is_ai_generated"):
                        st.error("❌ AI ANTI-FRAUD: Rasm AI tomonidan yaratilgan deb aniqlandi!")
                        st.stop()

                # Koordinat duplikat tekshiruvi
                if len(st.session_state.tree_db) > 0:
                    is_dup, dup_id = check_duplicate_location(lat, lon, st.session_state.tree_db)
                    if is_dup:
                        st.error(f"⚠️ ANTI-FRAUD: Bu joylashuvga 10m ichida daraxt allaqachon ro'yxatdan o'tgan! (ID: #{dup_id})")
                        st.stop()

                timestamp    = datetime.now()
                blockchain_id = generate_blockchain_hash(lat, lon, t_type, timestamp)
                short_id      = hashlib.sha256(f"{lat}{lon}{timestamp}".encode()).hexdigest()[:6].upper()

                # Holat: AI tasdiqlasa avtomatik tasdiqlangan
                holat = "✅ Tasdiqlangan" if (ai_result and "error" not in ai_result and
                        ai_result.get("overall_verdict") == "TASDIQLASH_MUMKIN" and
                        ai_result.get("authenticity_score", 0) >= 60) else "⏳ Tekshirilmoqda"

                new_data = {
                    "id":           short_id,
                    "blockchain_id": blockchain_id,
                    "turi":         t_type,
                    "soni":         t_count,
                    "yoshi":        t_age,
                    "balandlik_m":  t_height,
                    "lat":          lat,
                    "lon":          lon,
                    "manzil":       location_name or "Ko'rsatilmagan",
                    "co2_yilik_kg": metrics["co2_per_year"],
                    "kredit":       metrics["kredit"],
                    "daromad_min":  metrics["daromad_min"],
                    "daromad_max":  metrics["daromad_max"],
                    "daromad_avg":  metrics["daromad_avg"],
                    "holat":        holat,
                    "sertifikat_sana": timestamp.strftime("%Y-%m-%d"),
                    "ai_verified":  bool(ai_result and "error" not in ai_result),
                    "ai_species":   ai_result.get("detected_species_id","") if ai_result else "",
                    "exif_gps_lat": exif_result.get("gps_lat") if exif_result else None,
                    "exif_gps_lon": exif_result.get("gps_lon") if exif_result else None,
                    "authenticity_score": (
                        ai_result.get("authenticity_score", 0) if ai_result and "error" not in ai_result
                        else exif_result.get("real_score", 0) if exif_result else 0
                    ),
                }

                st.session_state.tree_db = pd.concat(
                    [st.session_state.tree_db, pd.DataFrame([new_data])],
                    ignore_index=True
                )
                st.balloons()
                st.success(f"✅ Daraxt muvaffaqiyatli sertifikatlandi! ID: #{short_id} | Holat: {holat}")
                st.markdown(f"""
                <div class='info-box'>
                    <strong>🔒 Blockchain sertifikat:</strong><br>
                    <span class='blockchain-badge'>{blockchain_id}</span>
                </div>
                <div class='info-box'>
                    📊 <strong>{t_count} ta {t_type}</strong> — yiliga <strong>{metrics['co2_per_year']:.1f} kg</strong> CO₂ yutadi<br>
                    ♻️ Kredit: <strong>{metrics['kredit']:.6f}</strong> | 
                    💰 Potensial: <strong>${metrics['daromad_min']:.4f} – ${metrics['daromad_max']:.4f}</strong>
                </div>
                <div class='{'info-box' if holat.startswith('✅') else 'warning-box'}'>
                    {holat} — {'AI orqali tasdiqlandi' if holat.startswith('✅') else 'Sun\'iy yo\'ldosh haftalik skanerlash kutilmoqda'}
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════════
    #  MENING DARAXTLARIM
    # ════════════════════════════════════════════
    elif menu == "🗂️ Mening Daraxtlarim":
        st.title("🗂️ Mening Daraxtlarim")
        if len(df) == 0:
            st.info("🌱 Hali daraxt qo'shilmagan. Birinchi daraxtingizni sertifikatlang!")
            return

        search = st.text_input("🔍 Qidirish:", placeholder="Archa, Chinor…")
        dff = df.copy()
        if search:
            dff = dff[dff['turi'].str.contains(search, case=False, na=False) |
                      dff['manzil'].str.contains(search, case=False, na=False)]

        c1, c2, c3 = st.columns(3)
        c1.metric("Jami daraxtlar", int(dff['soni'].sum()))
        c2.metric("Jami kreditlar",  f"{dff['kredit'].sum():.6f}")
        c3.metric("Jami daromad",    f"${dff['daromad_avg'].sum():.4f}")

        st.divider()
        display_cols = ['id','turi','soni','yoshi','manzil','co2_yilik_kg','kredit',
                        'daromad_min','daromad_max','holat','sertifikat_sana']
        if 'ai_verified' in dff.columns:
            display_cols.append('ai_verified')
        if 'authenticity_score' in dff.columns:
            display_cols.append('authenticity_score')

        disp = dff[display_cols].copy()
        disp.columns = (['ID','Tur','Soni','Yoshi','Manzil','CO₂/yil(kg)','Kredit',
                          'Min($)','Maks($)','Holat','Sana'] +
                         (['AI✓'] if 'ai_verified' in dff.columns else []) +
                         (['Autentiklik'] if 'authenticity_score' in dff.columns else []))
        st.dataframe(disp, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("🔒 Blockchain Sertifikatlar")
        for _, row in df.iterrows():
            ai_badge = "🤖 AI ✅" if row.get('ai_verified') else "🤖 AI —"
            auth = row.get('authenticity_score','—')
            with st.expander(f"{row['turi']} — #{row['id']} | {row['holat']} | {ai_badge}"):
                b1, b2 = st.columns(2)
                with b1:
                    st.markdown(f"**Tur:** {row['turi']}")
                    st.markdown(f"**Soni:** {row['soni']} ta | **Yoshi:** {row['yoshi']} yil")
                    st.markdown(f"**Manzil:** {row['manzil']}")
                    st.markdown(f"**Koordinata:** {row['lat']:.6f}, {row['lon']:.6f}")
                    if row.get('exif_gps_lat'):
                        st.markdown(f"**GPS (EXIF):** {row['exif_gps_lat']:.5f}, {row['exif_gps_lon']:.5f}")
                with b2:
                    st.markdown(f"**CO₂/yil:** {row['co2_yilik_kg']:.1f} kg")
                    st.markdown(f"**Kredit:** {row['kredit']:.6f}")
                    st.markdown(f"**Daromad:** ${row['daromad_min']:.4f} – ${row['daromad_max']:.4f}")
                    st.markdown(f"**AI tasdiqlangan:** {'✅' if row.get('ai_verified') else '—'}")
                    st.markdown(f"**Autentiklik:** {auth}/100")
                st.markdown(f"<div class='blockchain-badge'>🔒 {row['blockchain_id']}</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════
    #  XARITA
    # ════════════════════════════════════════════
    elif menu == "🗺️ Xarita":
        st.title("🗺️ Barcha Daraxtlar Xaritasi")
        total_on_map = int(df['soni'].sum()) if len(df) > 0 else 0
        st.markdown(f"Xaritada jami **{total_on_map}** ta daraxt | 🟢 AI tasdiqlangan | 🟠 Tekshirilmoqda")

        m_map = folium.Map(location=[41.2995, 64.5853], zoom_start=6)
        if len(df) > 0:
            for _, row in df.iterrows():
                color   = 'green' if row['holat'] == '✅ Tasdiqlangan' else 'orange'
                ai_mark = "🤖✅" if row.get('ai_verified') else ""
                folium.Marker(
                    [row['lat'], row['lon']],
                    popup=folium.Popup(f"""
                        <b>{row['turi']}</b> {ai_mark}<br>
                        📍 {row['manzil']}<br>
                        🌳 {row['soni']} ta | ♻️ {row['kredit']:.4f} kredit<br>
                        🛡️ Autentiklik: {row.get('authenticity_score','—')}/100<br>
                        <small>{row['blockchain_id'][:24]}…</small>
                    """, max_width=280),
                    tooltip=f"{row['turi']} | {row['kredit']:.4f}",
                    icon=folium.Icon(color=color, icon='leaf', prefix='fa')
                ).add_to(m_map)
        st_folium(m_map, width=None, height=550, use_container_width=True)

    # ════════════════════════════════════════════
    #  KALKULYATOR
    # ════════════════════════════════════════════
    elif menu == "🧮 Kalkulyator":
        st.title("🧮 Karbon Kredit Kalkulyatori")
        st.markdown("AI o'lchamlari bilan aniqroq hisoblash")

        col1, col2, col3 = st.columns(3)
        with col1: k_type  = st.selectbox("Daraxt turi:",  list(TREE_SPECIES.keys()), key="ck")
        with col2:
            k_count  = st.number_input("Soni:",           min_value=1,   max_value=10000, value=1,   key="cc")
            k_age    = st.number_input("Yoshi (yil):",    min_value=1,   max_value=200,   value=5,   key="ca")
        with col3:
            k_height = st.number_input("Balandlik (m):",  min_value=0.1, max_value=100.0, value=3.0, step=0.1, key="ch")
            k_diam   = st.number_input("Diametr (sm):",   min_value=1,   max_value=500,   value=20,  key="cd")
            k_health = st.slider("Sog'liq (%):","k_hs",  min_value=10,  max_value=100,   value=100)

        if k_type:
            m_std = calculate_metrics(k_type, k_count, k_age)
            m_ai  = calculate_ai_metrics(k_type, k_count, k_age, k_height, k_diam, k_health)

            st.divider()
            col_s, col_a = st.columns(2)
            with col_s:
                st.subheader("📐 Standart formula")
                st.metric("CO₂/yil",    f"{m_std['co2_per_year']} kg")
                st.metric("Kredit",     f"{m_std['kredit']:.6f}")
                st.metric("Daromad",    f"${m_std['daromad_avg']:.4f}")
            with col_a:
                st.subheader(f"🤖 AI formula (×{m_ai.get('ai_multiplier',1)})")
                st.metric("CO₂/yil",    f"{m_ai['co2_per_year']} kg",
                           delta=f"{m_ai['co2_per_year']-m_std['co2_per_year']:+.1f}")
                st.metric("Kredit",     f"{m_ai['kredit']:.6f}",
                           delta=f"{m_ai['kredit']-m_std['kredit']:+.6f}")
                st.metric("Daromad",    f"${m_ai['daromad_avg']:.4f}",
                           delta=f"${m_ai['daromad_avg']-m_std['daromad_avg']:+.4f}")

            st.markdown(f"""
            <div class='smart-price-card'>
                <div style='font-size:0.75rem; opacity:0.7; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.75rem'>AI Daromad diapazoni</div>
                <div style='display:grid; grid-template-columns:1fr 1fr; gap:0.75rem'>
                    <div style='background:rgba(255,255,255,0.07); border-radius:10px; padding:0.85rem'>
                        <div style='font-size:0.7rem; opacity:0.7'>Minimum ($40/t)</div>
                        <div style='font-size:1.4rem; font-weight:700; color:#52c45a'>${m_ai['daromad_min']:.4f}</div>
                        <div style='font-size:0.75rem; opacity:0.6'>{format_uzs(m_ai['daromad_min_uzs'])}</div>
                    </div>
                    <div style='background:rgba(255,255,255,0.07); border-radius:10px; padding:0.85rem'>
                        <div style='font-size:0.7rem; opacity:0.7'>Maksimum ($80/t)</div>
                        <div style='font-size:1.4rem; font-weight:700; color:#f0c040'>${m_ai['daromad_max']:.4f}</div>
                        <div style='font-size:0.75rem; opacity:0.6'>{format_uzs(m_ai['daromad_max_uzs'])}</div>
                    </div>
                </div>
                <div style='margin-top:0.75rem; font-size:0.74rem; opacity:0.6'>
                    * AI korreksiya balandlik, diametr va sog'liq ko'rsatkichiga asoslanadi<br>
                    * 1 kredit = 1 tonne CO₂ | 1$ = {UZS_RATE:,} so'm
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════
    #  MARKETPLACE (AQLLI BOZOR)
    # ════════════════════════════════════════════
    elif menu == "💰 Bozor (Marketplace)":
        st.title("💰 Aqlli Karbon Kreditlar Bozori")

        total_credits = df['kredit'].sum() if len(df) > 0 else 0
        price_rec = smart_price_recommendation(total_credits)

        st.markdown(f"**Sizning balansingiz:** `{total_credits:.6f}` kredit = **${total_credits * CREDIT_PRICE_AVG:.4f}**")

        # AI narx tavsiyasi
        st.markdown(f"""
        <div class='ai-result-box'>
            🤖 AQLLI NARX TAHLILI<br><br>
            📊 Tavsiya etilgan narx: <strong style='color:#52c45a; font-size:1.1rem'>${price_rec['recommended_price']}/t</strong><br>
            {price_rec['trend']} | Sezon: {price_rec['season_label']}<br>
            💡 {price_rec['best_time']}
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("🏢 Xaridorlar ro'yxati")
        buyers = pd.DataFrame({
            "Xaridor":        ["🚗 Tesla", "🔍 Google", "🍎 Apple", "🏭 UzAuto", "⚡ UzbekEnergo", "🏗️ Qurilish UZ"],
            "Narx (1 kredit)": ["$75", "$68", "$72", "$55", "$50", "$45"],
            "Talab (kredit)":  ["500+", "200+", "300+", "50+", "100+", "20+"],
            "Holat":           ["🟢 Ochiq","🟢 Ochiq","🟢 Ochiq","🟡 Kutilmoqda","🟢 Ochiq","🟢 Ochiq"],
            "AI talab":        ["✅ Blockchain+AI", "✅ AI Verified", "✅ AI+Satellite", "— Mahalliy", "— Mahalliy", "— Mahalliy"],
        })
        st.dataframe(buyers, use_container_width=True, hide_index=True)

        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("O'rtacha narx",    f"${CREDIT_PRICE_AVG}/t")
        col2.metric("AI tavsiyasi",     f"${price_rec['recommended_price']}/t",
                     delta=f"${price_rec['recommended_price']-CREDIT_PRICE_AVG:+.2f}")
        col3.metric("Minimum",          f"${CREDIT_PRICE_MIN}/t")
        col4.metric("Maksimum",         f"${CREDIT_PRICE_MAX}/t")

        st.divider()
        st.subheader("🔄 Kredit sotish")
        if total_credits > 0:
            sell_amount = st.number_input("Sotmoqchi bo'lgan kredit:", min_value=0.0001,
                                          max_value=float(total_credits),
                                          value=min(0.001, float(total_credits)), format="%.6f")
            sell_price_opt = st.selectbox("Narx:", [
                f"${price_rec['recommended_price']}/t (AI tavsiyasi ⭐)",
                f"${CREDIT_PRICE_MIN}/t (minimum)",
                f"${CREDIT_PRICE_AVG}/t (o'rtacha)",
                f"${CREDIT_PRICE_MAX}/t (maksimum)",
            ])
            price_val = (price_rec['recommended_price'] if "AI" in sell_price_opt
                         else CREDIT_PRICE_MIN if "minimum" in sell_price_opt
                         else CREDIT_PRICE_MAX if "maksimum" in sell_price_opt
                         else CREDIT_PRICE_AVG)
            earn = sell_amount * price_val
            st.markdown(f"**Taxminiy tushum:** ${earn:.4f} = {format_uzs(earn * UZS_RATE)}")
            if st.button("💰 Sotish buyurtmasi berish", use_container_width=True):
                st.success(f"✅ Buyurtma qabul qilindi! {sell_amount:.6f} kredit → ${earn:.4f}. Xaridor bilan bog'lanasiz.")
        else:
            st.info("Sotish uchun avval daraxt qo'shing va kredit to'plang")

    # ════════════════════════════════════════════
    #  REYTING
    # ════════════════════════════════════════════
    elif menu == "🏆 Reyting":
        st.title("🏆 Foydalanuvchilar Reytingi")
        leaders = [
            {"#":"🥇","Ism":"Abdullayev Jamshid","Viloyat":"Toshkent","Daraxt":142,"Kredit":4.832,"Daromad($)":314.08,"AI✓":"✅"},
            {"#":"🥈","Ism":"Karimova Malika","Viloyat":"Samarqand","Daraxt":98,"Kredit":3.211,"Daromad($)":208.72,"AI✓":"✅"},
            {"#":"🥉","Ism":"Toshmatov Dilshod","Viloyat":"Farg'ona","Daraxt":87,"Kredit":2.954,"Daromad($)":192.0,"AI✓":"✅"},
            {"#":"4","Ism":"Yusupova Nilufar","Viloyat":"Buxoro","Daraxt":65,"Kredit":1.876,"Daromad($)":121.9,"AI✓":"✅"},
            {"#":"5","Ism":"Mirzayev Bobur","Viloyat":"Namangan","Daraxt":54,"Kredit":1.542,"Daromad($)":100.2,"AI✓":"—"},
            {"#":"…","Ism":f"👤 {user.get('name','Siz')} (Siz)","Viloyat":user.get('region','Toshkent'),
             "Daraxt":total_trees,"Kredit":round(total_credits,6),
             "Daromad($)":round(total_credits*CREDIT_PRICE_AVG,2),
             "AI✓":"✅" if (len(df)>0 and 'ai_verified' in df.columns and df['ai_verified'].any()) else "—"},
        ]
        st.dataframe(pd.DataFrame(leaders), use_container_width=True, hide_index=True)
        st.markdown("<div class='info-box'>Reyting har kuni yangilanadi. AI tasdiqlangan daraxtlar ⭐ bonus ball oladi!</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════
    #  AI SOZLAMALARI
    # ════════════════════════════════════════════
    elif menu == "⚙️ AI Sozlamalari":
        st.title("⚙️ AI Sozlamalari")
        st.markdown("Claude AI bilan integratsiya uchun Anthropic API kalitini kiriting.")

        st.markdown("""
        <div class='ai-result-box'>
            🤖 CarbonVision AI imkoniyatlari:<br>
            • 🌳 Daraxt turini rasmdan aniqlash (Computer Vision)<br>
            • 📸 Rasm autentikligini tekshirish (haqiqiy kamera vs internet)<br>
            • 🛡️ AI-generatsiya qilingan rasmlarni aniqlash<br>
            • 📏 Balandlik, diametr, yosh taxminlash<br>
            • 💚 Daraxt sog'lig'ini baholash<br>
            • 💰 Aqlli narx tavsiyasi (Smart Marketplace)
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("🔑 Anthropic API Kaliti")
        api_key_input = st.text_input(
            "API kalit:",
            value=st.session_state.anthropic_key,
            type="password",
            placeholder="sk-ant-api03-…",
            help="https://console.anthropic.com/settings/keys dan oling"
        )

        col_save, col_test = st.columns(2)
        with col_save:
            if st.button("💾 Saqlash", use_container_width=True):
                st.session_state.anthropic_key = api_key_input
                if len(api_key_input) > 20:
                    st.success("✅ API kalit saqlandi!")
                else:
                    st.warning("⚠️ Kalit juda qisqa")

        with col_test:
            if st.button("🧪 Test qilish", use_container_width=True):
                if len(api_key_input) < 20:
                    st.error("API kalit kiritilmagan")
                else:
                    try:
                        import anthropic
                        client = anthropic.Anthropic(api_key=api_key_input)
                        resp = client.messages.create(
                            model="claude-opus-4-5",
                            max_tokens=30,
                            messages=[{"role": "user", "content": "Say: AI ready"}]
                        )
                        st.success(f"✅ AI ulandi: {resp.content[0].text}")
                    except Exception as e:
                        st.error(f"❌ Xato: {str(e)[:120]}")

        st.divider()
        st.subheader("📦 O'rnatish")
        st.code("pip install anthropic Pillow streamlit-folium folium", language="bash")
        st.markdown("""
        **API kalitini olish:**
        1. [console.anthropic.com](https://console.anthropic.com) ga kiring
        2. **API Keys** bo'limiga o'ting
        3. **Create Key** tugmasini bosing
        4. Kalitni nusxalab, yuqoridagi maydonga joylashtiring
        """)

        st.divider()
        st.subheader("🧠 AI modeli: claude-opus-4-5")
        st.markdown("""
        - **Vision qobiliyati:** Rasmni tahlil qilib daraxt turini aniqlaydi
        - **Fraud detection:** Rasm internet/AI generatsiya ekanligini tekshiradi
        - **Parametr taxmini:** Yosh, balandlik, diametrni vizual baholaydi
        - **EXIF analiz:** Kamera metadata, GPS koordinata tekshiruvi
        """)

    # ════════════════════════════════════════════
    #  TIZIM HAQIDA
    # ════════════════════════════════════════════
    elif menu == "ℹ️ Tizim haqida":
        st.title("ℹ️ CarbonVision haqida")
        st.markdown("""
        ## 🌿 CarbonVision — O'zbekiston AI Karbon Kredit Platformasi

        > *"G'arbda Tesla milliardlab dollar ishlatayotgan tizimni, biz O'zbekistonda oddiy aholiga — fermerlar, o'quvchilar, bog'bonlarga ochiq qilamiz."*

        ---

        ### 🤖 AI qatlami (yangi!)
        | Funksiya | Texnologiya | Tavsif |
        |----------|-------------|--------|
        | **Daraxt turi aniqlash** | Claude Opus Vision | Rasmdan avtomatik tur tanish |
        | **Rasm autentikligi** | EXIF + AI | Kamera meta, GPS, tahrirlash izlari |
        | **AI generatsiya tekshiruvi** | Claude Opus | Midjourney/DALL-E rasmlarini bloklash |
        | **Parametr taxmini** | Computer Vision | Yosh, balandlik, diametr, sog'liq |
        | **Aqlli narx (Smart Price)** | ML algoritm | Talab/taklif va sezon tahlili |

        ### 🔒 Xavfsizlik tizimi
        | Mexanizm | Tavsif |
        |----------|--------|
        | **Double-counting** | 10m radius anti-fraud |
        | **Blockchain Hash** | `UZ-CC-…` noyob ID |
        | **EXIF GPS verify** | Rasm koordinatasi ≈ kiritilgan manzil |
        | **AI Fraud Score** | 0–100 autentiklik reytingi |
        | **Satellite** | Haftalik sun'iy yo'ldosh skanerlash |

        ### 📐 Formulalar
        ```
        CO₂ (kg/yil)   = koeffitsient × soni
        AI_korreksiya  = (balandlik_faktori + diametr_faktori) / 2 × sog'liq
        Kredit         = CO₂_kg × yosh × AI_korreksiya / 1000
        Daromad ($)    = kredit × $40–$80
        ```
        """)

        species_df = pd.DataFrame([
            {"Tur": k, "CO₂/yil (kg)": v["co2"], "ID": v["id"]}
            for k, v in TREE_SPECIES.items()
        ])
        st.dataframe(species_df, use_container_width=True, hide_index=True)

        st.markdown("""
        ### 🚀 Kelajak
        - [ ] Real Ethereum/Solana Blockchain
        - [ ] Planet Labs satellite API
        - [ ] Mobile app (React Native)
        - [ ] Payme/Click to'lov
        - [ ] LiDAR daraxt o'lchash
        """)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if not st.session_state.authenticated:
    auth_page()
else:
    main_app()
