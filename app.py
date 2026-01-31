import streamlit as st
import time
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

# --- 2. 究極のUIデザイン & 漆黒アニメーション ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@800&family=Inter:wght@400;600&display=swap');

    /* ダークテーマの徹底 */
    .stApp { background-color: #05050a; color: #ffffff; }

    /* すりガラス & ハプティック・ボタン */
    .stButton>button {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.7), rgba(118, 75, 162, 0.7)) !important;
        backdrop-filter: blur(12px);
        color: white !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 16px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .stButton>button:active {
        transform: scale(0.96) !important;
        filter: brightness(1.3);
    }

    /* スケルトン・ローディング */
    @keyframes pulse {
        0% { background-color: rgba(255,255,255,0.03); }
        50% { background-color: rgba(255,255,255,0.08); }
        100% { background-color: rgba(255,255,255,0.03); }
    }
    .loading-skeleton {
        height: 24px;
        width: 100%;
        border-radius: 12px;
        animation: pulse 1.5s infinite ease-in-out;
        margin-bottom: 12px;
    }

    /* ソースカード（すりガラス） */
    .source-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 1.8rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    .source-card h3 { color: #00f2fe !important; margin:0; font-size: 1.4rem; }
    .source-card p { color: #aaa !important; font-size: 0.9rem; margin-top: 5px; }

    /* 漆黒オープニング */
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
        font-size: clamp(2.5rem, 12vw, 5.5rem);
        color: #fff;
        font-weight: 800;
        letter-spacing: 0.2em;
        text-shadow: 0 0 30px rgba(0,242,254,0.8);
        text-align: center;
    }

    /* メインコンテンツ幅制限 */
    .main-wrapper { max-width: 750px; margin: 0 auto; padding: 20px; padding-bottom: 120px; }

    /* タイピングエフェクト用 */
    .typing-box {
        font-size: 1.1rem;
        line-height: 1.7;
        color: #e0e0e0;
        background: rgba(255,255,255,0.02);
        padding: 20px;
        border-radius: 15px;
        border-left: 3px solid #667eea;
    }
</style>

<div class="opening-container">
    <div class="opening-title">DEEP LEARN</div>
</div>
""", unsafe_allow_html=True)

# --- 3. AIタイピングエフェクト ---
def type_text(text):
    if not text: return
    placeholder = st.empty()
    full_response = ""
    for char in text:
        full_response += char
        placeholder.markdown(f'<div class="typing-box">{full_response}▌</div>', unsafe_allow_html=True)
        time.sleep(0.008) # 3-Flashの速さに合わせた超高速表示
    placeholder.markdown(f'<div class="typing-box">{full_response}</div>', unsafe_allow_html=True)

def main():
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'current_text' not in st.session_state: st.session_state.current_text = None
    
    client = GeminiClient() # ここで gemini-3-flash-preview が初期化される
    
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    if st.session_state.page == "home":
        st.markdown('<div style="text-align:center; padding: 30px 0;"><h1 style="font-family:\'Exo 2\'; font-size:clamp(2rem, 8vw, 3.5rem); margin:0; background: linear-gradient(to right, #00f2fe, #fff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">DEEP LEARN</h1><p style="color:#667; letter-spacing: 2px;">POWERED BY GEMINI 3 FLASH</p></div>', unsafe_allow_html=True)
        
        # YouTubeセクション
        with st.container():
            st.markdown('<div class="source-card"><h3>🎬 YouTube</h3><p>動画を瞬時にナレッジへ変換</p></div>', unsafe_allow_html=True)
            url = st.text_input("URL", label_visibility="collapsed", placeholder="https://youtube.com/watch?v=...")
            if st.button("🚀 解析を開始する"):
                if url:
                    with st.status("🧠 AI同期中...", expanded=True) as status:
                        st.markdown('<div class="loading-skeleton"></div><div class="loading-skeleton" style="width:80%"></div>', unsafe_allow_html=True)
                        try:
                            res = YouTubeHandler().get_transcript_from_url(url)
                            st.session_state.current_text = res['text']
                            status.update(label="同期完了！", state="complete", expanded=False)
                            st.session_state.page = "study"
                            st.rerun()
                        except Exception as e:
                            status.update(label="エラー発生", state="error")
                            st.error(f"動画の取得に失敗しました: {e}")

        # PDFセクション
        with st.container():
            st.markdown('<div class="source-card"><h3>📄 Document</h3><p>PDF資料から重要情報を抽出</p></div>', unsafe_allow_html=True)
            file = st.file_uploader("Upload", type=['pdf'], label_visibility="collapsed")
            if file and st.button("🚀 ファイルを読み込む"):
                try:
                    res = PDFHandler.extract_text_from_bytes(file.read())
                    st.session_state.current_text = res['text']
                    st.session_state.page = "study"
                    st.rerun()
                except Exception as e:
                    st.error(f"PDFの解析に失敗しました: {e}")

        st.write("---")
        if st.button("📂 保存済みライブラリ"):
            st.session_state.page = "kb"
            st.rerun()

    elif st.session_state.page == "study":
        st.markdown('<h2 style="text-align:center; font-family:\'Exo 2\';">📖 Study Session</h2>', unsafe_allow_html=True)
        if st.button("🏠 ホームへ戻る"):
            st.session_state.page = "home"
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["✨ 要約", "🎯 ポイント", "❓ クイズ"])
        
        with tab1:
            if st.button("⚡ 高精度要約を生成"):
                with st.spinner("Gemini 3 Flash が思考中..."):
                    res = client.summarize(st.session_state.current_text, '30min')
                    type_text(res)
        
        with tab2:
            if st.button("⚡ キーポイントを抽出"):
                with st.spinner("分析中..."):
                    res = client.extract_key_points(st.session_state.current_text)
                    type_text(res)
        
        with tab3:
            if st.button("⚡ クイズを自動生成"):
                with st.spinner("問題を作成中..."):
                    res = client.generate_quiz(st.session_state.current_text)
                    type_text(res)

    elif st.session_state.page == "kb":
        st.title("📂 Library")
        if st.button("🏠 戻る"):
            st.session_state.page = "home"
            st.rerun()
        # データベース読み出しロジック（Databaseクラスの実装に依存）
        db = Database()
        items = db.get_all_knowledge()
        if not items:
            st.info("保存されたナレッジはありません。")
        for item in items:
            with st.expander(item['title']):
                if st.button("この学習を再開", key=item['id']):
                    st.session_state.current_text = item['original_text']
                    st.session_state.page = "study"
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
