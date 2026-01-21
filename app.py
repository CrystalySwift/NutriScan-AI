# app.py - UPDATED WITH IMAGE UPLOAD
import streamlit as st
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from typing import Dict, Any
import tempfile
from PIL import Image

# Import our modules
try:
    from database import NutritionDatabase, extract_number
    from image_classifier import get_food_classifier
    from deepseek_api import get_nutrition_api, extract_number as extract_num
except ImportError:
    # Fallback if modules are in same directory
    import sys
    sys.path.append('.')
    from database import NutritionDatabase, extract_number
    from image_classifier import get_food_classifier
    from deepseek_api import get_nutrition_api, extract_number as extract_num

# -------------------------
# KONFIGURASI APLIKASI
# -------------------------
st.set_page_config(
    page_title="Food Nutrition Assistant",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def init_database():
    return NutritionDatabase()

db = init_database()

# Initialize classifier and API (cached)
@st.cache_resource
def init_classifier():
    return get_food_classifier()

@st.cache_resource
def init_nutrition_api():
    return get_nutrition_api()

# -------------------------
# SESSION STATE MANAGEMENT
# -------------------------
def init_session_state():
    """Initialize session state variables"""
    if "page" not in st.session_state:
        st.session_state.page = "login"
    
    if "user" not in st.session_state:
        st.session_state.user = None
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    if "current_data" not in st.session_state:
        st.session_state.current_data = {}
    
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    
    if "food_input" not in st.session_state:
        st.session_state.food_input = ""
    
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    
    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None
    
    if "nutrition_result" not in st.session_state:
        st.session_state.nutrition_result = None

init_session_state()

# -------------------------
# DEEPSEEK API CONFIGURATION
# -------------------------
st.sidebar.title("🔧 Konfigurasi")

# API Key Management
api_source = st.sidebar.radio(
    "Sumber API Key:",
    ["Masukkan Manual", "Environment Variable", "Gratis (Demo Mode)"],
    key="api_source"
)

DEEPSEEK_API_KEY = None

if api_source == "Masukkan Manual":
    DEEPSEEK_API_KEY = st.sidebar.text_input(
        "DeepSeek API Key", 
        type="password",
        help="Dapatkan dari https://platform.deepseek.com/api_keys",
        key="api_key_input"
    )
elif api_source == "Environment Variable":
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
    if DEEPSEEK_API_KEY:
        st.sidebar.success("✅ API Key ditemukan")
    else:
        st.sidebar.warning("❌ DEEPSEEK_API_KEY tidak ditemukan")

USE_FREE_MODE = api_source == "Gratis (Demo Mode)"

if USE_FREE_MODE:
    st.sidebar.info("🔓 **Demo Mode Aktif**")

# Initialize API with key
nutrition_api = init_nutrition_api()
if DEEPSEEK_API_KEY:
    nutrition_api.api_key = DEEPSEEK_API_KEY

# -------------------------
# IMAGE UPLOAD & PREDICTION FUNCTIONS
# -------------------------
def handle_image_upload():
    """Handle image upload and food prediction"""
    
    st.subheader("📸 Upload Foto Makanan")
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Pilih foto makanan Anda",
        type=['jpg', 'jpeg', 'png', 'webp'],
        help="Upload foto makanan untuk dianalisis secara otomatis"
    )
    
    if uploaded_file is not None:
        # Display image
        image = Image.open(uploaded_file)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(image, caption="Foto Makanan", width=250)
        
        with col2:
            # Save to session state
            st.session_state.uploaded_image = image
            
            # Predict button
            if st.button("🔍 Analisis Gambar", type="primary"):
                with st.spinner("Menganalisis gambar..."):
                    # Initialize classifier
                    classifier = init_classifier()
                    
                    # Make prediction
                    predictions = classifier.predict(image, top_k=3)
                    
                    if predictions:
                        st.session_state.prediction_result = predictions
                        
                        # Display predictions
                        st.success("✅ Gambar berhasil dianalisis!")
                        
                        st.write("**Hasil Prediksi:**")
                        for food_name, confidence in predictions:
                            st.write(f"• {food_name} ({confidence:.1%} confidence)")
                        
                        # Button to use prediction
                        if st.button("Gunakan Prediksi Terbaik", type="secondary"):
                            best_food = predictions[0][0]
                            st.session_state.food_input = best_food
                            st.rerun()
                    
                    else:
                        st.error("❌ Tidak dapat mengenali makanan dalam gambar")
    
    # Or use camera
    with st.expander("📷 Atau gunakan kamera"):
        camera_photo = st.camera_input("Ambil foto dengan kamera")
        
        if camera_photo:
            image = Image.open(camera_photo)
            st.session_state.uploaded_image = image
            
            if st.button("Analisis Foto Kamera", type="primary"):
                with st.spinner("Menganalisis gambar..."):
                    classifier = init_classifier()
                    predictions = classifier.predict(image, top_k=3)
                    
                    if predictions:
                        st.session_state.prediction_result = predictions
                        st.success(f"✅ Terdeteksi: {predictions[0][0]}")
                        
                        # Auto-fill with best prediction
                        st.session_state.food_input = predictions[0][0]
                        st.rerun()

def get_nutrition_from_prediction(food_name, portion_size="normal"):
    """Get nutrition analysis for predicted food"""
    with st.spinner(f"Analisis nutrisi {food_name}..."):
        nutrition = nutrition_api.analyze_food_nutrition(food_name, portion_size)
        return nutrition

# -------------------------
# AUTHENTICATION PAGES
# -------------------------
def login_page():
    """Login page"""
    st.title("🍎 Food Nutrition Assistant")
    st.markdown("### Masuk ke Akun Anda")
    
    # Demo credentials
    with st.expander("ℹ️ Akun Demo"):
        st.code("Email: demo@example.com\nPassword: demo123")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3077/3077321.png", width=150)
    
    with col2:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔐 Login", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Email dan password harus diisi")
                else:
                    user = db.authenticate_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.user_id = user['id']
                        st.session_state.page = "home"
                        st.success(f"Selamat datang, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Email atau password salah")
        
        with col_btn2:
            if st.button("📝 Daftar Baru", use_container_width=True):
                st.session_state.show_register = True
                st.rerun()
    
    # Registration form
    if st.session_state.show_register:
        st.markdown("---")
        st.subheader("📝 Pendaftaran Akun Baru")
        
        reg_col1, reg_col2 = st.columns(2)
        
        with reg_col1:
            reg_name = st.text_input("Nama Lengkap", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
        
        with reg_col2:
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_confirm = st.text_input("Konfirmasi Password", type="password", key="reg_confirm")
        
        if st.button("✅ Daftar Sekarang", type="primary"):
            if not all([reg_name, reg_email, reg_password, reg_confirm]):
                st.error("Semua field harus diisi")
            elif reg_password != reg_confirm:
                st.error("Password tidak cocok")
            elif len(reg_password) < 6:
                st.error("Password minimal 6 karakter")
            elif db.user_exists(reg_email):
                st.error("Email sudah terdaftar")
            else:
                user_id = db.create_user(reg_email, reg_password, reg_name)
                if user_id:
                    st.success("🎉 Akun berhasil dibuat! Silakan login.")
                    st.session_state.show_register = False
                    st.rerun()
                else:
                    st.error("Gagal membuat akun")
        
        if st.button("❌ Batal"):
            st.session_state.show_register = False
            st.rerun()

def logout():
    """Logout user"""
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.page = "login"
    st.rerun()

# -------------------------
# UPDATED HOME PAGE WITH IMAGE UPLOAD
# -------------------------
def home_page():
    """Main home page with image upload"""
    # Load user profile
    user_profile = db.get_user_profile(st.session_state.user_id)
    
    if not user_profile:
        st.error("Profil tidak ditemukan. Silakan login kembali.")
        logout()
        return
    
    # Header
    col_header1, col_header2, col_header3 = st.columns([3, 1, 1])
    with col_header1:
        st.title(f"🍎 Selamat Datang, {user_profile['name']}!")
        st.caption("Upload foto makanan atau ketik manual")
    with col_header2:
        st.metric("📅 Hari Ini", datetime.now().strftime("%d %b"))
    with col_header3:
        if st.button("🚪 Logout", type="secondary"):
            logout()
    
    st.markdown("---")
    
    # Today's summary
    today = datetime.now().strftime("%Y-%m-%d")
    today_entries = db.get_daily_entries(st.session_state.user_id, today)
    
    col_summary1, col_summary2, col_summary3, col_summary4 = st.columns(4)
    
    total_cal = sum(entry.get('calories', 0) for entry in today_entries)
    total_pro = sum(entry.get('protein', 0) for entry in today_entries)
    total_water = sum(entry.get('water_ml', 0) for entry in today_entries)
    total_exercise = sum(entry.get('exercise_min', 0) for entry in today_entries)
    
    with col_summary1:
        st.metric("🍽️ Makanan", len(today_entries))
    with col_summary2:
        st.metric("🔥 Kalori", f"{int(total_cal)} kcal")
    with col_summary3:
        st.metric("💧 Air", f"{total_water} ml")
    with col_summary4:
        st.metric("🏃 Olahraga", f"{total_exercise} mnt")
    
    st.markdown("---")
    
    # Main content with tabs
    tab1, tab2, tab3 = st.tabs(["📸 Upload Gambar", "📝 Input Manual", "🍱 Pilihan Cepat"])
    
    with tab1:
        # Image upload section
        handle_image_upload()
        
        # If we have a prediction, show nutrition analysis
        if st.session_state.prediction_result:
            st.markdown("---")
            st.subheader("🥗 Analisis Nutrisi dari Gambar")
            
            # Let user select which prediction to use
            predictions = st.session_state.prediction_result
            prediction_options = [f"{name} ({conf:.1%})" for name, conf in predictions]
            
            selected_idx = st.selectbox(
                "Pilih prediksi yang ingin digunakan:",
                range(len(predictions)),
                format_func=lambda i: prediction_options[i]
            )
            
            selected_food = predictions[selected_idx][0]
            selected_confidence = predictions[selected_idx][1]
            
            col_portion1, col_portion2 = st.columns(2)
            with col_portion1:
                portion = st.selectbox("Ukuran Porsi", ["Kecil", "Normal", "Besar"], index=1, key="img_portion")
            with col_portion2:
                water = st.number_input("💧 Air (ml)", min_value=0, max_value=5000, value=500, step=100, key="img_water")
            
            # Button to analyze nutrition
            if st.button("🧪 Analisis Nutrisi dari Gambar", type="primary"):
                with st.spinner(f"Menganalisis nutrisi {selected_food}..."):
                    # Get nutrition from DeepSeek API
                    nutrition = get_nutrition_from_prediction(selected_food, portion.lower())
                    
                    # Display results
                    st.success(f"✅ Nutrisi {selected_food} berhasil dianalisis!")
                    
                    col_nut1, col_nut2 = st.columns(2)
                    with col_nut1:
                        st.metric("🔥 Kalori", nutrition.get('calories', '0 kcal'))
                        st.metric("🥩 Protein", nutrition.get('protein', '0 g'))
                    with col_nut2:
                        st.metric("🥑 Lemak", nutrition.get('fat', '0 g'))
                        st.metric("🍞 Karbo", nutrition.get('carbs', '0 g'))
                    
                    if 'notes' in nutrition:
                        st.info(f"📝 **Catatan:** {nutrition['notes']}")
                    
                    # Save button
                    if st.button("💾 Simpan ke Database", type="secondary"):
                        entry_data = {
                            "food": selected_food,
                            "portion": portion,
                            "nutrition": nutrition,
                            "water": water,
                            "exercise": 0,
                            "date": today,
                            "prediction_confidence": selected_confidence,
                            "source": "image_upload"
                        }
                        
                        if db.add_daily_entry(st.session_state.user_id, entry_data):
                            st.success("✅ Data berhasil disimpan!")
                            st.session_state.current_data = entry_data
                            st.session_state.page = "report"
                            st.rerun()
    
    with tab2:
        # Manual input section
        st.subheader("📝 Input Manual")
        
        food_name = st.text_input(
            "🍽️ Apa yang kamu makan/minum?",
            value=st.session_state.food_input,
            placeholder="Contoh: Nasi goreng, Salad buah, Ayam bakar...",
            key="food_input_manual"
        )
        
        col_input1, col_input2, col_input3 = st.columns(3)
        with col_input1:
            portion = st.selectbox("Porsi", ["Kecil", "Normal", "Besar"], index=1, key="manual_portion")
        with col_input2:
            water = st.number_input("💧 Air (ml)", min_value=0, max_value=5000, value=500, step=100, key="manual_water")
        with col_input3:
            exercise = st.number_input("🏃 Olahraga (mnt)", min_value=0, max_value=300, value=0, step=5, key="manual_exercise")
        
        if st.button("🔍 Analisis & Simpan", type="primary", use_container_width=True):
            if not food_name.strip():
                st.error("❗ Masukkan nama makanan terlebih dahulu")
            else:
                with st.spinner("Menganalisis nutrisi..."):
                    # Get nutrition from DeepSeek API
                    nutrition = get_nutrition_from_prediction(food_name, portion.lower())
                    
                    entry_data = {
                        "food": food_name,
                        "portion": portion,
                        "nutrition": nutrition,
                        "water": water,
                        "exercise": exercise,
                        "date": today
                    }
                    
                    # Save to database
                    if db.add_daily_entry(st.session_state.user_id, entry_data):
                        st.success("✅ Data berhasil disimpan!")
                        st.session_state.current_data = entry_data
                        st.session_state.page = "report"
                        st.session_state.food_input = ""  # Clear input
                        st.rerun()
                    else:
                        st.error("❌ Gagal menyimpan data")
    
    with tab3:
        # Quick selection
        st.subheader("🍱 Pilihan Cepat")
        
        quick_foods = ["Nasi Goreng", "Ayam Goreng", "Tempe Goreng", "Buah Pisang", 
                      "Sayur Bayam", "Telur Rebus", "Sate Ayam", "Rendang"]
        
        cols = st.columns(4)
        for idx, food in enumerate(quick_foods):
            col = cols[idx % 4]
            if col.button(food, use_container_width=True):
                st.session_state.food_input = food
                st.rerun()
        
        st.markdown("---")
        st.write("Klik makanan di atas untuk mengisi otomatis")
    
    # Right sidebar with targets
    st.sidebar.markdown("---")
    with st.sidebar:
        st.subheader("📊 Target Harian")
        
        # Calculate targets
        weight = user_profile.get('weight', 65)
        target_calories = weight * 30  # Simple formula
        target_water = 2000
        target_exercise = 30
        
        # Progress bars
        cal_percent = min(total_cal / target_calories * 100, 100) if target_calories > 0 else 0
        st.progress(cal_percent / 100, text=f"Kalori: {int(total_cal)}/{target_calories} kcal")
        
        water_percent = min(total_water / target_water * 100, 100)
        st.progress(water_percent / 100, text=f"Air: {total_water}/{target_water} ml")
        
        ex_percent = min(total_exercise / target_exercise * 100, 100)
        st.progress(ex_percent / 100, text=f"Olahraga: {total_exercise}/{target_exercise} mnt")
        
        # Recent entries
        if today_entries:
            st.subheader("📝 Entri Hari Ini")
            for entry in today_entries[:3]:
                st.write(f"• {entry['food_name'][:20]}... ({entry.get('calories', 0)} kcal)")
    
    # Navigation at bottom
    st.markdown("---")
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("📋 Riwayat", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()
    with col_nav2:
        if st.button("📊 Statistik", use_container_width=True):
            st.session_state.page = "stats"
            st.rerun()
    with col_nav3:
        if st.button("👤 Profil", use_container_width=True):
            st.session_state.page = "profile"
            st.rerun()

# -------------------------
# OTHER PAGES (Updated for DeepSeek API)
# -------------------------
def report_page():
    """Nutrition report page"""
    st.title("📄 Laporan Nutrisi")
    
    data = st.session_state.current_data
    if not data:
        st.warning("Tidak ada data untuk ditampilkan")
        if st.button("Kembali ke Home"):
            st.session_state.page = "home"
            st.rerun()
        return
    
    nutrition = data.get('nutrition', {})
    
    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.success(f"✅ **{data.get('food', 'Unknown')}**")
        st.caption(f"Porsi: {data.get('portion', 'Normal')}")
        if 'analyzed_at' in nutrition:
            st.caption(f"Dianalisis: {nutrition['analyzed_at'][:16]}")
    with col_h2:
        if st.button("🏠 Kembali ke Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    
    st.markdown("---")
    
    # Nutrition details
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🍽️ Komposisi Nutrisi")
        
        # Display key metrics
        metrics = [
            ("🔥 Kalori", nutrition.get('calories', '0 kcal'), "#FF6B6B"),
            ("🥩 Protein", nutrition.get('protein', '0 g'), "#4ECDC4"),
            ("🥑 Lemak", nutrition.get('fat', '0 g'), "#FFD166"),
            ("🍞 Karbohidrat", nutrition.get('carbs', '0 g'), "#06D6A0"),
        ]
        
        for label, value, color in metrics:
            st.markdown(f"""
            <div style="background-color:{color}20; padding:15px; border-radius:10px; margin:10px 0; border-left:5px solid {color}">
                <h4 style="margin:0; color:{color}">{label}</h4>
                <h2 style="margin:5px 0; color:#333">{value}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional nutrients
        if 'fiber' in nutrition:
            st.write(f"🌾 **Serat:** {nutrition['fiber']}")
        if 'sugar' in nutrition:
            st.write(f"🍬 **Gula:** {nutrition['sugar']}")
        if 'sodium' in nutrition:
            st.write(f"🧂 **Natrium:** {nutrition['sodium']}")
        
        if 'notes' in nutrition:
            st.info(f"📝 **Catatan:** {nutrition['notes']}")
        
        if 'source' in nutrition:
            source_map = {
                'deepseek_api': '🤖 AI DeepSeek',
                'text_extraction': '📝 Analisis Teks',
                'fallback_estimation': '📊 Estimasi',
                'image_upload': '📸 Upload Gambar'
            }
            st.caption(f"**Sumber:** {source_map.get(nutrition['source'], '📊 Data')}")
    
    with col2:
        st.subheader("🏃 Aktivitas")
        
        st.metric("💧 Air Minum", f"{data.get('water', 0)} ml")
        st.metric("⏱️ Olahraga", f"{data.get('exercise', 0)} menit")
        
        # Progress bars
        water_target = 2000
        water_percent = min(data.get('water', 0) / water_target * 100, 100)
        st.progress(water_percent / 100, 
                   text=f"Target air: {water_percent:.0f}%")
        
        ex_target = 30
        ex_percent = min(data.get('exercise', 0) / ex_target * 100, 100)
        st.progress(ex_percent / 100,
                   text=f"Target olahraga: {ex_percent:.0f}%")
        
        # Nutrition tips
        st.subheader("💡 Tips Nutrisi")
        calories = extract_num(nutrition.get('calories', '0'))
        
        if calories > 500:
            st.warning("⚠️ Kalori cukup tinggi, perhatikan porsi berikutnya")
        elif calories < 100:
            st.info("🍎 Bisa tambah buah atau kacang untuk energi tambahan")
        
        if data.get('water', 0) < 500:
            st.warning("💧 Minum air lebih banyak sepanjang hari")
    
    st.markdown("---")
    
    # Navigation
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("➕ Tambah Lagi", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with col_nav2:
        if st.button("📋 Lihat Riwayat", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
st.sidebar.markdown("---")

if st.session_state.user:
    st.sidebar.subheader(f"👋 {st.session_state.user.get('name', 'User')}")
    
    st.sidebar.markdown("📍 **Navigasi**")
    
    nav_options = [
        ("🏠 Home", "home"),
        ("📋 Riwayat", "history"),
        ("📊 Statistik", "stats"),
        ("👤 Profil", "profile"),
    ]
    
    for label, page in nav_options:
        if st.sidebar.button(label, use_container_width=True, key=f"nav_{page}"):
            st.session_state.page = page
            st.rerun()
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
        logout()

else:
    st.sidebar.info("🔐 Silakan login untuk menggunakan aplikasi")

# Database info
st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ Info Sistem"):
    stats = db.get_database_stats()
    st.caption(f"**Pengguna:** {stats.get('total_users', 0)}")
    st.caption(f"**Entri:** {stats.get('total_entries', 0)}")
    
    # Check if model exists
    model_exists = os.path.exists("food_model.h5")
    st.caption(f"**Model Keras:** {'✅ Ada' if model_exists else '❌ Tidak ditemukan'}")
    
    # Check API status
    api_status = "✅ Aktif" if nutrition_api.is_available() else "⚠️ Mode Demo"
    st.caption(f"**DeepSeek API:** {api_status}")

# About
st.sidebar.markdown("---")
st.sidebar.caption("""
**Food Nutrition Assistant v3.0**

• Image Recognition: Keras Model
• Nutrition Analysis: DeepSeek AI
• Database: SQLite Local

📸 Fitur baru: Upload foto makanan!
""")

# -------------------------
# MAIN ROUTER
# -------------------------
if st.session_state.user is None:
    login_page()
else:
    # Define page handlers
    page_handlers = {
        "home": home_page,
        "report": report_page,
        # Add other pages here (history, stats, profile)
        # They should work with DeepSeek API too
    }
    
    # Get handler or default to home
    handler = page_handlers.get(st.session_state.page, home_page)
    
    # Add error handling
    try:
        handler()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        if st.button("Kembali ke Home"):
            st.session_state.page = "home"
            st.rerun()

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.caption("© 2024 Food Nutrition Assistant • Keras Model + DeepSeek AI")

# app.py - Di bagian import/initialization

# GANTI ini:
# from image_classifier import get_food_classifier

# MENJADI:
from image_classifier import get_food_classifier

# Atau buat fungsi khusus untuk model Anda:
def get_my_model_classifier():
    """Get classifier with your specific model"""
    from image_classifier import FoodImageClassifier
    return FoodImageClassifier(model_path='best_food_effnet.keras')

# Kemudian di home_page(), ganti:
# classifier = init_classifier()
# MENJADI:
classifier = get_my_model_classifier()