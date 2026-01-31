"""DeepLearn - 学習支援アプリ メインUI"""
import streamlit as st
import urllib.parse
import time
from gemini_client import GeminiClient
from youtube_handler import YouTubeHandler
from pdf_handler import PDFHandler
from database import Database

# ページ設定
st.set_page_config(
    page_title="DeepLearn - 学習支援アプリ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- スタイリッシュUI & アニメーション設定 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@700&family=Inter:wght@400;600&display=swap');
    
    :root {
        --primary: #667eea;
        --secondary: #764ba2;
        --accent: #00f2fe;
        --bg-dark: #1a1a2e;
        --text-main: #2d3436;
    }

    /* 全体背景 */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fd;
    }

    /* --- 起動時派手なアニメーション --- */
    @keyframes splash {
        0% { transform: scale(0.8); opacity: 0; filter: blur(10px); }
        50% { transform: scale(1.05); opacity: 1; filter: blur(0px); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 10px #fff, 0 0 20px var(--accent); }
        50% { text-shadow: 0 0 20px #fff, 0 0 40px var(--accent); }
    }

    .hero-container {
        background: linear-gradient(135deg, var(--bg-dark) 0%, var(--secondary) 100%);
        border-radius: 30px;
        padding: 5rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 25px 50px rgba(0,0,0,0.2);
        animation: splash 1.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        position: relative;
        overflow: hidden;
    }

    .hero-icon {
        font-size: 5rem;
        margin-bottom: 1rem;
        display: inline-block;
        filter: drop-shadow(0 0 15px var(--accent));
    }

    .hero-title {
        font-family: 'Exo 2', sans-serif;
        font-size: 4.5rem;
        background: linear-gradient(to right, #fff, var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 3s infinite;
        margin: 0;
    }

    /* --- 視認性改善（白ボタン対策） --- */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        width: 100%;
    }

    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }

    /* --- スマホ最適化（サイドバー＆レイアウト） --- */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem !important; }
        .hero-container { padding: 3rem 1rem !important; }
        
        /* スマホ時にサイドバー内の要素を大きく */
        section[data-testid="stSidebar"] {
            width: 80vw !important;
        }
        .stSelectbox, .stTextInput, .stTextArea {
            margin-bottom: 1.5rem !important;
        }
        
        /* カードのスタック */
        .feature-grid { grid-template-columns: 1fr !important; }
    }

    /* フィーチャーカード */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid #eee;
        transition: 0.3s;
    }
    .feature-card:hover {
        border-color: var(--primary);
        box-shadow: 0 15px 30px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        # 起動時の演出時間
        # time.sleep(0.5) 
    
    defaults = {
        'current_text': None, 'current_title': None,
        'current_source_type': None, 'current_source_url': None,
        'summaries': {}, 'key_points': None, 'quiz': None, 'view_mode': None
    }
    for key, value in defaults.items():
        if key not in st.session_state: st.session_state[key] = value

def get_gemini_client():
    if 'gemini_client' not in st.session_state:
        st.session_state.gemini_client = GeminiClient()
    return st.session_state.gemini_client

def sidebar():
    with st.sidebar:
        st.markdown("<h1 style='color:white; font-family:Exo 2;'>🧠 DeepLearn</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#aaa;'>Next-Gen Learning AI</p>", unsafe_allow_html=True)
        st.write("---")
        
        mode = st.radio("メニュー", ["ホーム", "ナレッジベース"], label_visibility="collapsed")
        if mode == "ナレッジベース":
            st.session_state.view_mode = "knowledge_base"
        else:
            st.session_state.view_mode = None

        st.markdown("### 📥 追加")
        source_type = st.selectbox("ソース", ["YouTube", "PDF", "Text"])
        
        if source_type == "YouTube":
            url = st.text_input("URLを入力")
            if st.button("🚀 読み込む") and url:
                with st.spinner("Analyzing..."):
                    res = YouTubeHandler().get_transcript_from_url(url)
                    st.session_state.current_text = res['text']
                    st.session_state.current_title = "YouTube Video"
                    st.session_state.summaries = {}
                    st.rerun()
        
        elif source_type == "PDF":
            file = st.file_uploader("ファイルをアップロード")
            if file and st.button("🚀 解析開始"):
                res = PDFHandler.extract_text_from_bytes(file.read())
                st.session_state.current_text = res['text']
                st.session_state.current_title = file.name
                st.session_state.summaries = {}
                st.rerun()
        
        else:
            txt = st.text_area("テキストを入力")
            if st.button("🚀 学習開始") and txt:
                st.session_state.current_text = txt
                st.session_state.current_title = "Input Text"
                st.rerun()

def render_landing():
    st.markdown("""
    <div class="hero-container">
        <div class="hero-icon">💎</div>
        <h1 class="hero-title">DEEP LEARN</h1>
        <p class="hero-subtitle">AIがあなたの学習を劇的に効率化する</p>
    </div>
    <div class="feature-grid">
        <div class="feature-card"><h2>🎬</h2><b>YouTube</b><p>動画を瞬時に要約</p></div>
        <div class="feature-card"><h2>📄</h2><b>Document</b><p>PDFから重要点を抽出</p></div>
        <div class="feature-card"><h2>⚡</h2><b>Teaching</b><p>教えるモードで定着</p></div>
    </div>
    """, unsafe_allow_html=True)

def main_content():
    if st.session_state.view_mode == "knowledge_base":
        st.title("📂 Knowledge Base")
        if st.button("← 戻る"):
            st.session_state.view_mode = None
            st.rerun()
        db = Database()
        for item in db.get_all_knowledge():
            with st.expander(item['title']):
                st.write(item['created_at'])
                if st.button("再開", key=item['id']):
                    st.session_state.current_text = item['original_text']
                    st.session_state.view_mode = None
                    st.rerun()
        return

    if st.session_state.current_text is None:
        render_landing()
        return

    st.title(f"📖 {st.session_state.current_title}")
    tabs = st.tabs(["📝 要約", "🎯 ポイント", "❓ クイズ", "💾 保存"])
    client = get_gemini_client()

    with tabs[0]:
        cols = st.columns(3)
        lvls = [('10min', 'クイック'), ('30min', '標準'), ('1hour', '詳細')]
        for i, (k, l) in enumerate(lvls):
            if cols[i].button(f"⚡ {l}"):
                with st.spinner("AI Generating..."):
                    st.session_state.summaries[k] = client.summarize(st.session_state.current_text, k)
        
        for k in st.session_state.summaries:
            st.markdown(f"--- \n ### {k} Summary")
            st.write(st.session_state.summaries[k])

    with tabs[1]:
        if st.button("ポイントを抽出"):
            st.session_state.key_points = client.extract_key_points(st.session_state.current_text)
        if st.session_state.key_points: st.write(st.session_state.key_points)

    with tabs[2]:
        if st.button("クイズ作成"):
            st.session_state.quiz = client.generate_quiz(st.session_state.current_text, 5)
        if st.session_state.quiz: st.write(st.session_state.quiz)

    with tabs[3]:
        if st.button("ナレッジベースに保存"):
            Database().save_knowledge(title=st.session_state.current_title, original_text=st.session_state.current_text, summaries=st.session_state.summaries)
            st.success("Saved!")
            st.balloons()

def main():
    init_session_state()
    sidebar()
    main_content()

if __name__ == "__main__":
    main()
