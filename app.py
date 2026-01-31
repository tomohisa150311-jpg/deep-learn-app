"""DeepLearn - 学習支援アプリ メインUI (視認性改善版)"""
import streamlit as st
import time
from gemini_client import GeminiClient
from youtube_handler import YouTubeHandler
from pdf_handler import PDFHandler
from database import Database

# ページ設定
st.set_page_config(
    page_title="DeepLearn",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- スタイリッシュUI & 視認性改善設定 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@700&family=Inter:wght@400;600&display=swap');
    
    :root {
        --primary: #667eea;
        --secondary: #764ba2;
        --accent: #00f2fe;
        --card-bg: #ffffff;
        --card-text: #2d3436; /* 常に濃いグレーで見やすく */
    }

    /* 全体背景 */
    .stApp { font-family: 'Inter', sans-serif; }

    /* --- 起動時アニメーション --- */
    @keyframes splash {
        0% { transform: scale(0.9); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 15px rgba(0,242,254,0.6); }
        50% { text-shadow: 0 0 30px rgba(0,242,254,0.9); }
    }

    .hero-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #764ba2 100%);
        border-radius: 25px;
        padding: 4rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        animation: splash 0.8s ease-out;
        color: white !important; /* ヒーロー内は常に白 */
    }

    .hero-title {
        font-family: 'Exo 2', sans-serif;
        font-size: clamp(2rem, 8vw, 4.5rem);
        background: linear-gradient(to right, #fff, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 3s infinite;
        margin: 0;
    }

    /* --- 視認性改善：白いカードセクション --- */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .feature-card {
        background: var(--card-bg);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.1);
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        transition: 0.3s;
    }

    /* カード内の文字色を強制的に固定 */
    .feature-card h2 { margin: 0; font-size: 2.5rem; }
    .feature-card b { 
        color: #1a1a2e !important; 
        font-size: 1.2rem; 
        display: block; 
        margin: 0.5rem 0;
    }
    .feature-card p { 
        color: #636e72 !important; 
        font-size: 0.9rem;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        border-color: var(--primary);
    }

    /* ボタンの視認性 */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
    }

    /* スマホ対応：サイドバーの余白 */
    @media (max-width: 768px) {
        .st-emotion-cache-16idsys p { font-size: 1.1rem; }
        .hero-container { padding: 2rem 1rem; }
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
    
    defaults = {
        'current_text': None, 'current_title': None,
        'summaries': {}, 'key_points': None, 'quiz': None, 'view_mode': None
    }
    for key, value in defaults.items():
        if key not in st.session_state: st.session_state[key] = value

def sidebar():
    with st.sidebar:
        st.markdown("<h1 style='color:white; font-family:Exo 2;'>🧠 DeepLearn</h1>", unsafe_allow_html=True)
        st.write("---")
        
        mode = st.radio("メニュー", ["🏠 ホーム", "📂 ナレッジベース"])
        st.session_state.view_mode = "knowledge_base" if "📂" in mode else None

        st.markdown("### 📥 コンテンツを追加")
        source_type = st.selectbox("ソースの種類", ["YouTube", "PDF", "Text"])
        
        if source_type == "YouTube":
            url = st.text_input("YouTube URLを入力")
            if st.button("🚀 読み込む") and url:
                with st.spinner("解析中..."):
                    res = YouTubeHandler().get_transcript_from_url(url)
                    st.session_state.current_text = res['text']
                    st.session_state.current_title = "YouTube Video"
                    st.rerun()
        
        elif source_type == "PDF":
            file = st.file_uploader("PDFをアップロード")
            if file and st.button("🚀 解析開始"):
                res = PDFHandler.extract_text_from_bytes(file.read())
                st.session_state.current_text = res['text']
                st.session_state.current_title = file.name
                st.rerun()
        
        else:
            txt = st.text_area("テキストを貼り付け")
            if st.button("🚀 学習開始") and txt:
                st.session_state.current_text = txt
                st.session_state.current_title = "Input Text"
                st.rerun()

def render_landing():
    st.markdown("""
    <div class="hero-container">
        <div class="hero-icon"><img src="https://em-content.zobj.net/source/apple/354/gem-stone_1f48e.png" width="80"></div>
        <h1 class="hero-title">DEEP LEARN</h1>
        <p style="opacity: 0.9; font-size: 1.1rem;">AIがあなたの学習を劇的に効率化する</p>
    </div>
    <div class="feature-grid">
        <div class="feature-card">
            <h2>🎬</h2>
            <b>YouTube動画</b>
            <p>長い動画も一瞬で要約。重要なポイントだけを効率よく吸収。</p>
        </div>
        <div class="feature-card">
            <h2>📄</h2>
            <b>PDF・ドキュメント</b>
            <p>難しい論文や資料も、AIが噛み砕いて解説します。</p>
        </div>
        <div class="feature-card">
            <h2>⚡</h2>
            <b>教えるモード</b>
            <p>理解度を試すクイズを作成。アウトプットで記憶を定着。</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main_content():
    if st.session_state.view_mode == "knowledge_base":
        st.title("📂 ナレッジベース")
        if st.button("← 戻る"):
            st.session_state.view_mode = None
            st.rerun()
        db = Database()
        items = db.get_all_knowledge()
        if not items:
            st.info("保存されたデータはありません。")
        for item in items:
            with st.expander(item['title']):
                st.write(f"保存日: {item['created_at']}")
                if st.button("この学習を再開", key=item['id']):
                    st.session_state.current_text = item['original_text']
                    st.session_state.view_mode = None
                    st.rerun()
        return

    if st.session_state.current_text is None:
        render_landing()
    else:
        st.title(f"📖 {st.session_state.current_title}")
        if st.button("🏠 ホームへ戻る"):
            st.session_state.current_text = None
            st.rerun()
        
        # 既存のタブ・解析ロジック（省略なしで継続）
        tabs = st.tabs(["📝 要約", "🎯 ポイント", "❓ クイズ"])
        client = GeminiClient()
        
        with tabs[0]:
            col1, col2, col3 = st.columns(3)
            if col1.button("⚡ クイック要約"):
                st.write(client.summarize(st.session_state.current_text, '10min'))
            if col2.button("⚡ 標準要約"):
                st.write(client.summarize(st.session_state.current_text, '30min'))
            if col3.button("⚡ 詳細要約"):
                st.write(client.summarize(st.session_state.current_text, '1hour'))

        with tabs[1]:
            if st.button("重要ポイント抽出"):
                st.write(client.extract_key_points(st.session_state.current_text))

        with tabs[2]:
            if st.button("クイズを生成"):
                st.write(client.generate_quiz(st.session_state.current_text))

def main():
    init_session_state()
    sidebar()
    main_content()

if __name__ == "__main__":
    main()
