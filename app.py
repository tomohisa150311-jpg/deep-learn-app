import streamlit as st
import time
from datetime import datetime

# --- 外部モジュール (ご環境に合わせて読み込み) ---
from gemini_client import GeminiClient
from youtube_handler import YouTubeHandler
from pdf_handler import PDFHandler
from database import Database

# --- 1. ページ設定 ---
st.set_page_config(
    page_title="DeepLearn | AI Learning Assistant",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. CSSデザイン ---
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&family=Exo+2:wght@300;700&display=swap');

    /* 全体設定 */
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #ffffff;
        font-family: 'Noto Sans JP', sans-serif;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 固定クレジット (右下に常時表示) */
    .sticky-footer {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        font-family: 'Exo 2', sans-serif;
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.9rem;
        letter-spacing: 2px;
        pointer-events: none; /* 下のボタンの邪魔をしない */
    }

    /* スプラッシュスクリーン */
    .splash-container {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background-color: #000000;
        z-index: 99999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
    }
    
    .splash-logo { font-size: 6rem; animation: pulseLogo 2s infinite ease-in-out; }
    .splash-text {
        font-family: 'Exo 2', sans-serif;
        font-size: 2.5rem;
        margin-top: 20px;
        background: linear-gradient(to right, #fff, #00c6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        opacity: 0;
        animation: fadeInUp 1s ease-out forwards 0.5s;
    }

    @keyframes pulseLogo {
        0% { transform: scale(1); text-shadow: 0 0 0 rgba(0,198,255,0); }
        50% { transform: scale(1.1); text-shadow: 0 0 30px rgba(0,198,255,0.8); }
        100% { transform: scale(1); text-shadow: 0 0 0 rgba(0,198,255,0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ガラスパネル */
    .glass-panel {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    .app-header { text-align: center; padding: 40px 0 20px 0; font-family: 'Exo 2', sans-serif; }
    .app-header h1 {
        font-size: 3.5rem;
        background: linear-gradient(to right, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* ボタン */
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

def get_instruction_suffix(is_easy_mode):
    if is_easy_mode:
        return "\n【重要：出力スタイル】専門用語を使わず、小学生でもわかる例え話で解説してください。絵文字を多用してください。"
    return ""

def main():
    # Session State
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'current_text' not in st.session_state: st.session_state.current_text = None
    if 'active_tool' not in st.session_state: st.session_state.active_tool = None
    if 'result_cache' not in st.session_state: st.session_state.result_cache = None
    if 'history_log' not in st.session_state: st.session_state.history_log = []
    if 'first_load' not in st.session_state: st.session_state.first_load = True

    # スプラッシュ演出
    if st.session_state.first_load:
        placeholder = st.empty()
        placeholder.markdown("""
        <div class="splash-container">
            <div class="splash-logo">💎</div>
            <div class="splash-text">DeepLearn</div>
            <div style="margin-top:20px; color:#666; letter-spacing:3px;">made in tomohisa</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(2.5)
        st.session_state.first_load = False
        placeholder.empty()
        st.rerun()

    # インスタンス化
    client = GeminiClient()
    db = Database()

    # サイドバー
    with st.sidebar:
        st.markdown("### ⚙️ 設定")
        easy_mode = st.toggle("🔰 やさしいモード", value=False)
        st.markdown("---")
        st.markdown("### 📚 最近の履歴")
        for item in reversed(st.session_state.history_log):
            st.caption(f"📅 {item['time']} - {item['url'][:25]}...")

    # メインヘッダー
    st.markdown("""
    <div class="app-header">
        <h1>💎 DeepLearn</h1>
        <p>AI Powered Learning Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    # --- HOME PAGE ---
    if st.session_state.page == "home":
        st.markdown('<div class="glass-panel" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("### 📺 動画で学びを始めよう")
        url = st.text_input("", placeholder="YouTube URLをペースト...")
        if st.button("🚀 解析をスタート", use_container_width=True):
            if url:
                with st.spinner("AIが解析中..."):
                    res = YouTubeHandler().get_transcript_from_url(url)
                    st.session_state.current_text = res['text']
                    st.session_state.history_log.append({"url": url, "time": datetime.now().strftime("%H:%M")})
                    st.session_state.page = "study"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- STUDY PAGE ---
    elif st.session_state.page == "study":
        if st.button("⬅️ TOPに戻る"):
            st.session_state.page = "home"
            st.rerun()

        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button("📝 要約する"): st.session_state.active_tool, st.session_state.result_cache = "sum", None
        if c2.button("🎯 ポイント"): st.session_state.active_tool, st.session_state.result_cache = "point", None
        if c3.button("❓ クイズ作成"): st.session_state.active_tool, st.session_state.result_cache = "quiz", None
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.active_tool:
            if st.session_state.result_cache is None:
                payload = st.session_state.current_text + get_instruction_suffix(easy_mode)
                with st.spinner("AI生成中..."):
                    try:
                        if st.session_state.active_tool == "sum": st.session_state.result_cache = client.summarize(payload, '30min')
                        elif st.session_state.active_tool == "point": st.session_state.result_cache = client.extract_key_points(payload)
                        elif st.session_state.active_tool == "quiz": st.session_state.result_cache = client.generate_quiz(payload)
                    except Exception as e:
                        st.error(f"エラー: {e}")
            
            if st.session_state.result_cache:
                st.markdown(f'<div class="glass-panel"><h3>結果</h3><div>{st.session_state.result_cache}</div></div>', unsafe_allow_html=True)

    # --- 端っこに常時表示するクレジット ---
    st.markdown('<div class="sticky-footer">made in tomohisa</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
