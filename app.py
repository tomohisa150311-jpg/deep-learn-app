import streamlit as st
import time
from gemini_client import GeminiClient
from youtube_handler import YouTubeHandler
from pdf_handler import PDFHandler
from database import Database

# 1. ページ設定
st.set_page_config(
    page_title="DeepLearn",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed", # サイドバーは基本隠す
)

# --- 2. 漆黒のオープニング & ボトムナビゲーション CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@800&family=Inter:wght@400;600&display=swap');

    /* 全体背景を少し暗めに設定して没入感を出す */
    .stApp {
        background-color: #0f0f1a;
        color: #ffffff;
    }

    /* --- 超派手！漆黒のオープニングアニメーション --- */
    @keyframes deep-flash {
        0% { opacity: 0; filter: brightness(0); transform: scale(0.9); }
        50% { opacity: 1; filter: brightness(1.5); transform: scale(1.05); }
        100% { opacity: 1; filter: brightness(1); transform: scale(1); }
    }
    
    @keyframes text-glow {
        0% { text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe; }
        50% { text-shadow: 0 0 30px #764ba2, 0 0 60px #764ba2; }
        100% { text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe; }
    }

    .opening-container {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #000000;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        z-index: 9999;
        animation: fadeout 1s forwards 2s; /* 2秒後にフェードアウト */
    }
    @keyframes fadeout { to { opacity: 0; visibility: hidden; } }

    .opening-title {
        font-family: 'Exo 2', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 5px;
        animation: deep-flash 1.5s ease-out, text-glow 2s infinite;
    }

    /* --- メインビジュアル & カード --- */
    .hero-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #432371 100%);
        border-radius: 30px;
        padding: 4rem 2rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-family: 'Exo 2', sans-serif;
        font-size: clamp(2.5rem, 10vw, 5rem);
        background: linear-gradient(to right, #00f2fe, #fff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        color: #e0e0e0 !important; /* 黒文字を廃止し、明るいグレーに */
        font-size: 1.2rem;
        font-weight: 400;
    }

    /* --- スマホ用ボトムナビゲーション --- */
    .bottom-nav {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background: rgba(15, 15, 26, 0.95);
        backdrop-filter: blur(10px);
        display: flex; justify-content: space-around;
        padding: 15px 0;
        border-top: 1px solid rgba(255,255,255,0.1);
        z-index: 1000;
    }

    /* ボタンのカスタマイズ（白ボタン問題を完全封印） */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important; /* 丸みのあるモダンな形状 */
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }

    /* カード内のテキストカラー固定 */
    .card {
        background: #1e1e30;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .card h3 { color: #00f2fe !important; margin-bottom: 10px; }
    .card p { color: #cccccc !important; font-size: 0.9rem; }

</style>

<div class="opening-container" id="opening">
    <div class="opening-title">DEEP LEARN</div>
</div>
""", unsafe_allow_html=True)

# 3. セッション管理
def init_state():
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'current_text' not in st.session_state: st.session_state.page = "home"
    # 他のステート初期化...

# 4. メイン画面の描画
def render_home():
    st.markdown("""
    <div class="hero-box">
        <h1 class="hero-title">DEEP LEARN</h1>
        <p class="hero-subtitle">次世代AI学習パートナー</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🚀 学習を始める")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card"><h3>🎬 YouTube</h3><p>動画URLを貼るだけで瞬時に要約</p></div>', unsafe_allow_html=True)
        url = st.text_input("URLをペースト", key="yt_url", label_visibility="collapsed")
        if st.button("動画を解析"):
            if url:
                with st.spinner("Analyzing Video..."):
                    res = YouTubeHandler().get_transcript_from_url(url)
                    st.session_state.current_text = res['text']
                    st.session_state.page = "study"
                    st.rerun()

    with col2:
        st.markdown('<div class="card"><h3>📄 PDF / Text</h3><p>手持ちの資料や文章を学習</p></div>', unsafe_allow_html=True)
        file = st.file_uploader("Upload", type=['pdf'], label_visibility="collapsed")
        if file:
            if st.button("PDFを解析"):
                res = PDFHandler.extract_text_from_bytes(file.read())
                st.session_state.current_text = res['text']
                st.session_state.page = "study"
                st.rerun()

def render_study():
    st.button("← 戻る", on_click=lambda: setattr(st.session_state, 'page', 'home'))
    st.title("📖 学習セッション")
    
    tab1, tab2, tab3 = st.tabs(["要約", "ポイント", "クイズ"])
    client = GeminiClient()
    
    with tab1:
        if st.button("詳細要約を生成"):
            st.write(client.summarize(st.session_state.current_text, '30min'))
    with tab2:
        if st.button("重要語句を抽出"):
            st.write(client.extract_key_points(st.session_state.current_text))
    with tab3:
        if st.button("理解度チェッククイズ"):
            st.write(client.generate_quiz(st.session_state.current_text))

def render_kb():
    st.title("📂 保存済みナレッジ")
    db = Database()
    items = db.get_all_knowledge()
    for item in items:
        with st.expander(item['title']):
            if st.button("この学習を再開", key=item['id']):
                st.session_state.current_text = item['original_text']
                st.session_state.page = "study"
                st.rerun()

# --- 5. ボトムナビゲーション (スマホでも使いやすい！) ---
def bottom_navbar():
    # 実際にはボタンのクリックでsession_stateを書き換える
    cols = st.columns(3)
    if cols[0].button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if cols[1].button("📂 Library", use_container_width=True):
        st.session_state.page = "kb"
        st.rerun()
    if cols[2].button("🧠 Study", use_container_width=True):
        if 'current_text' in st.session_state:
            st.session_state.page = "study"
            st.rerun()
        else:
            st.warning("先にデータを読み込んでください")

def main():
    init_state()
    
    # ページ遷移
    if st.session_state.page == "home":
        render_home()
    elif st.session_state.page == "study":
        render_study()
    elif st.session_state.page == "kb":
        render_kb()
    
    st.write("---")
    bottom_navbar()

if __name__ == "__main__":
    main()
