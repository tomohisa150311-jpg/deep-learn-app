import streamlit as st
import os
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

# --- 2. CSS（フリーズ防止 & アニメーション） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@800&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #05050a; color: #ffffff; }
    .main-wrapper { max-width: 500px; margin: 0 auto; padding: 15px; }

    /* フェードイン演出（フリーズの原因になるループの代わり） */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        line-height: 1.8;
        font-size: 1.05rem;
        animation: fadeIn 0.5s ease-out forwards;
        white-space: pre-wrap;
    }

    /* ボタンデザイン */
    .stButton>button {
        border-radius: 16px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        transition: 0.2s;
    }
</style>
""", unsafe_allow_html=True)

def main():
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'current_text' not in st.session_state: st.session_state.current_text = None
    if 'active_tool' not in st.session_state: st.session_state.active_tool = None
    if 'result_cache' not in st.session_state: st.session_state.result_cache = None

    client = GeminiClient()
    db = Database()
    
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    # --- HOME PAGE ---
    if st.session_state.page == "home":
        st.markdown('<h1 style="text-align:center; font-family:\'Exo 2\';">💎 DeepLearn</h1>', unsafe_allow_html=True)
        url = st.text_input("YouTube URL", placeholder="URLをペースト...")
        if st.button("🚀 解析開始"):
            if url:
                with st.spinner("AI同期中..."):
                    res = YouTubeHandler().get_transcript_from_url(url)
                    st.session_state.current_text = res['text']
                st.session_state.page = "study"
                st.rerun()

    # --- STUDY PAGE ---
    elif st.session_state.page == "study":
        col1, col2 = st.columns([1,1])
        if col1.button("⬅️ Home"):
            st.session_state.page = "home"
            st.session_state.active_tool = None
            st.session_state.result_cache = None
            st.rerun()
        if col2.button("💾 保存"):
            db.save_knowledge("新規学習", st.session_state.current_text)
            st.toast("保存完了")

        # ツール選択
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        
        # フリーズ回避：ボタン押下時に直接生成せず、フラグを立ててから次のループで描画
        if c1.button("✨要約"):
            st.session_state.active_tool = "sum"
            st.session_state.result_cache = None
        if c2.button("🎯重点"):
            st.session_state.active_tool = "point"
            st.session_state.result_cache = None
        if c3.button("❓テスト"):
            st.session_state.active_tool = "quiz"
            st.session_state.result_cache = None

        # 結果表示エリア
        if st.session_state.active_tool:
            if st.session_state.result_cache is None:
                with st.spinner("Gemini 3 Flash 思考中..."):
                    if st.session_state.active_tool == "sum":
                        st.session_state.result_cache = client.summarize(st.session_state.current_text, '30min')
                    elif st.session_state.active_tool == "point":
                        st.session_state.result_cache = client.extract_key_points(st.session_state.current_text)
                    elif st.session_state.active_tool == "quiz":
                        st.session_state.result_cache = client.generate_quiz(st.session_state.current_text)
            
            # キャッシュされた結果を表示（ここでループを使わない！）
            st.markdown(f'<div class="glass-panel">{st.session_state.result_cache}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
