import streamlit as st
import pandas as pd
import hashlib
import folium
from streamlit_folium import st_folium
from datetime import datetime

# --- SAHIFA SOZLAMALARI ---
st.set_page_config(page_title="EcoCarbon Pro | Unified Dashboard", page_icon="🌳", layout="wide")

# --- MA'LUMOTLARNI SAQLASH (DATABASE SIMULATSIYASI) ---
if 'tree_db' not in st.session_state:
    # Boshlang'ich namunaviy ma'lumotlar
    st.session_state.tree_db = pd.DataFrame([
        {"id": "A1B2C3", "turi": "Chinor", "yoshi": 10, "lat": 41.3111, "lon": 69.2405, "kredit": 0.45, "daromad": 29.25},
        {"id": "D4E5F6", "turi": "Archa", "yoshi": 5, "lat": 41.3200, "lon": 69.2500, "kredit": 0.11, "daromad": 7.15}
    ])

# --- FUNKSIYALAR ---
def calculate_metrics(t_type, age):
    ratios = {"Archa": 22, "Chinor": 45, "Mevali": 15, "Terak": 30}
    kg = ratios.get(t_type, 10) * age
    kredit = kg / 1000
    daromad = kredit * 65  # 1 kredit = $65
    return kredit, daromad

# --- SIDEBAR NAVIGATSIYA ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2913/2913520.png", width=80)
    st.title("EcoCarbon AI")
    menu = st.radio("Bo'limlar:", ["Boshqaruv Paneli", "Yangi Daraxt Sertifikatlash", "Bozor (Marketplace)"])
    st.info(f"Jami daraxtlar: {len(st.session_state.tree_db)}")

# --- 1-BO'LIM: BOSHQARUV PANELI ---
if menu == "Boshqaruv Paneli":
    st.title("📊 Mening Raqamli Ekosistemam")
    
    # Metrikalarni hisoblash
    total_trees = len(st.session_state.tree_db)
    total_credits = st.session_state.tree_db['kredit'].sum()
    total_income = st.session_state.tree_db['daromad'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Jami Daraxtlar", f"{total_trees} ta")
    col2.metric("Karbon Kreditlar", f"{total_credits:.3f} t", "+0.02")
    col3.metric("Jami Daromad", f"${total_income:.2f}", "+15%")
    col4.metric("Kiber-Xavfsizlik", "Active ✅")

    st.subheader("📍 Mening daraxtlarim xaritada")
    
    # Xaritani yaratish
    m = folium.Map(location=[41.3111, 69.2405], zoom_start=12)
    for index, row in st.session_state.tree_db.iterrows():
        folium.Marker(
            [row['lat'], row['lon']], 
            popup=f"{row['turi']} (#{row['id']})", 
            icon=folium.Icon(color='green', icon='leaf')
        ).add_to(m)
    
    st_folium(m, width=1100, height=450)

    st.subheader("📋 Ro'yxatga olingan aktivlar")
    st.dataframe(st.session_state.tree_db, use_container_width=True)

# --- 2-BO'LIM: SERTIFIKATLASH ---
elif menu == "Yangi Daraxt Sertifikatlash":
    st.title("🌳 Yangi Daraxtni Sertifikatlash")
    
    with st.form("tree_form"):
        col1, col2 = st.columns(2)
        with col1:
            t_type = st.selectbox("Daraxt turi:", ["Archa", "Chinor", "Mevali", "Terak"])
            t_age = st.number_input("Daraxt yoshi (yil):", min_value=1, value=5)
            t_height = st.number_input("Daraxt balandligi (metrda):", min_value=0.5, value=2.0)
        
        with col2:
            lat = st.number_input("Kordinata (Lat) - masalan: 41.31", value=41.3111, format="%.6f")
            lon = st.number_input("Kordinata (Lon) - masalan: 69.24", value=69.2405, format="%.6f")
            photo = st.file_uploader("Daraxt rasmini yuklang:", type=['jpg', 'png'])

        submitted = st.form_submit_button("🚀 Sertifikatlash va Bazaga qo'shish")

        if submitted:
            if photo:
                new_kredit, new_daromad = calculate_metrics(t_type, t_age)
                new_id = hashlib.sha256(f"{lat}{lon}{datetime.now()}".encode()).hexdigest()[:6].upper()
                
                # Yangi ma'lumotni bazaga qo'shish
                new_data = {
                    "id": new_id, 
                    "turi": t_type, 
                    "yoshi": t_age, 
                    "lat": lat, 
                    "lon": lon, 
                    "kredit": new_kredit, 
                    "daromad": new_daromad
                }
                st.session_state.tree_db = pd.concat([st.session_state.tree_db, pd.DataFrame([new_data])], ignore_index=True)
                
                st.balloons()
                st.success(f"Daraxt muvaffaqiyatli sertifikatlandi! ID: #{new_id}")
                st.info(f"Ushbu daraxt yillik {new_kredit:.3f} tonna CO2 yutadi.")
            else:
                st.error("Iltimos, daraxt rasmini yuklang!")

# --- 3-BO'LIM: MARKETPLACE ---
elif menu == "Bozor (Marketplace)":
    st.title("💰 Karbon Kreditlar Bozori")
    st.write("Sizning jami balansingiz: **" + f"{st.session_state.tree_db['kredit'].sum():.3f}" + " t**")
    
    st.table(pd.DataFrame({
        "Xaridor": ["Tesla", "Google", "UzAuto"],
        "Narx (1t)": ["$70", "$65", "$60"],
        "Holat": ["Ochiq", "Ochiq", "Kutilmoqda"]
    }))
