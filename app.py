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

# --- 2. CSSデザイン ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@800&family=Inter:wght@400;600&display=swap');

    .stApp { background-color: #05050a; color: #ffffff; }

    .summary-container {
        font-size: 1.05rem; line-height: 1.8; color: #e0e0e0;
        background: rgba(255,255,255,0.03); padding: 20px;
        border-radius: 18px; border-left: 4px solid #00f2fe;
        margin-bottom: 20px; white-space: pre-wrap;
    }

    /* ライブラリカードのデザイン */
    .kb-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px; padding: 15px;
        margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);
        transition: 0.3s;
    }
    .kb-card:hover { border-color: #00f2fe; background: rgba(0, 242, 254, 0.05); }

    .stButton>button {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.7), rgba(118, 75, 162, 0.7)) !important;
        backdrop-filter: blur(12px); color: white !important;
        border-radius: 16px !important; transition: all 0.2s !important;
        width: 100%;
    }
    .stButton>button:active { transform: scale(0.96) !important; }

    .opening-container {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: #000; display: flex; align-items: center; justify-content: center;
        z-index: 9999; animation: fadeout 0.8s forwards 2.2s;
    }
    @keyframes fadeout { to { opacity: 0; visibility: hidden; } }
    .opening-title { font-family: 'Exo 2'; font-size: clamp(2.5rem, 12vw, 5.5rem); color: #fff; text-shadow: 0 0 30px #00f2fe; }
    .main-wrapper { max-width: 700px; margin: 0 auto; padding: 20px; padding-bottom: 120px; }
</style>

<div class="opening-container">
    <div class="opening-title">DEEP LEARN</div>
</div>
""", unsafe_allow_html=True)

def type_summary(text):
    if not text: return
    placeholder = st.empty()
    full_response = ""
    for char in text:
        full_response += char
        placeholder.markdown(f'<div class="summary-container">{full_response}▌</div>', unsafe_allow_html=True)
        time.sleep(0.005)
    placeholder.markdown(f'<div class="summary-container">{full_response}</div>', unsafe_allow_html=True)

def main():
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'current_text' not in st.session_state: st.session_state.current_text = None
    if 'current_title' not in st.session_state: st.session_state.current_title = ""
    
    client = GeminiClient()
    db = Database()
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    # --- HOME PAGE ---
    if st.session_state.page == "home":
        st.markdown('<div style="text-align:center; padding: 30px 0;"><h1 style="font-family:\'Exo 2\'; font-size:3rem; margin:0; background: linear-gradient(to right, #00f2fe, #fff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">DEEP LEARN</h1></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 新しく学習する"):
                st.session_state.input_mode = True
        with col2:
            if st.button("📂 ライブラリを見る"):
                st.session_state.page = "library"
                st.rerun()

        if st.session_state.get('input_mode'):
            st.markdown("---")
            url = st.text_input("YouTube URL", placeholder="https://youtube.com/...")
            if st.button("🎬 動画を解析"):
                if url:
                    with st.status("🧠 AI同期中..."):
                        res = YouTubeHandler().get_transcript_from_url(url)
                        st.session_state.current_text = res['text']
                        st.session_state.current_title = "YouTube Content"
                    st.session_state.page = "study"
                    st.rerun()

    # --- STUDY PAGE ---
    elif st.session_state.page == "study":
        st.markdown(f'<h3 style="text-align:center;">📖 {st.session_state.current_title}</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Home"):
                st.session_state.page = "home"
                st.rerun()
        with col2:
            if st.button("💾 この学習を保存"):
                db.save_knowledge(st.session_state.current_title, st.session_state.current_text)
                st.toast("ライブラリに保存しました！", icon="✅")

        tab1, tab2, tab3 = st.tabs(["✨ 要約", "🎯 ポイント", "❓ クイズ"])
        
        with tab1:
            if st.button("⚡ 5分で読破する要約"):
                res = client.summarize(st.session_state.current_text, '30min')
                type_summary(res)
        
        with tab2:
            if st.button("⚡ 重要語句を抽出"):
                res = client.extract_key_points(st.session_state.current_text)
                type_summary(res)
        
        with tab3:
            if st.button("⚡ クイズを生成"):
                with st.spinner("思考中..."):
                    quiz_data = client.generate_quiz(st.session_state.current_text)
                    st.session_state.last_quiz = quiz_data
            if 'last_quiz' in st.session_state:
                st.markdown(f'<div class="summary-container">{st.session_state.last_quiz}</div>', unsafe_allow_html=True)
                with st.expander("👁️ 正解・解説を確認する"):
                    st.info("回答は上記テキスト内に含まれています。")

    # --- LIBRARY PAGE (振り返り) ---
    elif st.session_state.page == "library":
        st.markdown('<h2 style="text-align:center;">📂 ライブラリ</h2>', unsafe_allow_html=True)
        if st.button("🏠 Homeへ戻る"):
            st.session_state.page = "home"
            st.rerun()
        
        items = db.get_all_knowledge()
        if not items:
            st.info("まだ保存されたナレッジがありません。")
        
        for item in items:
            with st.container():
                st.markdown(f"""
                <div class="kb-card">
                    <small style="color:#00f2fe;">{item['created_at']}</small>
                    <h4 style="margin:5px 0;">{item['title']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                if c1.button("🧠 復習する", key=f"rev_{item['id']}"):
                    st.session_state.current_text = item['original_text']
                    st.session_state.current_title = item['title']
                    st.session_state.page = "study"
                    st.rerun()
                if c2.button("🗑️ 削除", key=f"del_{item['id']}"):
                    db.delete_knowledge(item['id'])
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
