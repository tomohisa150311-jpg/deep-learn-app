"""DeepLearn - 学習支援アプリ メインUI"""
import streamlit as st
import urllib.parse
from gemini_client import GeminiClient
from youtube_handler import YouTubeHandler
from pdf_handler import PDFHandler
from database import Database

# ページ設定
st.set_page_config(
    page_title="DeepLearn - 学習支援アプリ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# モダンなカスタムCSS & スマホ最適化
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ベーススタイル */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ヒーローセクション */
    .hero-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 24px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        animation: fadeInUp 0.8s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .hero-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: rgba(255,255,255,0.9);
        margin-bottom: 1.5rem;
        font-weight: 300;
    }

    /* スマホ最適化 */
    @media (max-width: 640px) {
        .hero-title { font-size: 2.2rem !important; }
        .hero-subtitle { font-size: 1rem !important; }
        .hero-stats { flex-direction: column; gap: 1rem !important; }
        .feature-grid { grid-template-columns: 1fr !important; }
        .stButton>button { width: 100% !important; height: 3.5rem !important; font-size: 1.1rem !important; }
    }
    
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 2rem;
    }
    
    .stat-item { text-align: center; }
    .stat-number { font-size: 2rem; font-weight: 700; color: white; }
    .stat-label { font-size: 0.9rem; color: rgba(255,255,255,0.8); }
    
    /* フィーチャーカード */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border: 1px solid #f0f0f0;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
    }

    /* サイドバーボタン */
    section[data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """セッション状態の初期化"""
    defaults = {
        'current_text': None,
        'current_title': None,
        'current_source_type': None,
        'current_source_url': None,
        'summaries': {},
        'key_points': None,
        'quiz': None,
        'teach_explanation': None,
        'view_mode': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_gemini_client():
    """Geminiクライアントを取得"""
    if 'gemini_client' not in st.session_state:
        try:
            st.session_state.gemini_client = GeminiClient()
        except ValueError as e:
            st.error(str(e))
            st.stop()
    return st.session_state.gemini_client


def get_database():
    """データベースを取得"""
    if 'database' not in st.session_state:
        st.session_state.database = Database()
    return st.session_state.database


def render_share_buttons(title: str, text: str):
    """共有ボタンを描画"""
    share_text = f"📚 {title}\n\n{text[:200]}...\n\n#DeepLearn で学習中！"
    encoded_text = urllib.parse.quote(share_text)
    
    twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
    line_url = f"https://social-plugins.line.me/lineit/share?url=&text={encoded_text}"
    
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-top: 15px;">
        <a href="{twitter_url}" target="_blank" style="background:#1DA1F2; color:white; padding:10px 20px; border-radius:50px; text-decoration:none;">🐦 Twitter</a>
        <a href="{line_url}" target="_blank" style="background:#00B900; color:white; padding:10px 20px; border-radius:50px; text-decoration:none;">💬 LINE</a>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📋 クリップボードにコピー", key=f"copy_{hash(text[:50])}"):
        st.code(share_text, language=None)
        st.success("コピーしてください！")


def sidebar():
    """サイドバーの描画"""
    with st.sidebar:
        st.markdown("## 🧠 DeepLearn")
        st.markdown("---")
        st.markdown("### 📥 コンテンツを追加")
        
        source_type = st.selectbox(
            "種類を選択",
            ["YouTube動画", "PDFファイル", "テキスト入力"],
            key="source_type_select"
        )
        
        if source_type == "YouTube動画":
            youtube_url = st.text_input("YouTube URL", key="youtube_url")
            if st.button("🎬 動画を読み込む", use_container_width=True):
                if youtube_url:
                    with st.spinner("取得中..."):
                        try:
                            handler = YouTubeHandler()
                            result = handler.get_transcript_from_url(youtube_url)
                            st.session_state.current_text = result['text']
                            st.session_state.current_title = "YouTube動画"
                            st.session_state.current_source_type = "youtube"
                            st.session_state.current_source_url = youtube_url
                            st.session_state.summaries = {}
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
        
        elif source_type == "PDFファイル":
            uploaded_file = st.file_uploader("PDFを選択", type=['pdf'])
            if uploaded_file and st.button("📄 読み込む", use_container_width=True):
                with st.spinner("解析中..."):
                    result = PDFHandler.extract_text_from_bytes(uploaded_file.read())
                    st.session_state.current_text = result['text']
                    st.session_state.current_title = uploaded_file.name
                    st.session_state.current_source_type = "pdf"
                    st.session_state.summaries = {}
                    st.rerun()
        
        else:
            t_title = st.text_input("タイトル")
            t_content = st.text_area("テキスト")
            if st.button("📝 読み込む", use_container_width=True):
                st.session_state.current_text = t_content
                st.session_state.current_title = t_title or "テキスト"
                st.session_state.current_source_type = "text"
                st.rerun()

        st.markdown("---")
        if st.button("📂 ナレッジベース", use_container_width=True):
            st.session_state.view_mode = "knowledge_base"
            st.rerun()


def render_landing():
    """ランディングページを描画"""
    st.markdown("""
    <div class="hero-container">
        <div class="hero-icon">🧠</div>
        <h1 class="hero-title">DeepLearn</h1>
        <p class="hero-subtitle">本や動画の内容を深く理解し、人に教えられるレベルまで</p>
        <div class="hero-stats">
            <div class="stat-item"><div class="stat-number">3段階</div><div class="stat-label">要約</div></div>
            <div class="stat-item"><div class="stat-number">AI</div><div class="stat-label">Gemini</div></div>
            <div class="stat-item"><div class="stat-number">∞</div><div class="stat-label">保存</div></div>
        </div>
    </div>
    <div class="feature-grid">
        <div class="feature-card"><h3>🎬 YouTube</h3><p>URLで要約</p></div>
        <div class="feature-card"><h3>📄 PDF</h3><p>文書を解析</p></div>
        <div class="feature-card"><h3>✍️ Text</h3><p>メモを学習</p></div>
    </div>
    """, unsafe_allow_html=True)


def main_content():
    """メインコンテンツの描画"""
    if st.session_state.get('view_mode') == 'knowledge_base':
        show_knowledge_base()
        return
    
    if st.session_state.current_text is None:
        render_landing()
        return
    
    st.title(f"📖 {st.session_state.current_title}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 要約", "🎯 ポイント", "❓ クイズ", "💾 保存"])
    gemini = get_gemini_client()
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        for i, (lvl, label) in enumerate([('10min', '10分'), ('30min', '30分'), ('1hour', '1時間')]):
            if col1 if i==0 else col2 if i==1 else col3:
                if st.button(f"⚡ {label}要約", use_container_width=True):
                    with st.spinner("生成中..."):
                        st.session_state.summaries[lvl] = gemini.summarize(st.session_state.current_text, lvl)
        
        for lvl in st.session_state.summaries:
            st.markdown(f"### {lvl} 要約")
            st.write(st.session_state.summaries[lvl])
            render_share_buttons(st.session_state.current_title, st.session_state.summaries[lvl])

    with tab2:
        if st.button("ポイント抽出"):
            st.session_state.key_points = gemini.extract_key_points(st.session_state.current_text)
        if st.session_state.key_points:
            st.write(st.session_state.key_points)

    with tab3:
        if st.button("クイズ作成"):
            st.session_state.quiz = gemini.generate_quiz(st.session_state.current_text, 5)
        if st.session_state.quiz:
            st.write(st.session_state.quiz)

    with tab4:
        if st.button("ナレッジベースに保存"):
            db = get_database()
            db.save_knowledge(
                title=st.session_state.current_title,
                source_type=st.session_state.current_source_type,
                source_url=st.session_state.current_source_url,
                original_text=st.session_state.current_text,
                summary_10min=st.session_state.summaries.get('10min'),
                summary_30min=st.session_state.summaries.get('30min'),
                summary_1hour=st.session_state.summaries.get('1hour'),
                key_points=st.session_state.key_points,
                quiz=st.session_state.quiz,
                tags=[]
            )
            st.success("保存しました！")
            st.balloons()


def show_knowledge_base():
    """ナレッジベース表示"""
    st.header("📂 保存済みリスト")
    if st.button("← 戻る"):
        st.session_state.view_mode = None
        st.rerun()
    
    db = get_database()
    for item in db.get_all_knowledge():
        with st.expander(item['title']):
            st.write(f"タイプ: {item['source_type']}")
            if st.button("この学習を再開", key=f"re_{item['id']}"):
                st.session_state.current_text = item['original_text']
                st.session_state.current_title = item['title']
                st.session_state.view_mode = None
                st.rerun()


def main():
    init_session_state()
    sidebar()
    main_content()

if __name__ == "__main__":
    main()
