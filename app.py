import streamlit as st
import requests
import fitz  # PyMuPDF
from datetime import datetime, timedelta, timezone
from streamlit_autorefresh import st_autorefresh  # NEW

# --- IST Timezone Setup ---
IST = timezone(timedelta(hours=5, minutes=30))

# --- Configuration ---
st.set_page_config(page_title="FYUGP Assistant", layout="wide")
st_autorefresh(interval=1000, key="realtime_refresh")  # Refresh every 1 second

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# --- Get Internet Date and Time ---
def get_internet_datetime():
    try:
        res = requests.get("https://worldtimeapi.org/api/timezone/Asia/Kolkata", timeout=1)
        if res.status_code == 200:
            dt = datetime.fromisoformat(res.json()["datetime"])
            return dt.strftime("%d %b %Y, %I:%M:%S %p")  # ⏱️ With seconds
    except:
        pass
    return datetime.now(IST).strftime("%d %b %Y, %I:%M:%S %p")  # ⏱️ With seconds

# --- Custom CSS ---
st.markdown("""
    <style>
    body { background: #111; }
    .css-18ni7ap.e8zbici2 { background: #111; }

    .sidebar {
        width: 180px;
        padding: 20px;
        color: white;
    }

    .content {
        flex: 1;
        padding: 30px;
        color: white;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        background-color: rgba(255, 255, 255, 0.05);
    }

    .title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(270deg, #00ccff, #00ff99, #ff0099, #00ccff);
        background-size: 600% 600%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleGlow 9s ease infinite;
    }

    .subtitle {
        text-align: center;
        color:#aaa;
        margin-bottom: 30px;
    }

    .message {
        background-color: #333;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 10px;
    }

    .user {
        text-align: right;
        background-color: #004d99;
        color: white;
    }

    .bot {
        text-align: left;
        background-color: #006600;
        color: white;
    }

    a button {
        background: linear-gradient(135deg, #00ccff, #00ff99, #ff0099);
        background-size: 300% 300%;
        color: black;
        padding: 10px 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 10px;
        width: 100%;
        cursor: pointer;
        box-shadow: 0 0 6px rgba(0, 255, 255, 0.15);
        transition: all 0.3s ease;
    }

    a button:hover {
        transform: translateY(-4px);
        box-shadow: 0 0 12px rgba(0, 255, 255, 0.35);
        background-position: right center;
    }

    @keyframes titleGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
""", unsafe_allow_html=True)

# --- Layout ---
col1, col2 = st.columns([1, 4])

# --- DuckDuckGo Answer Search ---
def duckduckgo_answer(query):
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1,
            "skip_disambig": 1
        }
        response = requests.get(url, params=params, timeout=1)
        data = response.json()
        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"]
        return "❌ No exact answer found. Please try rephrasing your question."
    except Exception as e:
        return f"❌ Failed to get an answer.\n\n**Error:** {str(e)}"

# --- Fast PDF Search ---
def search_pdf(text, query):
    for line in text.split("\n"):
        if query.lower() in line.lower():
            return line.strip()
    return None

# --- Sidebar ---
with col1:
    st.markdown("<div class='sidebar'>", unsafe_allow_html=True)
    st.markdown("## 🔗 Quick Access")

    st.markdown("""
    <a href="https://thunderous-sunflower-7230f3.netlify.app/" target="_blank">
        <button>📝 Notes Site</button>
    </a>
    <a href="https://keralauniversity.ac.in/" target="_blank">
        <button>🏛️ University Site</button>
    </a>
    <a href="https://slcm.keralauniversity.ac.in/" target="_blank">
        <button>📚 Course Site</button>
    </a>
    <a href="https://casmvk.kerala.gov.in/" target="_blank">
        <button>🏫 College Site</button>
    </a>
    """, unsafe_allow_html=True)

    if "help_visible" not in st.session_state:
        st.session_state.help_visible = False

    if st.circle("❓ Help / Guide"):
        st.session_state.help_visible = not st.session_state.help_visible

    if st.session_state.help_visible:
        st.info("Use sidebar buttons to use the websites or ask your doubts in the search bar (use small letters) and upload a PDF and ask from it.")

    uploaded_file = st.file_uploader("📄 Upload a Notes PDF", type=["pdf"])
    if uploaded_file:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        st.session_state.pdf_text = full_text
        st.success("✅ PDF loaded! Now ask anything from it.")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Chat Area ---
with col2:
    st.markdown("<div class='content'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>StudyPanda</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Ask from PDF, Useful websites, or any doubt, Nb:- Use Small Letters for get the answers</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:right; color:#888;'> {get_internet_datetime()}</div>", unsafe_allow_html=True)

    for role, msg in st.session_state.chat_history:
        css_class = "user" if role == "user" else "bot"
        st.markdown(f"<div class='message {css_class}'>{msg}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Type your question here...")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        user_lower = user_input.lower()

        if "vc" in user_lower:
            answer = "👨‍🏫 The Vice Chancellor of Kerala University is Prof. Dr. Mohanan Kunnummal (as of 2025)."
        elif "fyugp" in user_lower:
            answer = "📘 FYUGP = Four Year Undergraduate Programme under NEP 2020. It includes flexible exits, skill credits, and multidisciplinary options."
        elif "who is aju" in user_lower:
            answer = (
                "Aju is a passionate and creative student with a strong interest in building useful and innovative digital tools. "
                "Aju lived in Eravankara. Instagram id : "
                "<a href='https://www.instagram.com/aaram_thamburan__?igsh=MTJqangxaXhwYTlhaA==' target='_blank'>@aaram_thamburan__</a> "
                "Follow him on instagram. "
                "He is now studying in the CAS MAVELIKARA in the Bsc Computer Science. "
                "Always eager to learn, Aju enjoys turning ideas into real projects—especially web apps and educational tools that help others. "
                "With a focus on simplicity and accessibility, Aju combines technical skills and thoughtful design to make meaningful contributions, "
                "especially in the field of education and technology. Whether it’s creating chatbots, websites for sharing college resources, or Android apps like 'Attendix', "
                "Aju shows both dedication and curiosity in every project. The FYUGP Assistant is a smart chatbot interface designed and developed by Aju "
                "to help students easily access semester-wise notes, model papers, and important university links—through one intelligent and interactive platform."
            )
        elif st.session_state.pdf_text:
            pdf_answer = search_pdf(st.session_state.pdf_text, user_input)
            if pdf_answer:
                answer = f"📄 From PDF:\n\n{pdf_answer}"
            else:
                answer = duckduckgo_answer(user_input)
        else:
            answer = duckduckgo_answer(user_input)

        st.session_state.chat_history.append(("bot", answer))
        st.rerun()

    st.markdown("<div style='text-align:center; color:#666; margin-top: 30px;'>© 2025 | Published by Aju Krishna</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
