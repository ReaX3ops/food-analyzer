import streamlit as st
from google import genai
from PIL import Image
import json

st.set_page_config(
    page_title="Food Analyzer",
    page_icon="🍱",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Outfit', sans-serif;
}

/* Animated gradient background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* Hide default streamlit elements */
#MainMenu, footer, header {visibility: hidden;}
.block-container {
    padding-top: 2rem;
    max-width: 680px;
}

/* Hero header glass card */
.hero-card {
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 24px;
    padding: 2rem 2.5rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f8f8f8, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.5px;
}

.hero-sub {
    color: rgba(255,255,255,0.5);
    font-size: 0.95rem;
    margin-top: 0.4rem;
    font-weight: 300;
}

/* Upload area styling */
.stFileUploader {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 20px !important;
    border: 2px dashed rgba(167, 139, 250, 0.4) !important;
    padding: 1rem !important;
}

.stFileUploader label {
    color: rgba(255,255,255,0.7) !important;
    font-family: 'Outfit', sans-serif !important;
}

[data-testid="stFileUploadDropzone"] {
    background: rgba(255,255,255,0.03) !important;
    border: none !important;
    border-radius: 14px !important;
}

[data-testid="stFileUploadDropzone"] p {
    color: rgba(255,255,255,0.5) !important;
}

/* Image display */
[data-testid="stImage"] img {
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
}

/* Result cards */
.result-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1.5rem;
}

.glass-card {
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.25);
}

.label {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(167, 139, 250, 0.8);
    margin-bottom: 0.3rem;
}

.food-name {
    font-size: 2rem;
    font-weight: 700;
    color: #f8f8f8;
    line-height: 1.2;
}

.calories-value {
    font-size: 2rem;
    font-weight: 700;
    color: #34d399;
}

.calories-unit {
    font-size: 1rem;
    color: rgba(255,255,255,0.4);
    font-weight: 300;
    margin-left: 4px;
}

.ingredient-tag {
    display: inline-block;
    background: rgba(167, 139, 250, 0.15);
    border: 1px solid rgba(167, 139, 250, 0.3);
    border-radius: 50px;
    padding: 5px 16px;
    margin: 4px;
    font-size: 0.88rem;
    color: rgba(255,255,255,0.85);
    font-weight: 400;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #a78bfa !important;
}

/* Divider */
hr {
    border-color: rgba(255,255,255,0.08) !important;
}

/* Error */
.stAlert {
    background: rgba(239, 68, 68, 0.1) !important;
    border: 1px solid rgba(239, 68, 68, 0.3) !important;
    border-radius: 14px !important;
    color: #fca5a5 !important;
}
</style>
""", unsafe_allow_html=True)

# Hero header
st.markdown("""
<div class="hero-card">
    <div class="hero-title">🍱 Food Analyzer</div>
    <div class="hero-sub">Upload a photo — get food name, calories & ingredients instantly</div>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

client = get_client()

uploaded_file = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, use_container_width=True)

    with st.spinner("Analyzing your food..."):
        prompt = """
Analyze the food image.

Return ONLY JSON like this:

{
  "food": "food name",
  "calories": "estimated calories",
  "ingredients": ["ingredient1","ingredient2","ingredient3"]
}
"""
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, img]
            )

            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)

            food = data.get("food", "មិនដឹង")
            calories = str(data.get("calories", "?"))

            ignore = ["bun", "bread", "beef patty"]
            ingredients = [i for i in data.get("ingredients", []) if i.lower() not in ignore]

            # Results
            st.markdown(f"""
            <div class="result-wrapper">
                <div class="glass-card">
                    <div class="label">Detected Food</div>
                    <div class="food-name">🍽️ {food}</div>
                </div>
                <div class="glass-card">
                    <div class="label">Estimated Calories</div>
                    <div><span class="calories-value">🔥 {calories}</span><span class="calories-unit">kcal</span></div>
                </div>
            """, unsafe_allow_html=True)

            if ingredients:
                tags = "".join(f'<span class="ingredient-tag">{i}</span>' for i in ingredients)
                st.markdown(f"""
                <div class="glass-card">
                    <div class="label">Ingredients</div>
                    <div style="margin-top:0.6rem">{tags}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error analyzing image: {e}")