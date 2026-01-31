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

# --- 2. 究極のモバイルUXデザイン CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@800&family=Inter:wght@400;600&display=swap');

    .stApp { background-color: #05050a; color: #ffffff; }
    
    /* コンテナの幅制限 */
    .main-wrapper { max-width: 500px; margin: 0 auto; padding: 15px; }

    /* タイル型カードボタン */
    .action-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .action-card:active { transform: scale(0.98); background: rgba(255,255,255,0.08); }
    .action-card h3 { margin: 0; font-size: 1.2rem; color: #00f2fe; display: flex; align-items: center; gap: 10px; }
    .action-card p { margin: 8px 0 0 0; font-size: 0.9rem; color: #889; }

    /* 要約表示エリア */
    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        line-height: 1.8;
        font-size: 1.05rem;
        color: #e0e0e0;
        margin-top: 15px;
        white-space: pre-wrap;
    }

    /* クイズ専用スタイル */
    .quiz-box {
        background: rgba(102, 126, 234, 0.05);
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
    }

    /* Streamlit標準要素のオーバーライド */
    .stButton>button {
        border-radius: 16px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    /* 漆黒オープニング */
    .opening-container {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: #000; display: flex; align-items: center; justify-content: center;
        z-index: 9999; animation: fadeout 0.8s forwards 1.5s;
    }
    @keyframes fadeout { to { opacity: 0; visibility: hidden; } }
    .opening-title { font-family: 'Exo 2'; font-size: 3rem; color: #fff; text-shadow: 0 0 20px #00f2fe; letter-spacing: 5px; }

    hr { opacity: 0.1; margin: 2rem 0; }
</style>

<div class="opening-container">
    <div class="opening-title">DEEP LEARN</div>
</div>
""", unsafe_allow_html=True)

def type_display(text, title="Result"):
    if not text: return
    st.markdown(f"### {title}")
    placeholder = st.empty()
    full_response = ""
    for char in text:
        full_response += char
        placeholder.markdown(f'<div class="glass-panel">{full_response}▌</div>', unsafe_allow_html=True)
        time.sleep(0.003)
    placeholder.markdown(f'<div class="glass-panel">{full_response}</div>', unsafe_allow_html=True)

def main():
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'current_text' not in st.session_state: st.session_state.current_text = None
    if 'current_title' not in st.session_state: st.session_state.current_title = ""
    if 'active_tool' not in st.session_state: st.session_state.active_tool = None

    client = GeminiClient()
    db = Database()
    
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    # --- HOME: インプットとライブラリへの導線 ---
    if st.session_state.page == "home":
        st.markdown('<h1 style="text-align:center; font-family:\'Exo 2\'; font-size:2.5rem; margin-bottom:1.5rem;">💎</h1>', unsafe_allow_html=True)
        
        # インプットエリア
        st.markdown("""
        <div style="background:rgba(255,255,255,0.02); padding:20px; border-radius:24px; border:1px solid rgba(255,255,255,0.05); margin-bottom:2rem;">
            <p style="text-align:center; color:#889; margin-bottom:15px;">学習を開始するソースを入力</p>
        """, unsafe_allow_html=True)
        url = st.text_input("URL", label_visibility="collapsed", placeholder="YouTube URLをペースト...")
        
        if st.button("🚀 解析をはじめる"):
            if url:
                with st.status("🧠 思考を同期中...", expanded=False):
                    res = YouTubeHandler().get_transcript_from_url(url)
                    st.session_state.current_text = res['text']
                    st.session_state.current_title = "新規学習セッション"
                st.session_state.page = "study"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 📂 続きから学ぶ")
        items = db.get_all_knowledge()
        if not items:
            st.markdown('<p style="color:#556; font-size:0.9rem;">保存されたナレッジはありません</p>', unsafe_allow_html=True)
        else:
            for item in items[:3]: # 直近3つ表示
                if st.button(f"📖 {item['title'][:20]}...", key=item['id']):
                    st.session_state.current_text = item['original_text']
                    st.session_state.current_title = item['title']
                    st.session_state.page = "study"
                    st.rerun()
        
        if st.button("すべてのライブラリを表示 →", type="secondary"):
            st.session_state.page = "library"
            st.rerun()

    # --- STUDY: 直感的なツール選択 ---
    elif st.session_state.page == "study":
        st.markdown(f'<p style="color:#00f2fe; font-weight:600; text-align:center; margin:0;">STUDY SESSION</p>', unsafe_allow_html=True)
        st.markdown(f'<h2 style="text-align:center; margin-top:5px; font-size:1.5rem;">{st.session_state.current_title}</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ 戻る"):
                st.session_state.page = "home"
                st.session_state.active_tool = None
                st.rerun()
        with col2:
            if st.button("💾 保存"):
                db.save_knowledge(st.session_state.current_title, st.session_state.current_text)
                st.toast("ライブラリに保存しました！")

        st.markdown("---")

        # ツール選択タイル
        if not st.session_state.active_tool:
            if st.button("⚡ 5分でわかる要約"):
                st.session_state.active_tool = "summarize"
                st.rerun()
            if st.button("🎯 重要キーポイント"):
                st.session_state.active_tool = "points"
                st.rerun()
            if st.button("❓ 理解度テスト"):
                st.session_state.active_tool = "quiz"
                st.rerun()
        
        # ツール実行結果
        if st.session_state.active_tool == "summarize":
            res = client.summarize(st.session_state.current_text, '30min')
            type_display(res, "Quick Summary")
            if st.button("🔄 他のツールを使う"):
                st.session_state.active_tool = None
                st.rerun()

        elif st.session_state.active_tool == "points":
            res = client.extract_key_points(st.session_state.current_text)
            type_display(res, "Key Insights")
            if st.button("🔄 他のツールを使う"):
                st.session_state.active_tool = None
                st.rerun()

        elif st.session_state.active_tool == "quiz":
            with st.spinner("クイズを生成中..."):
                res = client.generate_quiz(st.session_state.current_text)
            st.markdown("### ❓ Challenge")
            st.markdown(f'<div class="quiz-box">{res}</div>', unsafe_allow_html=True)
            with st.expander("👁️ 正解を表示"):
                st.write("解説を確認して知識を定着させましょう。")
            if st.button("🔄 他のツールを使う"):
                st.session_state.active_tool = None
                st.rerun()

    # --- LIBRARY ---
    elif st.session_state.page == "library":
        st.markdown('<h2>📂 Library</h2>', unsafe_allow_html=True)
        if st.button("🏠 ホームへ戻る"):
            st.session_state.page = "home"
            st.rerun()
        
        for item in db.get_all_knowledge():
            with st.container():
                st.markdown(f"""
                <div class="action-card">
                    <small style="color:#889;">{item['created_at']}</small>
                    <h3>📖 {item['title']}</h3>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                if c1.button("学習する", key=f"l_{item['id']}"):
                    st.session_state.current_text = item['original_text']
                    st.session_state.current_title = item['title']
                    st.session_state.page = "study"
                    st.rerun()
                if c2.button("削除", key=f"d_{item['id']}"):
                    db.delete_knowledge(item['id'])
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
