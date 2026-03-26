import streamlit as st
import pandas as pd
import hashlib
import folium
from streamlit_folium import st_folium
from datetime import datetime
import random

# --- SAHIFA SOZLAMALARI ---
st.set_page_config(
    page_title="CarbonVision | O'zbekiston Karbon Kredit Platformasi",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main { background-color: #f8fdf8; }
    .stMetric { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e0f0e0; box-shadow: 0 2px 8px rgba(0,80,0,0.07); }
    .stMetric label { color: #4a7c4a !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
    .stMetric [data-testid="stMetricValue"] { color: #1a4a1a !important; font-size: 1.8rem !important; font-weight: 700 !important; }
    .blockchain-badge { background: linear-gradient(135deg, #0a1f0a, #1a4a1a); color: #52c45a; padding: 0.4rem 0.8rem; border-radius: 8px; font-family: monospace; font-size: 0.78rem; word-break: break-all; }
    .credit-badge { background: #f0fdf0; border: 1.5px solid #38a83d; border-radius: 8px; padding: 0.5rem 1rem; color: #15803d; font-weight: 700; }
    .warning-box { background: #fef3c7; border-left: 4px solid #d97706; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }
    .info-box { background: #f0fdf4; border-left: 4px solid #38a83d; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }
    .satellite-box { background: linear-gradient(135deg, #0a1f0a, #0f2d0f); color: #52c45a; border-radius: 12px; padding: 1rem 1.25rem; font-family: monospace; font-size: 0.85rem; }
    div[data-testid="stSidebarContent"] { background: linear-gradient(180deg, #0a1f0a 0%, #0f2d0f 100%); }
    div[data-testid="stSidebarContent"] * { color: #c8f0ca !important; }
    div[data-testid="stSidebarContent"] .stRadio label { color: #c8f0ca !important; }
    .stButton button { background: linear-gradient(135deg, #25752d, #38a83d); color: white; border: none; border-radius: 10px; font-weight: 600; padding: 0.6rem 1.5rem; }
    .stButton button:hover { background: linear-gradient(135deg, #1e5c1e, #25752d); transform: translateY(-1px); }
    h1 { color: #0f2d0f !important; }
    h2, h3 { color: #1a4a1a !important; }
</style>
""", unsafe_allow_html=True)

# --- DARAXT TURLARI ---
TREE_SPECIES = {
    "🌲 Archa (Juniper)": {"co2": 22, "id": "archa"},
    "🌳 Terak (Poplar)": {"co2": 48, "id": "terak"},
    "🌿 To'l (Willow)": {"co2": 35, "id": "tol"},
    "🌳 Chinor (Plane Tree)": {"co2": 56, "id": "chinor"},
    "🌰 Yong'oq (Walnut)": {"co2": 40, "id": "yongoq"},
    "🍎 Olma (Apple)": {"co2": 20, "id": "olma"},
    "🍑 Shaftoli (Peach)": {"co2": 18, "id": "shaftoli"},
    "🌲 Shumto'l (Elm)": {"co2": 30, "id": "shumtol"},
    "🌿 Qayin (Birch)": {"co2": 25, "id": "qayin"},
    "🌳 Eman (Oak)": {"co2": 48, "id": "eman"},
    "🍁 Zarang (Maple)": {"co2": 32, "id": "zarang"},
    "🌿 Pista (Pistachio)": {"co2": 15, "id": "pista"},
    "🌳 Mevali (Fruit mix)": {"co2": 18, "id": "mevali"},
}

CREDIT_PRICE_MIN = 40
CREDIT_PRICE_MAX = 80
CREDIT_PRICE_AVG = 65
UZS_RATE = 12700

# --- FUNKSIYALAR ---
def calculate_metrics(t_type, count, age):
    co2_per_year = TREE_SPECIES.get(t_type, {}).get("co2", 20)
    co2_total_kg = co2_per_year * count * age
    kredit = co2_total_kg / 1000
    daromad_min = kredit * CREDIT_PRICE_MIN
    daromad_max = kredit * CREDIT_PRICE_MAX
    daromad_avg = kredit * CREDIT_PRICE_AVG
    return {
        "co2_per_year": co2_per_year * count,
        "co2_total_kg": co2_total_kg,
        "kredit": kredit,
        "daromad_min": daromad_min,
        "daromad_max": daromad_max,
        "daromad_avg": daromad_avg,
        "daromad_min_uzs": int(daromad_min * UZS_RATE),
        "daromad_max_uzs": int(daromad_max * UZS_RATE),
    }

def generate_blockchain_hash(lat, lon, t_type, timestamp):
    raw = f"{lat}{lon}{t_type}{timestamp}{random.random()}"
    return "UZ-CC-" + hashlib.sha256(raw.encode()).hexdigest()[:24].upper()

def check_duplicate_location(lat, lon, existing_df, threshold_m=10):
    for _, row in existing_df.iterrows():
        dist = ((row['lat'] - lat) ** 2 + (row['lon'] - lon) ** 2) ** 0.5 * 111000
        if dist < threshold_m:
            return True, row['id']
    return False, None

def format_uzs(amount):
    return f"{int(amount):,} so'm".replace(",", " ")

# --- SESSION STATE INIT ---
if 'tree_db' not in st.session_state:
    st.session_state.tree_db = pd.DataFrame(columns=[
        "id", "blockchain_id", "turi", "soni", "yoshi", "balandlik_m",
        "lat", "lon", "manzil", "co2_yilik_kg", "kredit",
        "daromad_min", "daromad_max", "daromad_avg",
        "holat", "sertifikat_sana"
    ])

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'users_db' not in st.session_state:
    st.session_state.users_db = {}

# ==================== AUTH ====================
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 2rem 0'>
            <div style='font-size:4rem'>🌿</div>
            <h1 style='color:#0f2d0f !important; font-size:2.5rem; margin:0'>CarbonVision</h1>
            <p style='color:#4a7c4a; font-size:1rem; margin-top:0.5rem'>
                O'zbekiston Karbon Kredit Platformasi
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])

        with tab1:
            st.subheader("Hisobingizga kiring")
            email = st.text_input("Email", placeholder="email@example.com", key="login_email")
            password = st.text_input("Parol", type="password", placeholder="••••••••", key="login_pass")

            if st.button("Kirish →", use_container_width=True, key="login_btn"):
                if email in st.session_state.users_db:
                    stored = st.session_state.users_db[email]
                    if stored["password"] == hashlib.md5(password.encode()).hexdigest():
                        st.session_state.authenticated = True
                        st.session_state.current_user = stored
                        st.success(f"✅ Xush kelibsiz, {stored['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Parol noto'g'ri")
                else:
                    st.error("❌ Foydalanuvchi topilmadi")

            st.divider()
            st.markdown("**Demo kirish** (test uchun):")
            if st.button("🚀 Demo sifatida kirish", use_container_width=True):
                demo_user = {"name": "Demo Foydalanuvchi", "email": "demo@carbonvision.uz", "region": "Toshkent"}
                st.session_state.authenticated = True
                st.session_state.current_user = demo_user
                if len(st.session_state.tree_db) == 0:
                    demo_trees = [
                        {
                            "id": "A1B2C3", "blockchain_id": "UZ-CC-A1B2C3D4E5F6G7H8I9J0K1L2",
                            "turi": "🌳 Chinor (Plane Tree)", "soni": 2, "yoshi": 10,
                            "balandlik_m": 8.0, "lat": 41.3111, "lon": 69.2405,
                            "manzil": "Chilonzor tumani, bog'", "co2_yilik_kg": 112,
                            "kredit": 1.12, "daromad_min": 44.8, "daromad_max": 89.6,
                            "daromad_avg": 72.8, "holat": "✅ Tasdiqlangan",
                            "sertifikat_sana": "2024-01-15"
                        },
                        {
                            "id": "D4E5F6", "blockchain_id": "UZ-CC-D4E5F6G7H8I9J0K1L2M3N4",
                            "turi": "🌲 Archa (Juniper)", "soni": 3, "yoshi": 5,
                            "balandlik_m": 3.5, "lat": 41.3200, "lon": 69.2500,
                            "manzil": "Yunusobod, hovli", "co2_yilik_kg": 66,
                            "kredit": 0.33, "daromad_min": 13.2, "daromad_max": 26.4,
                            "daromad_avg": 21.45, "holat": "✅ Tasdiqlangan",
                            "sertifikat_sana": "2024-03-20"
                        }
                    ]
                    st.session_state.tree_db = pd.DataFrame(demo_trees)
                st.rerun()

        with tab2:
            st.subheader("Yangi hisob yaratish")
            reg_name = st.text_input("To'liq ism", placeholder="Ism Familiya", key="reg_name")
            reg_email = st.text_input("Email", placeholder="email@example.com", key="reg_email")
            reg_phone = st.text_input("Telefon", placeholder="+998901234567", key="reg_phone")
            reg_region = st.selectbox("Viloyat", [
                "Toshkent", "Samarqand", "Buxoro", "Namangan", "Andijon",
                "Farg'ona", "Qashqadaryo", "Surxondaryo", "Xorazm",
                "Sirdaryo", "Jizzax", "Navoiy", "Qoraqalpog'iston"
            ], key="reg_region")
            reg_pass = st.text_input("Parol", type="password", placeholder="Kamida 6 belgi", key="reg_pass")
            reg_pass2 = st.text_input("Parolni takrorlang", type="password", key="reg_pass2")

            if st.button("Ro'yxatdan o'tish →", use_container_width=True, key="reg_btn"):
                if not reg_name or not reg_email or not reg_pass:
                    st.error("❌ Barcha maydonlarni to'ldiring")
                elif reg_pass != reg_pass2:
                    st.error("❌ Parollar mos kelmaydi")
                elif len(reg_pass) < 6:
                    st.error("❌ Parol kamida 6 belgidan iborat bo'lishi kerak")
                elif reg_email in st.session_state.users_db:
                    st.error("❌ Bu email allaqachon ro'yxatdan o'tgan")
                else:
                    user = {
                        "name": reg_name, "email": reg_email,
                        "phone": reg_phone, "region": reg_region,
                        "password": hashlib.md5(reg_pass.encode()).hexdigest(),
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.users_db[reg_email] = user
                    st.session_state.authenticated = True
                    st.session_state.current_user = user
                    st.success(f"🎉 Xush kelibsiz, {reg_name}!")
                    st.rerun()

# ==================== MAIN APP ====================
def main_app():
    user = st.session_state.current_user

    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; padding:1rem 0'>
            <div style='font-size:2.5rem'>🌿</div>
            <div style='font-size:1.2rem; font-weight:700; color:#c8f0ca'>CarbonVision</div>
            <div style='font-size:0.8rem; color:#8eca90; margin-top:0.25rem'>O'zbekiston</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**👤 {user.get('name', 'Foydalanuvchi')}**")
        st.markdown(f"📍 {user.get('region', 'Toshkent')}")
        st.divider()

        menu = st.radio("Bo'limlar:", [
            "📊 Dashboard",
            "🌳 Daraxt Sertifikatlash",
            "🗂️ Mening Daraxtlarim",
            "🗺️ Xarita",
            "🧮 Kalkulyator",
            "💰 Bozor (Marketplace)",
            "🏆 Reyting",
            "ℹ️ Tizim haqida"
        ])

        st.divider()

        total_trees = st.session_state.tree_db['soni'].sum() if len(st.session_state.tree_db) > 0 else 0
        total_credits = st.session_state.tree_db['kredit'].sum() if len(st.session_state.tree_db) > 0 else 0
        st.markdown(f"🌳 **{int(total_trees)}** ta daraxt")
        st.markdown(f"♻️ **{total_credits:.4f}** kredit")
        st.markdown(f"💰 **${total_credits * CREDIT_PRICE_AVG:.2f}** potensial")

        st.divider()
        if st.button("🚪 Chiqish", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()

    # ==================== DASHBOARD ====================
    if menu == "📊 Dashboard":
        st.title("📊 Boshqaruv Paneli")
        st.markdown(f"Salom, **{user.get('name', '')}** 👋 — Real vaqt rejimida karbon kredit hisobingiz")

        df = st.session_state.tree_db

        total_trees = int(df['soni'].sum()) if len(df) > 0 else 0
        total_credits = df['kredit'].sum() if len(df) > 0 else 0
        total_co2 = df['co2_yilik_kg'].sum() if len(df) > 0 else 0
        total_earn_min = df['daromad_min'].sum() if len(df) > 0 else 0
        total_earn_max = df['daromad_max'].sum() if len(df) > 0 else 0
        total_earn_avg = df['daromad_avg'].sum() if len(df) > 0 else 0
        verified = len(df[df['holat'] == '✅ Tasdiqlangan']) if len(df) > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌳 Jami Daraxtlar", f"{total_trees} ta", f"+{total_trees} ro'yxatda")
        col2.metric("♻️ Karbon Kreditlar", f"{total_credits:.4f}", "tonne CO₂ ekvivalent")
        col3.metric("💨 Yillik CO₂ yutish", f"{total_co2} kg", f"{total_co2/1000:.3f} tonne")
        col4.metric("💰 Potensial daromad", f"${total_earn_avg:.2f}", f"${total_earn_min:.2f}–${total_earn_max:.2f}")

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
            st.markdown(f"""
            <div style='display:grid; gap:0.75rem'>
                <div style='background:#f0fdf4; border-radius:10px; padding:0.75rem 1rem; display:flex; justify-content:space-between'>
                    <span style='color:#4a7c4a'>✅ Tasdiqlangan</span>
                    <strong style='color:#15803d'>{verified} ta</strong>
                </div>
                <div style='background:#fef3c7; border-radius:10px; padding:0.75rem 1rem; display:flex; justify-content:space-between'>
                    <span style='color:#92400e'>⏳ Kutilmoqda</span>
                    <strong style='color:#b45309'>{len(df) - verified} ta</strong>
                </div>
                <div style='background:#f0fdf4; border-radius:10px; padding:0.75rem 1rem; display:flex; justify-content:space-between'>
                    <span style='color:#4a7c4a'>💰 Min daromad</span>
                    <strong style='color:#15803d'>${total_earn_min:.2f} ({format_uzs(total_earn_min * UZS_RATE)})</strong>
                </div>
                <div style='background:#fefce8; border-radius:10px; padding:0.75rem 1rem; display:flex; justify-content:space-between'>
                    <span style='color:#854d0e'>🏆 Maks daromad</span>
                    <strong style='color:#a16207'>${total_earn_max:.2f} ({format_uzs(total_earn_max * UZS_RATE)})</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.subheader("📍 Daraxtlar xaritada")
        if len(df) > 0:
            m = folium.Map(location=[41.3111, 69.2405], zoom_start=11)
            for _, row in df.iterrows():
                color = 'green' if row['holat'] == '✅ Tasdiqlangan' else 'orange'
                folium.Marker(
                    [row['lat'], row['lon']],
                    popup=folium.Popup(f"""
                        <b>{row['turi']}</b><br>
                        Soni: {row['soni']} ta<br>
                        Kredit: {row['kredit']:.4f}<br>
                        Manzil: {row['manzil']}<br>
                        <small>{row['blockchain_id']}</small>
                    """, max_width=250),
                    tooltip=f"{row['turi']} — {row['kredit']:.4f} kredit",
                    icon=folium.Icon(color=color, icon='leaf', prefix='fa')
                ).add_to(m)
            st_folium(m, width=None, height=400, use_container_width=True)
        else:
            st.info("Xaritada ko'rsatish uchun daraxt qo'shing")

        st.markdown("""
        <div class='satellite-box'>
            🛰️ SUN'IY YO'LDOSH NAZORAT TIZIMI: Faol | Haftalik skanerlash: Yoqilgan<br>
            🔒 BLOCKCHAIN: Barcha kreditlar immutable ledger'da saqlanmoqda<br>
            ♻️ DOUBLE-COUNTING HIMOYA: 10m radius anti-fraud tizimi: Faol
        </div>
        """, unsafe_allow_html=True)

    # ==================== SERTIFIKATLASH ====================
    elif menu == "🌳 Daraxt Sertifikatlash":
        st.title("🌳 Yangi Daraxtni Sertifikatlash")
        st.markdown("Daraxtingizni ro'yxatga oling, blockchain sertifikat va karbon kredit oling")

        with st.form("tree_form"):
            st.subheader("1️⃣ Daraxt ma'lumotlari")
            col1, col2, col3 = st.columns(3)
            with col1:
                t_type = st.selectbox("Daraxt turi:", list(TREE_SPECIES.keys()))
                co2_info = TREE_SPECIES[t_type]["co2"]
                st.caption(f"ℹ️ Bu tur yiliga **{co2_info} kg** CO₂ yutadi")
            with col2:
                t_count = st.number_input("Daraxt soni:", min_value=1, max_value=1000, value=1)
            with col3:
                t_age = st.number_input("Yoshi (yil):", min_value=1, max_value=200, value=5)

            st.subheader("2️⃣ O'lchamlar")
            col3, col4 = st.columns(2)
            with col3:
                t_height = st.number_input("Balandligi (metrda):", min_value=0.1, max_value=100.0, value=2.0, step=0.1)
            with col4:
                t_diameter = st.number_input("Trunk diametri (sm):", min_value=1, max_value=500, value=20)

            st.subheader("3️⃣ Joylashuv")
            loc_method = st.radio("Joylashuv usuli:", ["✏️ Qo'lda kiritish", "🗺️ Koordinata"], horizontal=True)

            col5, col6 = st.columns(2)
            with col5:
                lat = st.number_input("Kenglik (Latitude):", value=41.2995, format="%.6f", min_value=37.0, max_value=46.0)
            with col6:
                lon = st.number_input("Uzunlik (Longitude):", value=69.2401, format="%.6f", min_value=55.0, max_value=75.0)

            location_name = st.text_input("Manzil nomi:", placeholder="masalan: Chilonzor-12, hovlim")

            st.subheader("4️⃣ Rasm va tavsif")
            col7, col8 = st.columns(2)
            with col7:
                photo = st.file_uploader("Daraxt rasmi (ixtiyoriy):", type=['jpg', 'png', 'jpeg'])
            with col8:
                description = st.text_area("Qo'shimcha ma'lumot:", placeholder="Daraxt haqida...")

            metrics = calculate_metrics(t_type, t_count, t_age)
            st.divider()
            st.subheader("📊 Taxminiy hisob-kitob")
            pc1, pc2, pc3 = st.columns(3)
            pc1.metric("CO₂ yutish (yiliga)", f"{metrics['co2_per_year']} kg")
            pc2.metric("Kredit miqdori", f"{metrics['kredit']:.6f}")
            pc3.metric("Potensial daromad", f"${metrics['daromad_avg']:.4f}", f"{format_uzs(metrics['daromad_avg'] * UZS_RATE)}")

            submitted = st.form_submit_button("🚀 Sertifikatlash va Kredit olish", use_container_width=True)

            if submitted:
                if len(st.session_state.tree_db) > 0:
                    is_dup, dup_id = check_duplicate_location(lat, lon, st.session_state.tree_db)
                    if is_dup:
                        st.error(f"⚠️ ANTI-FRAUD: Bu joylashuvga 10m ichida daraxt allaqachon ro'yxatdan o'tgan! (ID: #{dup_id}). Double-counting tizimi ishlamoqda.")
                        st.stop()

                timestamp = datetime.now()
                blockchain_id = generate_blockchain_hash(lat, lon, t_type, timestamp)
                short_id = hashlib.sha256(f"{lat}{lon}{timestamp}".encode()).hexdigest()[:6].upper()

                new_data = {
                    "id": short_id,
                    "blockchain_id": blockchain_id,
                    "turi": t_type,
                    "soni": t_count,
                    "yoshi": t_age,
                    "balandlik_m": t_height,
                    "lat": lat,
                    "lon": lon,
                    "manzil": location_name or "Ko'rsatilmagan",
                    "co2_yilik_kg": metrics["co2_per_year"],
                    "kredit": metrics["kredit"],
                    "daromad_min": metrics["daromad_min"],
                    "daromad_max": metrics["daromad_max"],
                    "daromad_avg": metrics["daromad_avg"],
                    "holat": "⏳ Tekshirilmoqda",
                    "sertifikat_sana": timestamp.strftime("%Y-%m-%d"),
                }

                st.session_state.tree_db = pd.concat(
                    [st.session_state.tree_db, pd.DataFrame([new_data])],
                    ignore_index=True
                )

                st.balloons()
                st.success(f"✅ Daraxt muvaffaqiyatli sertifikatlandi! ID: #{short_id}")

                st.markdown(f"""
                <div class='info-box'>
                    <strong>🔒 Blockchain sertifikat:</strong><br>
                    <span class='blockchain-badge'>{blockchain_id}</span>
                </div>
                <div class='info-box'>
                    📊 <strong>{t_count} ta {t_type}</strong> — yiliga <strong>{metrics['co2_per_year']} kg</strong> CO₂ yutadi<br>
                    ♻️ Kredit: <strong>{metrics['kredit']:.6f}</strong> (1 kredit = 1 tonne CO₂)<br>
                    💰 Potensial daromad: <strong>${metrics['daromad_min']:.4f} – ${metrics['daromad_max']:.4f}</strong> / yil<br>
                    💵 O'zbek so'mida: <strong>{format_uzs(metrics['daromad_min_uzs'])} – {format_uzs(metrics['daromad_max_uzs'])}</strong>
                </div>
                <div class='warning-box'>
                    ⏳ Holat: <strong>Tekshirilmoqda</strong> — Sun'iy yo'ldosh haftalik skanerlash kutilmoqda
                </div>
                """, unsafe_allow_html=True)

    # ==================== MENING DARAXTLARIM ====================
    elif menu == "🗂️ Mening Daraxtlarim":
        st.title("🗂️ Mening Daraxtlarim")

        df = st.session_state.tree_db

        if len(df) == 0:
            st.info("🌱 Hali daraxt qo'shilmagan. Birinchi daraxtingizni sertifikatlang!")
        else:
            search = st.text_input("🔍 Qidirish (tur nomi yoki manzil):", placeholder="Archa, Chinor, Toshkent...")
            if search:
                df = df[df['turi'].str.contains(search, case=False, na=False) |
                        df['manzil'].str.contains(search, case=False, na=False)]

            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Jami daraxtlar", int(df['soni'].sum()))
            col_s2.metric("Jami kreditlar", f"{df['kredit'].sum():.6f}")
            col_s3.metric("Jami daromad (avg)", f"${df['daromad_avg'].sum():.4f}")

            st.divider()

            display_df = df[[
                'id', 'turi', 'soni', 'yoshi', 'balandlik_m',
                'manzil', 'co2_yilik_kg', 'kredit',
                'daromad_min', 'daromad_max', 'holat', 'sertifikat_sana'
            ]].copy()

            display_df.columns = [
                'ID', 'Tur', 'Soni', 'Yoshi', 'Balandlik (m)',
                'Manzil', 'CO₂/yil (kg)', 'Kredit',
                'Min daromad ($)', 'Maks daromad ($)', 'Holat', 'Sana'
            ]

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("🔒 Blockchain Sertifikatlar")
            for _, row in st.session_state.tree_db.iterrows():
                with st.expander(f"{row['turi']} — #{row['id']} | {row['holat']}"):
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        st.markdown(f"**Tur:** {row['turi']}")
                        st.markdown(f"**Soni:** {row['soni']} ta")
                        st.markdown(f"**Manzil:** {row['manzil']}")
                        st.markdown(f"**Koordinata:** {row['lat']:.6f}, {row['lon']:.6f}")
                    with col_b2:
                        st.markdown(f"**CO₂/yil:** {row['co2_yilik_kg']} kg")
                        st.markdown(f"**Kredit:** {row['kredit']:.6f}")
                        st.markdown(f"**Daromad:** ${row['daromad_min']:.4f} – ${row['daromad_max']:.4f}")
                        st.markdown(f"**Sana:** {row['sertifikat_sana']}")
                    st.markdown(f"""
                    <div class='blockchain-badge'>
                        🔒 {row['blockchain_id']}
                    </div>
                    """, unsafe_allow_html=True)

    # ==================== XARITA ====================
    elif menu == "🗺️ Xarita":
        st.title("🗺️ Barcha Daraxtlar Xaritasi")

        df = st.session_state.tree_db
        total_on_map = int(df['soni'].sum()) if len(df) > 0 else 0
        st.markdown(f"Xaritada jami **{total_on_map}** ta daraxt ko'rsatilmoqda")

        m = folium.Map(location=[41.2995, 64.5853], zoom_start=6)

        if len(df) > 0:
            for _, row in df.iterrows():
                color = 'green' if row['holat'] == '✅ Tasdiqlangan' else 'orange'
                folium.Marker(
                    [row['lat'], row['lon']],
                    popup=folium.Popup(f"""
                        <b style='font-size:1rem'>{row['turi']}</b><br>
                        <hr style='margin:0.25rem 0'>
                        📍 {row['manzil']}<br>
                        🌳 Soni: {row['soni']} ta<br>
                        ♻️ Kredit: {row['kredit']:.4f}<br>
                        💰 Daromad: ${row['daromad_avg']:.4f}<br>
                        <small style='color:#666'>{row['blockchain_id'][:20]}...</small>
                    """, max_width=280),
                    tooltip=f"{row['turi']} | {row['kredit']:.4f} kredit",
                    icon=folium.Icon(color=color, icon='leaf', prefix='fa')
                ).add_to(m)

        st_folium(m, width=None, height=550, use_container_width=True)

        st.markdown("""
        **Rang belgisi:**
        - 🟢 Yashil — Tasdiqlangan (sun'iy yo'ldosh orqali)
        - 🟠 To'q sariq — Tekshirilmoqda
        """)

    # ==================== KALKULYATOR ====================
    elif menu == "🧮 Kalkulyator":
        st.title("🧮 Karbon Kredit Kalkulyatori")
        st.markdown("Daraxtingiz qancha kredit va daromad keltirishi mumkinligini hisoblang")

        col1, col2, col3 = st.columns(3)
        with col1:
            k_type = st.selectbox("Daraxt turi:", list(TREE_SPECIES.keys()), key="calc_type")
        with col2:
            k_count = st.number_input("Soni:", min_value=1, max_value=10000, value=1, key="calc_count")
        with col3:
            k_age = st.number_input("Yoshi (yil):", min_value=1, max_value=200, value=5, key="calc_age")

        if k_type:
            m = calculate_metrics(k_type, k_count, k_age)

            st.divider()
            st.subheader(f"📊 Natija: {k_count} ta {k_type} — {k_age} yillik")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("CO₂/yil", f"{m['co2_per_year']} kg")
            c2.metric("Jami CO₂", f"{m['co2_total_kg']} kg")
            c3.metric("Kredit", f"{m['kredit']:.6f}")
            c4.metric("Daromad (avg)", f"${m['daromad_avg']:.4f}")

            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0a1f0a,#0f2d0f); border-radius:16px; padding:1.5rem; color:white; margin-top:1rem'>
                <div style='font-size:0.8rem; opacity:0.7; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1rem'>Daromad diapazoni</div>
                <div style='display:grid; grid-template-columns:1fr 1fr; gap:1rem'>
                    <div style='background:rgba(255,255,255,0.07); border-radius:10px; padding:1rem'>
                        <div style='font-size:0.75rem; opacity:0.7'>Minimum ($40/t)</div>
                        <div style='font-size:1.5rem; font-weight:700; color:#52c45a'>${m['daromad_min']:.4f}</div>
                        <div style='font-size:0.8rem; opacity:0.6'>{format_uzs(m['daromad_min_uzs'])}</div>
                    </div>
                    <div style='background:rgba(255,255,255,0.07); border-radius:10px; padding:1rem'>
                        <div style='font-size:0.75rem; opacity:0.7'>Maksimum ($80/t)</div>
                        <div style='font-size:1.5rem; font-weight:700; color:#f0c040'>${m['daromad_max']:.4f}</div>
                        <div style='font-size:0.8rem; opacity:0.6'>{format_uzs(m['daromad_max_uzs'])}</div>
                    </div>
                </div>
                <div style='margin-top:1rem; font-size:0.78rem; opacity:0.6; line-height:1.6'>
                    * 1 kredit = 1 tonne CO₂ | Bozor narxi: $40–$80 | 1$ = {UZS_RATE:,} so'm
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.divider()
            st.markdown("""
            **Formula:**
            ```
            CO₂ (kg) = ko'effitsient × soni × yoshi
            Kredit    = CO₂_kg / 1000
            Daromad   = kredit × $40–$80
            ```
            """)

    # ==================== MARKETPLACE ====================
    elif menu == "💰 Bozor (Marketplace)":
        st.title("💰 Karbon Kreditlar Bozori")

        df = st.session_state.tree_db
        total_credits = df['kredit'].sum() if len(df) > 0 else 0

        st.markdown(f"**Sizning balansingiz:** `{total_credits:.6f}` kredit = **${total_credits * CREDIT_PRICE_AVG:.4f}**")

        st.divider()
        st.subheader("🏢 Xaridorlar ro'yxati")

        buyers = pd.DataFrame({
            "Xaridor": ["🚗 Tesla", "🔍 Google", "🍎 Apple", "🏭 UzAuto", "⚡ UzbekEnergo", "🏗️ Qurilish UZ"],
            "Narx (1 kredit)": ["$75", "$68", "$72", "$55", "$50", "$45"],
            "Talab (kredit)": ["500+", "200+", "300+", "50+", "100+", "20+"],
            "Holat": ["🟢 Ochiq", "🟢 Ochiq", "🟢 Ochiq", "🟡 Kutilmoqda", "🟢 Ochiq", "🟢 Ochiq"],
            "Sertifikat talabi": ["ISO + Blockchain", "Blockchain", "ISO + Satellite", "Mahalliy", "Mahalliy", "Mahalliy"]
        })
        st.dataframe(buyers, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("📈 Bozor narxlari (joriy)")
        col1, col2, col3 = st.columns(3)
        col1.metric("O'rtacha narx", f"${CREDIT_PRICE_AVG}/t", "+5%")
        col2.metric("Minimum", f"${CREDIT_PRICE_MIN}/t")
        col3.metric("Maksimum", f"${CREDIT_PRICE_MAX}/t")

        st.divider()
        st.subheader("🔄 Kredit sotish")
        if total_credits > 0:
            sell_amount = st.number_input("Sotmoqchi bo'lgan kredit miqdori:", min_value=0.0001, max_value=float(total_credits), value=min(0.001, float(total_credits)), format="%.6f")
            sell_price = st.selectbox("Narx:", [f"${CREDIT_PRICE_MIN}/t (min)", f"${CREDIT_PRICE_AVG}/t (o'rtacha)", f"${CREDIT_PRICE_MAX}/t (maks)"])
            price_val = CREDIT_PRICE_MIN if "min" in sell_price else (CREDIT_PRICE_MAX if "maks" in sell_price else CREDIT_PRICE_AVG)
            earn = sell_amount * price_val
            st.markdown(f"**Taxminiy tushum:** ${earn:.4f} = {format_uzs(earn * UZS_RATE)}")
            if st.button("💰 Sotish buyurtmasi berish", use_container_width=True):
                st.success(f"✅ Buyurtma qabul qilindi! {sell_amount:.6f} kredit → ${earn:.4f}. Xaridor bilan bog'lanasiz.")
        else:
            st.info("Sotish uchun avval daraxt qo'shing va kredit to'plang")

    # ==================== REYTING ====================
    elif menu == "🏆 Reyting":
        st.title("🏆 Foydalanuvchilar Reytingi")
        st.markdown("O'zbekistondagi eng faol karbon kredit ishtirokchilari")

        df = st.session_state.tree_db
        total_credits = df['kredit'].sum() if len(df) > 0 else 0

        leaders = [
            {"#": "🥇", "Ism": "Abdullayev Jamshid", "Viloyat": "Toshkent", "Daraxt": 142, "Kredit": 4.832, "Daromad ($)": 314.08},
            {"#": "🥈", "Ism": "Karimova Malika", "Viloyat": "Samarqand", "Daraxt": 98, "Kredit": 3.211, "Daromad ($)": 208.72},
            {"#": "🥉", "Ism": "Toshmatov Dilshod", "Viloyat": "Farg'ona", "Daraxt": 87, "Kredit": 2.954, "Daromad ($)": 192.0},
            {"#": "4", "Ism": "Yusupova Nilufar", "Viloyat": "Buxoro", "Daraxt": 65, "Kredit": 1.876, "Daromad ($)": 121.9},
            {"#": "5", "Ism": "Mirzayev Bobur", "Viloyat": "Namangan", "Daraxt": 54, "Kredit": 1.542, "Daromad ($)": 100.2},
            {"#": "...", "Ism": f"👤 {user.get('name', 'Siz')} (Siz)", "Viloyat": user.get('region', 'Toshkent'), "Daraxt": int(df['soni'].sum()) if len(df) > 0 else 0, "Kredit": round(total_credits, 6), "Daromad ($)": round(total_credits * CREDIT_PRICE_AVG, 2)},
        ]

        lb_df = pd.DataFrame(leaders)
        st.dataframe(lb_df, use_container_width=True, hide_index=True)

        st.markdown("""
        <div class='info-box'>
        Reyting har kuni yangilanadi. Ko'proq daraxt qo'shing — yuqoriga ko'tariling! 🌳
        </div>
        """, unsafe_allow_html=True)

    # ==================== TIZIM HAQIDA ====================
    elif menu == "ℹ️ Tizim haqida":
        st.title("ℹ️ CarbonVision haqida")

        st.markdown("""
        ## 🌿 CarbonVision — O'zbekiston Karbon Kredit Platformasi

        > *"G'arbda Tesla milliardlab dollar ishlatayotgan tizimni, biz O'zbekistonda oddiy aholiga — fermerlar, o'quvchilar, bog'bonlarga ochiq qilamiz."*

        ---

        ### 📐 Formula
        ```
        CO₂ (kg/yil)   = daraxt_turi_koeffitsienti × soni
        Karbon Kredit  = CO₂_kg × yosh / 1000
        Daromad ($)    = kredit × $40–$80
        Daromad (so'm) = daromad_usd × 12,700
        ```

        ### 🔒 Xavfsizlik tizimi
        | Mexanizm | Tavsif |
        |----------|--------|
        | **Double-counting** | 10m radius anti-fraud tekshiruv |
        | **Blockchain Hash** | Har kredit uchun `UZ-CC-...` noyob ID |
        | **Satellite verify** | Sun'iy yo'ldosh haftalik skanerlash |
        | **JWT Auth** | Xavfsiz autentifikatsiya |

        ### 🌳 Daraxt turlari va CO₂ koeffitsientlari
        """)

        species_df = pd.DataFrame([
            {"Tur": k, "CO₂/yil (kg)": v["co2"], "1 dona, 1 yil kreditda": f"{v['co2']/1000:.6f}"}
            for k, v in TREE_SPECIES.items()
        ])
        st.dataframe(species_df, use_container_width=True, hide_index=True)

        st.markdown("""
        ### 🚀 Kelajakdagi rivojlantirish
        - [ ] Haqiqiy Google OAuth (Firebase)
        - [ ] Planet Labs / Sentinel satellite API
        - [ ] Real Ethereum Blockchain
        - [ ] Mobile app (React Native)
        - [ ] Payme / Click to'lov tizimi
        - [ ] SMS bildirishnomalar (Eskiz.uz)
        """)


# ==================== ENTRY POINT ====================
# Bu qator MUHIM — ilovani ishga tushiradi
if not st.session_state.authenticated:
    auth_page()
else:
    main_app()
