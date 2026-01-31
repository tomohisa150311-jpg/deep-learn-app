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

# --- 2. CSSデザイン (Glassmorphism & Animation & Splash) ---
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

    /* --- スプラッシュスクリーン (オープニング) --- */
    .splash-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: #000000;
        z-index: 99999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
    }
    
    .splash-logo {
        font-size: 6rem;
        animation: pulseLogo 2s infinite ease-in-out;
    }
    
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

    .splash-credit {
        position: absolute;
        bottom: 50px;
        font-family: 'Exo 2', sans-serif;
        font-size: 1rem;
        letter-spacing: 3px;
        color: #666;
        opacity: 0;
        animation: fadeInUp 1s ease-out forwards 1.0s;
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

    /* タイトルスタイル */
    .app-header {
        text-align: center;
        padding: 40px 0 20px 0;
        font-family: 'Exo 2', sans-serif;
        text-shadow: 0 0 20px rgba(0, 198, 255, 0.5);
    }
    .app-header h1 {
        font-size: 3.5rem;
        margin-bottom: 0;
        background: linear-gradient(to right, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .app-header p {
        font-size: 1rem;
        color: #aab;
        letter-spacing: 2px;
    }

    /* ガラスパネル (共通カード) */
    .glass-panel {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .glass-panel:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.2);
    }

    /* 結果表示エリア */
    .result-content {
        line-height: 1.8;
        font-size: 1.05rem;
        white-space: pre-wrap;
    }
    
    /* ボタン */
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        transition: all 0.3s !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%) !important;
        border-color: #00c6ff !important;
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(0, 198, 255, 0.4) !important;
    }

    /* 入力フォーム */
    .stTextInput>div>div>input {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        padding: 10px 15px !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #00c6ff !important;
        box-shadow: 0 0 10px rgba(0, 198, 255, 0.2) !important;
    }
    
    /* ユーティリティ */
    .badge-easy {
        display: inline-block;
        background: #00b09b;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 10px;
        box-shadow: 0 0 10px rgba(0, 176, 155, 0.4);
    }
    
    /* クレジット footer */
    .footer-credit {
        text-align: center;
        font-family: 'Exo 2', sans-serif;
        color: rgba(255,255,255,0.3);
        font-size: 0.8rem;
        margin-top: 30px;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ヘルパー関数 ---
def get_instruction_suffix(is_easy_mode):
    if is_easy_mode:
        return """
        \n【重要：出力スタイルについて】
        ・デジタルに詳しくない人や、小学生でも理解できる言葉を使ってください。
        ・専門用語は一切使わず、日常的な例え話に置き換えてください。
        ・親しみやすいトーンで、絵文字（💎, ✨, 🚀など）を適度に使ってください。
        ・箇条書きを活用して、視覚的にわかりやすくしてください。
        """
    return ""

def main():
    # --- Session State 初期化 ---
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'current_text' not in st.session_state: st.session_state.current_text = None
    if 'active_tool' not in st.session_state: st.session_state.active_tool = None
    if 'result_cache' not in st.session_state: st.session_state.result_cache = None
    if 'last_easy_mode' not in st.session_state: st.session_state.last_easy_mode = False
    
    # 履歴管理用のリスト
    if 'history_log' not in st.session_state: st.session_state.history_log = []
    
    # オープニングアニメーション制御フラグ
    if 'first_load' not in st.session_state: st.session_state.first_load = True

    # --- オープニングアニメーション (初回のみ実行) ---
    if st.session_state.first_load:
        placeholder = st.empty()
        # HTML/CSSでフルスクリーンオーバーレイを描画
        placeholder.markdown("""
        <div class="splash-container">
            <div class="splash-logo">💎</div>
            <div class="splash-text">DeepLearn</div>
            <div class="splash-credit">made in tomohisa</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 疑似ロード時間
        time.sleep(2.5)
        
        # 状態更新 & リロードしてアプリ画面へ
        st.session_state.first_load = False
        placeholder.empty()
        st.rerun()

    # --- インスタンス化 ---
    client = GeminiClient()
    db = Database()

    # --- サイドバー設定 ---
    with st.sidebar:
        st.markdown("### ⚙️ 設定")
        easy_mode = st.toggle("🔰 やさしいモード", value=False, help="ONにすると、専門用語を使わず、誰にでもわかる言葉で解説します。")
        
        if easy_mode != st.session_state.last_easy_mode:
            st.session_state.result_cache = None
            st.session_state.last_easy_mode = easy_mode
            st.rerun()

        st.markdown("---")
        st.markdown("### 📚 最近の履歴")
        
        # セッション履歴の表示
        if st.session_state.history_log:
            for item in reversed(st.session_state.history_log):
                with st.expander(f"📅 {item['time']}", expanded=False):
                    st.caption(f"URL: {item['url']}")
                    st.info("保存済み")
        else:
            st.caption("まだ履歴はありません")

        # Tomohisa Credit (Sidebar Bottom)
        st.markdown("""
        <div class="footer-credit">
            made in tomohisa
        </div>
        """, unsafe_allow_html=True)

    # --- メインエリア ---
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
        st.markdown("YouTubeのURLを入力するだけで、AIが内容を瞬時に解析・要約します。")
        
        url = st.text_input("", placeholder="ここにYouTubeのURLをペーストしてください...", label_visibility="collapsed")
        
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            if st.button("🚀 解析をスタート", use_container_width=True):
                if url:
                    with st.spinner("🧠 AIが動画を視聴中... 文字起こしを取得しています"):
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        try:
                            # 実際の解析処理
                            res = YouTubeHandler().get_transcript_from_url(url)
                            st.session_state.current_text = res['text']
                            
                            # 履歴に追加
                            timestamp = datetime.now().strftime("%H:%M")
                            st.session_state.history_log.append({"url": url, "time": timestamp})
                            
                            st.session_state.page = "study"
                            st.rerun()
                        except Exception as e:
                            st.error(f"エラーが発生しました: {e}")
                else:
                    st.warning("URLを入力してください")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- STUDY PAGE ---
    elif st.session_state.page == "study":
        
        # ナビゲーションバー
        c_nav1, c_nav2 = st.columns([1, 5])
        with c_nav1:
            if st.button("⬅️ TOP", use_container_width=True):
                st.session_state.page = "home"
                st.session_state.active_tool = None
                st.session_state.result_cache = None
                st.rerun()
        
        with c_nav2:
            mode_badge = '<span class="badge-easy">🔰 やさしいモード ON</span>' if easy_mode else ""
            st.markdown(f'<div style="text-align:right; padding-top:5px;">{mode_badge}</div>', unsafe_allow_html=True)

        # メインコントロール
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown("###
