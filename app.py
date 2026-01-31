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

# --- 2. 究極のUIデザイン（1, 2, 3の実装） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@800&family=Inter:wght@400;600&display=swap');

    .stApp { background-color: #05050a; color: #ffffff; }

    /* 1. グラスモフィズム（すりガラス） & 2. ハプティック（押し心地） */
    .stButton>button {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.8), rgba(118, 75, 162, 0.8)) !important;
        backdrop-filter: blur(10px);
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 15px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton>button:active {
        transform: scale(0.95) !important; /* 押し込んだ感覚 */
        filter: brightness(1.2);
    }

    /* 3. スケルトン・ローディング風アニメーション */
    @keyframes pulse {
        0% { background-color: rgba(255,255,255,0.05); }
        50% { background-color: rgba(255,255,255,0.1); }
        100% { background-color: rgba(255,255,255,0.05); }
    }
    .loading-skeleton {
        height: 20px;
        width: 100%;
        border-radius: 10px;
        animation: pulse 1.5s infinite ease-in-out;
        margin-bottom: 10px;
    }

    /* カードデザイン（すりガラス） */
    .source-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border-radius: 24px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* 漆黒オープニング（スマホ最適化） */
    .opening-container {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #000;
        display: flex; align-items: center; justify-content: center;
        z-index: 9999;
        animation: fadeout 0.8s forwards 2.2s;
    }
    @keyframes fadeout { to { opacity: 0; visibility: hidden; } }
    
    .opening-title {
        font-family: 'Exo 2', sans-serif;
        font-size: clamp(2.5rem, 15vw, 6rem);
        color: #fff;
        text-shadow: 0 0 20px #00f2fe;
    }

    /* スマホでのズレを防止するコンテナ */
    .main-wrapper { max-width: 700px; margin: 0 auto; padding-bottom: 100px; }
</style>

<div class="opening-container">
    <div class="opening-title">DEEP LEARN</div>
</div>
""", unsafe_allow_html=True)

# --- 5. AIタイピングエフェクトの実装 ---
def type_text(text):
    placeholder = st.empty()
    full_response = ""
    for char in text:
        full_response += char
        placeholder.markdown(f'<div style="font-size:1.1rem; line-height:1.6;">{full_response}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01) # 速度調整
    placeholder.markdown(f'<div style="font-size:1.1rem; line-height:1.6;">{full_response}</div>', unsafe_allow_html=True)

def main():
    if 'page' not in st.session_state: st.session_state.page = "home"
    
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    if st.session_state.page == "home":
        st.markdown('<div style="text-align:center; padding: 40px 0;"><h1 style="font-family:\'Exo 2\'; font-size:3rem; margin:0;">DEEP LEARN</h1><p style="color:#889;">Next-Gen Learning Assistant</p></div>', unsafe_allow_html=True)
        
        # YouTubeセクション
        with st.container():
            st.markdown('<div class="source-card"><h3>🎬 YouTube</h3><p>動画URLから瞬時に知を抽出</p></div>', unsafe_allow_html=True)
            url = st.text_input("URL", label_visibility="collapsed", placeholder="https://...")
            if st.button("🚀 この動画を学習する"):
                if url:
                    # 3. スケルトン風の待機演出
                    with st.status("AI同期中...", expanded=True) as status:
                        st.markdown('<div class="loading-skeleton"></div><div class="loading-skeleton" style="width:80%"></div>', unsafe_allow_html=True)
                        res = YouTubeHandler().get_transcript_from_url(url)
                        st.session_state.current_text = res['text']
                        status.update(label="同期完了！", state="complete", expanded=False)
                    st.session_state.page = "study"
                    st.rerun()

        # PDFセクション
        with st.container():
            st.markdown('<div class="source-card"><h3>📄 Document</h3><p>PDFファイルを解析</p></div>', unsafe_allow_html=True)
            file = st.file_uploader("Upload", type=['pdf'], label_visibility="collapsed")
            if file and st.button("🚀 PDFを読み込む"):
                res = PDFHandler.extract_text_from_bytes(file.read())
                st.session_state.current_text = res['text']
                st.session_state.page = "study"
                st.rerun()

        st.write("---")
        if st.button("📂 ライブラリを開く"):
            st.session_state.page = "kb"
            st.rerun()

    elif st.session_state.page == "study":
        st.markdown('<h2 style="text-align:center;">📖 Study Session</h2>', unsafe_allow_html=True)
        if st.button("🏠 Home"):
            st.session_state.page = "home"
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["要約", "ポイント", "クイズ"])
        client = GeminiClient()
        
        with tab1:
            if st.button("✨ 要約を生成"):
                res = client.summarize(st.session_state.current_text, '30min')
                # 5. タイピングエフェクトで出力
                type_text(res)
        
        with tab2:
            if st.button("✨ キーポイント抽出"):
                res = client.extract_key_points(st.session_state.current_text)
                type_text(res)

    elif st.session_state.page == "kb":
        st.title("📂 Library")
        if st.button("🏠 Back"):
            st.session_state.page = "home"
            st.rerun()
        # データベース読み込みロジック...

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
