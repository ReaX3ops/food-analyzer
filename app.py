import streamlit as st
from google import genai
from PIL import Image
import json

st.set_page_config(
    page_title="SnackScan",
    page_icon="🍱",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

* { font-family: 'Outfit', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 700px; }

.hero-card {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 24px;
    padding: 1.8rem 2.5rem;
    text-align: center;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f8f8f8, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.hero-sub {
    color: rgba(255,255,255,0.45);
    font-size: 0.92rem;
    margin-top: 0.3rem;
    font-weight: 300;
}

.glass-card {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.25);
}
.label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(167,139,250,0.8);
    margin-bottom: 0.3rem;
}
.food-name {
    font-size: 1.9rem;
    font-weight: 700;
    color: #f8f8f8;
}
.calories-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #34d399;
}
.calories-unit {
    font-size: 0.95rem;
    color: rgba(255,255,255,0.4);
    font-weight: 300;
    margin-left: 4px;
}

.ingredient-tag {
    display: inline-block;
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 50px;
    padding: 5px 16px;
    margin: 4px;
    font-size: 0.88rem;
    color: rgba(255,255,255,0.85);
}

.nutrition-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
    margin-top: 0.6rem;
}
.nutrition-item {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 0.9rem 0.5rem;
    text-align: center;
}
.nutrition-icon { font-size: 1.4rem; }
.nutrition-name {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.45);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.2rem;
}
.nutrition-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #f8f8f8;
    margin-top: 0.1rem;
}

[data-testid="stFileUploadDropzone"] {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(167,139,250,0.4) !important;
    border-radius: 16px !important;
}
[data-testid="stFileUploadDropzone"] p { color: rgba(255,255,255,0.45) !important; }

[data-testid="stImage"] img {
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
}

.stButton > button {
    background: rgba(167,139,250,0.2) !important;
    border: 1px solid rgba(167,139,250,0.4) !important;
    color: white !important;
    border-radius: 50px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.85rem !important;
}
.stButton > button:hover {
    background: rgba(167,139,250,0.35) !important;
}

.stAlert {
    background: rgba(239,68,68,0.1) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    border-radius: 14px !important;
    color: #fca5a5 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Init session state ──
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "result" not in st.session_state:
    st.session_state.result = None
if "image" not in st.session_state:
    st.session_state.image = None

def t(en, km):
    return km if st.session_state.lang == "km" else en

# ── Hero ──
st.markdown(f"""
<div class="hero-card">
    <div class="hero-title">🍱 SnackScan</div>
    <div class="hero-sub">{t("Upload a photo — get food name, calories & nutrition instantly",
                             "បង្ហោះរូបភាព — ទទួលបានឈ្មោះម្ហូប កាឡូរី និងជីវជាតិភ្លាមៗ")}</div>
</div>
""", unsafe_allow_html=True)

# ── Language toggle (no rerun needed, just flips the label) ──
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🇰🇭 KM" if st.session_state.lang == "en" else "🇬🇧 EN"):
        st.session_state.lang = "km" if st.session_state.lang == "en" else "en"

# ── Gemini client ──
@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

client = get_client()

# ── Upload ──
uploaded_file = st.file_uploader(
    t("Upload food image", "បង្ហោះរូបភាពម្ហូប"),
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed"
)

if uploaded_file:
    img = Image.open(uploaded_file)
    st.session_state.image = img

    # Only call Gemini if we don't have a result yet
    if st.session_state.result is None:
        with st.spinner(t("Analyzing your food...", "កំពុងវិភាគម្ហូបរបស់អ្នក...")):
            prompt = """Analyze the food image.

Return ONLY a JSON object, no markdown, no explanation:

{
  "food_en": "food name in English",
  "food_km": "food name in Khmer",
  "calories": "estimated total calories as number only",
  "ingredients_en": ["ingredient1", "ingredient2", "ingredient3"],
  "ingredients_km": ["ingredient1 in Khmer", "ingredient2 in Khmer", "ingredient3 in Khmer"],
  "nutrition": {
    "protein": "Xg",
    "carbs": "Xg",
    "fat": "Xg",
    "fiber": "Xg",
    "sugar": "Xg",
    "sodium": "Xmg"
  }
}"""

            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt, img]
                )
                text = response.text.replace("```json", "").replace("```", "").strip()
                st.session_state.result = json.loads(text)
            except Exception as e:
                st.error(f"Error analyzing image: {e}")

# ── Display results ──
if st.session_state.image is not None:
    st.image(st.session_state.image, use_container_width=True)

if st.session_state.result is not None:
    data = st.session_state.result
    lang = st.session_state.lang

    food = data.get("food_km" if lang == "km" else "food_en", "Unknown")
    calories = str(data.get("calories", "?"))
    nutrition = data.get("nutrition", {})
    ignore = ["bun", "bread", "beef patty"]
    ingredients_key = "ingredients_km" if lang == "km" else "ingredients_en"
    ingredients = [i for i in data.get(ingredients_key, []) if i.lower() not in ignore]

    st.markdown(f"""
    <div class="glass-card">
        <div class="label">{t("Detected Food", "ម្ហូបដែលបានរកឃើញ")}</div>
        <div class="food-name">🍽️ {food}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card">
        <div class="label">{t("Estimated Calories", "កាឡូរីដែលប៉ាន់ស្មាន")}</div>
        <div><span class="calories-value">🔥 {calories}</span><span class="calories-unit">kcal</span></div>
    </div>""", unsafe_allow_html=True)

    if nutrition:
        items = [
            ("💪", t("Protein", "ប្រូតេអ៊ីន"),   nutrition.get("protein", "–")),
            ("🍞", t("Carbs",   "កាបូអ៊ីដ្រាត"),  nutrition.get("carbs",   "–")),
            ("🧈", t("Fat",     "ខ្លាញ់"),         nutrition.get("fat",     "–")),
            ("🌿", t("Fiber",   "ជាតិសរសៃ"),       nutrition.get("fiber",   "–")),
            ("🍬", t("Sugar",   "ស្ករ"),           nutrition.get("sugar",   "–")),
            ("🧂", t("Sodium",  "អំបិល"),          nutrition.get("sodium",  "–")),
        ]
        grid = "".join(f"""<div class="nutrition-item">
            <div class="nutrition-icon">{icon}</div>
            <div class="nutrition-name">{name}</div>
            <div class="nutrition-value">{val}</div>
        </div>""" for icon, name, val in items)

        st.markdown(f"""
        <div class="glass-card">
            <div class="label">{t("Nutrition Breakdown", "តម្លៃអាហារូបត្ថម្ភ")}</div>
            <div class="nutrition-grid">{grid}</div>
        </div>""", unsafe_allow_html=True)

    if ingredients:
        tags = "".join(f'<span class="ingredient-tag">{i}</span>' for i in ingredients)
        st.markdown(f"""
        <div class="glass-card">
            <div class="label">{t("Ingredients", "គ្រឿងផ្សំ")}</div>
            <div style="margin-top:0.6rem">{tags}</div>
        </div>""", unsafe_allow_html=True)
