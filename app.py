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
    initial_sidebar_state="collapsed",
)

# --- 2. 漆黒の演出 & スマホ最適化 CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@800&family=Inter:wght@400;600&display=swap');

    /* 全体背景：没入感のあるダークネイビー */
    .stApp {
        background-color: #05050a;
        color: #ffffff;
    }

    /* --- 漆黒のオープニングアニメーション (スマホ対応版) --- */
    @keyframes deep-flash {
        0% { opacity: 0; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    @keyframes text-glow {
        0%, 100% { text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe; }
        50% { text-shadow: 0 0 30px #764ba2, 0 0 50px #764ba2; }
    }

    .opening-container {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #000000;
        display: flex; align-items: center; justify-content: center;
        z-index: 9999;
        animation: fadeout 0.8s forwards 1.8s;
    }
    @keyframes fadeout { to { opacity: 0; visibility: hidden; } }

    .opening-title {
        font-family: 'Exo 2', sans-serif;
        font-size: clamp(2.5rem, 12vw, 5rem); /* スマホで絶対はみ出さないサイズ */
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        animation: deep-flash 1s ease-out, text-glow 2s infinite;
    }

    /* --- メインコンテンツ：スマホ最適化レイアウト --- */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 10px;
    }

    .hero-box {
        background: linear-gradient(145deg, #101020, #201040);
        border-radius: 25px;
        padding: 3rem 1rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        margin-top: 20px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .hero-title {
        font-family: 'Exo 2', sans-serif;
        font-size: clamp(2rem, 10vw, 4rem);
        background: linear-gradient(to right, #00f2fe, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .hero-subtitle {
        color: #b0b0c0 !important;
        font-size: clamp(0.9rem, 4vw, 1.1rem);
        margin-top: 10px;
    }

    /* タイルボタン形式（直感的なインターフェース） */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-bottom: 10px;
        transition: 0.3s;
    }
    
    .stButton>button:active {
        transform: scale(0.95);
    }

    /* カードデザイン */
    .source-card {
        background: #161625;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 5px solid #00f2fe;
    }
    .source-card h3 { color: #00f2fe !important; font-size: 1.3rem; margin-bottom: 5px; }
    .source-card p { color: #999 !important; font-size: 0.85rem; }

    /* 水平線の色 */
    hr { border-color: rgba(255,255,255,0.1) !important; }

    /* スマホ版ボトムナビのモック */
    .nav-wrapper {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background: #0a0a15;
        padding: 10px 0;
        z-index: 100;
        border-top: 1px solid #333;
    }
</style>

<div class="opening-container">
    <div class="opening-title">DEEP LEARN</div>
</div>
""", unsafe_allow_html=True)

# 3. メインロジック
def main():
    if 'page' not in st.session_state: st.session_state.page = "home"

    # 全体をコンテナで包んでスマホの端っこ問題を解消
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)

        if st.session_state.page == "home":
            # ヒーローセクション
            st.markdown("""
            <div class="hero-box">
                <h1 class="hero-title">DEEP LEARN</h1>
                <p class="hero-subtitle">AIがあなたの学習を劇的に効率化する</p>
            </div>
            """, unsafe_allow_html=True)

            # コンテンツ追加セクション（直感的なタイル形式）
            st.markdown('<div class="source-card"><h3>🎬 YouTube</h3><p>動画URLを貼り付けて解析</p></div>', unsafe_allow_html=True)
            yt_url = st.text_input("URLを入力", key="yt_url", label_visibility="collapsed", placeholder="https://youtube.com/...")
            if st.button("🚀 動画を読み込む"):
                if yt_url:
                    with st.spinner("AI解析中..."):
                        res = YouTubeHandler().get_transcript_from_url(yt_url)
                        st.session_state.current_text = res['text']
                        st.session_state.page = "study"
                        st.rerun()

            st.markdown('<div class="source-card"><h3>📄 PDF / Text</h3><p>ドキュメントや文章を読み込む</p></div>', unsafe_allow_html=True)
            file = st.file_uploader("Upload", type=['pdf'], label_visibility="collapsed")
            if file and st.button("🚀 PDFを読み込む"):
                res = PDFHandler.extract_text_from_bytes(file.read())
                st.session_state.current_text = res['text']
                st.session_state.page = "study"
                st.rerun()

            st.write("---")
            if st.button("📂 保存した学習を見る"):
                st.session_state.page = "kb"
                st.rerun()

        elif st.session_state.page == "study":
            st.markdown('<h2 style="text-align:center;">📖 学習セッション</h2>', unsafe_allow_html=True)
            if st.button("🏠 ホームに戻る"):
                st.session_state.page = "home"
                st.rerun()

            tab1, tab2, tab3 = st.tabs(["要約", "ポイント", "クイズ"])
            client = GeminiClient()
            with tab1:
                if st.button("AI要約を実行"):
                    st.write(client.summarize(st.session_state.current_text, '30min'))
            with tab2:
                if st.button("重要語句を抽出"):
                    st.write(client.extract_key_points(st.session_state.current_text))
            with tab3:
                if st.button("理解度チェック"):
                    st.write(client.generate_quiz(st.session_state.current_text))

        elif st.session_state.page == "kb":
            st.title("📂 Library")
            if st.button("🏠 戻る"):
                st.session_state.page = "home"
                st.rerun()
            db = Database()
            for item in db.get_all_knowledge():
                with st.expander(item['title']):
                    if st.button("再開", key=item['id']):
                        st.session_state.current_text = item['original_text']
                        st.session_state.page = "study"
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
