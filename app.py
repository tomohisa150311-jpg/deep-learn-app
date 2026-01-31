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

# モダンなカスタムCSS
st.markdown("""
    /* ↓ここにスマホ用を追記！ */
    @media (max-width: 640px) {
        .hero-title { font-size: 2.2rem !important; }
        .stButton>button { width: 100% !important; }
        /* ...などなど */
    }
    </style>
""", unsafe_allow_html=True)<style>
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
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
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
    
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 2rem;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.8);
    }
    
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
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: #666;
        line-height: 1.5;
    }
    
    /* コンテンツカード */
    .content-card {
        background: linear-gradient(145deg, #ffffff, #f8f9ff);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .content-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .content-icon {
        font-size: 2rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .content-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a2e;
    }
    
    /* サマリーレベルボタン */
    .level-buttons {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .level-btn {
        flex: 1;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .level-btn-10 {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
    }
    
    .level-btn-30 {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    .level-btn-60 {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
    }
    
    .level-btn:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .level-time {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .level-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* 共有ボタン */
    .share-container {
        display: flex;
        gap: 0.75rem;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #eee;
    }
    
    .share-btn {
        padding: 0.6rem 1.2rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 500;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .share-twitter {
        background: #1DA1F2;
        color: white;
    }
    
    .share-line {
        background: #00B900;
        color: white;
    }
    
    .share-copy {
        background: #6c757d;
        color: white;
    }
    
    .share-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* タブスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    /* サイドバー */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    section[data-testid="stSidebar"] h2 {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] h3 {
        color: rgba(255,255,255,0.9) !important;
    }
    
    section[data-testid="stSidebar"] label {
        color: rgba(255,255,255,0.8) !important;
    }
    
    section[data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    section[data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* プログレスバー */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    /* 成功・エラーメッセージ */
    .stSuccess {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        border: none;
        border-radius: 12px;
    }
    
    /* スピナー */
    .stSpinner > div {
        border-color: #667eea transparent transparent transparent;
    }
    
    /* 結果表示エリア */
    .result-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
    
    /* アニメーション */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .animate-slide {
        animation: slideIn 0.5s ease-out;
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
    # 共有用テキストを準備
    share_text = f"📚 {title}\n\n{text[:200]}...\n\n#DeepLearn で学習中！"
    encoded_text = urllib.parse.quote(share_text)
    
    twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
    line_url = f"https://social-plugins.line.me/lineit/share?url=&text={encoded_text}"
    
    st.markdown(f"""
    <div class="share-container">
        <a href="{twitter_url}" target="_blank" class="share-btn share-twitter">
            🐦 Twitter
        </a>
        <a href="{line_url}" target="_blank" class="share-btn share-line">
            💬 LINE
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # コピーボタン
    if st.button("📋 クリップボードにコピー", key=f"copy_{hash(text[:50])}"):
        st.code(share_text, language=None)
        st.success("上のテキストをコピーしてください！")


def sidebar():
    """サイドバーの描画"""
    with st.sidebar:
        st.markdown("## 🧠 DeepLearn")
        st.markdown("*知識を深く、確実に*")
        st.markdown("---")
        
        st.markdown("### 📥 コンテンツを追加")
        
        source_type = st.selectbox(
            "種類を選択",
            ["YouTube動画", "PDFファイル", "テキスト入力"],
            key="source_type_select"
        )
        
        if source_type == "YouTube動画":
            youtube_url = st.text_input(
                "YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                key="youtube_url"
            )
            
            if st.button("🎬 動画を読み込む", key="load_youtube", use_container_width=True):
                if youtube_url:
                    with st.spinner("字幕を取得中..."):
                        try:
                            handler = YouTubeHandler()
                            result = handler.get_transcript_from_url(youtube_url)
                            st.session_state.current_text = result['text']
                            st.session_state.current_title = f"YouTube動画"
                            st.session_state.current_source_type = "youtube"
                            st.session_state.current_source_url = youtube_url
                            st.session_state.summaries = {}
                            st.session_state.key_points = None
                            st.session_state.quiz = None
                            st.session_state.teach_explanation = None
                            st.session_state.view_mode = None
                            st.success("✅ 読み込み完了！")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                else:
                    st.warning("URLを入力してください")
        
        elif source_type == "PDFファイル":
            uploaded_file = st.file_uploader(
                "PDFをアップロード",
                type=['pdf'],
                key="pdf_upload"
            )
            
            if uploaded_file is not None:
                if st.button("📄 PDFを読み込む", key="load_pdf", use_container_width=True):
                    with st.spinner("PDFを解析中..."):
                        try:
                            result = PDFHandler.extract_text_from_bytes(uploaded_file.read())
                            st.session_state.current_text = result['text']
                            st.session_state.current_title = uploaded_file.name
                            st.session_state.current_source_type = "pdf"
                            st.session_state.current_source_url = None
                            st.session_state.summaries = {}
                            st.session_state.key_points = None
                            st.session_state.quiz = None
                            st.session_state.teach_explanation = None
                            st.session_state.view_mode = None
                            st.success(f"✅ {result['page_count']}ページ読み込み完了！")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
        
        else:
            text_title = st.text_input("タイトル", placeholder="学習内容のタイトル", key="text_title")
            text_content = st.text_area(
                "テキストを入力",
                height=150,
                placeholder="学習したい内容を貼り付けてください...",
                key="text_content"
            )
            
            if st.button("📝 テキストを読み込む", key="load_text", use_container_width=True):
                if text_content:
                    st.session_state.current_text = text_content
                    st.session_state.current_title = text_title or "テキスト入力"
                    st.session_state.current_source_type = "text"
                    st.session_state.current_source_url = None
                    st.session_state.summaries = {}
                    st.session_state.key_points = None
                    st.session_state.quiz = None
                    st.session_state.teach_explanation = None
                    st.session_state.view_mode = None
                    st.success("✅ 読み込み完了！")
                    st.rerun()
                else:
                    st.warning("テキストを入力してください")
        
        st.markdown("---")
        
        st.markdown("### 📚 ナレッジベース")
        if st.button("📂 保存した学習を見る", key="view_knowledge", use_container_width=True):
            st.session_state.view_mode = "knowledge_base"
            st.rerun()


def render_hero():
    """ヒーローセクションを描画"""
    st.markdown("""
    <div class="hero-container">
        <div class="hero-icon">🧠</div>
        <h1 class="hero-title">DeepLearn</h1>
        <p class="hero-subtitle">本や動画の内容を深く理解し、人に教えられるレベルまで</p>
        <div class="hero-stats">
            <div class="stat-item">
                <div class="stat-number">3段階</div>
                <div class="stat-label">要約レベル</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">AI</div>
                <div class="stat-label">Gemini搭載</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">∞</div>
                <div class="stat-label">学習を保存</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_features():
    """フィーチャーカードを描画"""
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🎬</div>
            <div class="feature-title">YouTube動画</div>
            <div class="feature-desc">URLを貼るだけで字幕を自動取得し、内容を要約</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">PDF文書</div>
            <div class="feature-desc">PDFをアップロードして、テキストを抽出・要約</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">✍️</div>
            <div class="feature-title">テキスト入力</div>
            <div class="feature-desc">記事やメモを直接貼り付けて学習</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_landing():
    """ランディングページを描画"""
    render_hero()
    render_features()
    
    st.markdown("### 👈 サイドバーからコンテンツを読み込んで始めましょう！")
    
    with st.expander("💡 使い方ガイド"):
        st.markdown("""
        ### DeepLearnの使い方
        
        1. **コンテンツを追加** - サイドバーからYouTube動画のURL、PDFファイル、またはテキストを入力
        2. **学習レベルを選択** - 10分 / 30分 / 1時間 から学習時間を選択
        3. **要約を生成** - AIが内容を最適な長さに要約
        4. **理解を深める** - キーポイント抽出、クイズ、教えるモードで学習
        5. **共有・保存** - SNSで共有したり、ナレッジベースに保存して復習
        """)


def main_content():
    """メインコンテンツの描画"""
    
    if st.session_state.get('view_mode') == 'knowledge_base':
        show_knowledge_base()
        return
    
    if st.session_state.current_text is None:
        render_landing()
        return
    
    # コンテンツ表示モード
    st.markdown(f"""
    <div class="content-card">
        <div class="content-header">
            <span class="content-icon">📖</span>
            <span class="content-title">{st.session_state.current_title}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("✖ クリア"):
            for key in ['current_text', 'current_title', 'current_source_type', 
                       'current_source_url', 'summaries', 'key_points', 'quiz', 'teach_explanation']:
                st.session_state[key] = None if key != 'summaries' else {}
            st.rerun()
    
    # タブ
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 要約", "🎯 キーポイント", "❓ クイズ", "👨‍🏫 教えるモード", "💾 保存"
    ])
    
    gemini = get_gemini_client()
    
    # 要約タブ
    with tab1:
        st.markdown("#### ⏱️ 学習時間を選んでください")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="level-btn level-btn-10">
                <div class="level-time">10分</div>
                <div class="level-label">クイック学習</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⚡ 生成", key="sum_10min", use_container_width=True):
                with st.spinner("10分要約を生成中..."):
                    summary = gemini.summarize(st.session_state.current_text, "10min")
                    st.session_state.summaries['10min'] = summary
        
        with col2:
            st.markdown("""
            <div class="level-btn level-btn-30">
                <div class="level-time">30分</div>
                <div class="level-label">スタンダード</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 生成", key="sum_30min", use_container_width=True):
                with st.spinner("30分要約を生成中..."):
                    summary = gemini.summarize(st.session_state.current_text, "30min")
                    st.session_state.summaries['30min'] = summary
        
        with col3:
            st.markdown("""
            <div class="level-btn level-btn-60">
                <div class="level-time">1時間</div>
                <div class="level-label">ディープラーニング</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📚 生成", key="sum_1hour", use_container_width=True):
                with st.spinner("1時間要約を生成中..."):
                    summary = gemini.summarize(st.session_state.current_text, "1hour")
                    st.session_state.summaries['1hour'] = summary
        
        st.markdown("---")
        
        if st.session_state.summaries:
            for level, label in [('10min', '⚡ 10分要約'), ('30min', '📖 30分要約'), ('1hour', '📚 1時間要約')]:
                if level in st.session_state.summaries:
                    with st.expander(label, expanded=(len(st.session_state.summaries) == 1)):
                        st.markdown(st.session_state.summaries[level])
                        render_share_buttons(
                            st.session_state.current_title,
                            st.session_state.summaries[level]
                        )
    
    # キーポイントタブ
    with tab2:
        st.markdown("#### 🎯 重要ポイントを抽出")
        if st.button("キーポイントを抽出", key="extract_keypoints", use_container_width=True):
            with st.spinner("キーポイントを抽出中..."):
                st.session_state.key_points = gemini.extract_key_points(st.session_state.current_text)
        
        if st.session_state.key_points:
            st.markdown(st.session_state.key_points)
            render_share_buttons(st.session_state.current_title, st.session_state.key_points)
    
    # クイズタブ
    with tab3:
        st.markdown("#### ❓ 理解度チェック")
        num_questions = st.slider("問題数", 3, 10, 5, key="quiz_num")
        
        if st.button("クイズを生成", key="generate_quiz", use_container_width=True):
            with st.spinner("クイズを生成中..."):
                st.session_state.quiz = gemini.generate_quiz(st.session_state.current_text, num_questions)
        
        if st.session_state.quiz:
            st.markdown(st.session_state.quiz)
    
    # 教えるモードタブ
    with tab4:
        st.markdown("#### 👨‍🏫 Feynmanテクニック")
        st.info("学んだことを誰かに教えるつもりで説明すると、理解が深まります。")
        
        if st.button("わかりやすい説明を生成", key="generate_teach", use_container_width=True):
            with st.spinner("説明を生成中..."):
                st.session_state.teach_explanation = gemini.explain_like_teaching(st.session_state.current_text)
        
        if st.session_state.teach_explanation:
            st.markdown("### 💡 AIによる説明例")
            st.markdown(st.session_state.teach_explanation)
            
            st.markdown("---")
            st.markdown("### ✍️ あなたの説明を書いてみましょう")
            st.text_area(
                "自分の言葉で説明",
                height=200,
                placeholder="学んだ内容を、友達や家族に教えるつもりで書いてみましょう...",
                key="user_explanation"
            )
    
    # 保存タブ
    with tab5:
        st.markdown("#### 💾 ナレッジベースに保存")
        
        save_title = st.text_input("タイトル", value=st.session_state.current_title, key="save_title")
        save_tags = st.text_input("タグ（カンマ区切り）", placeholder="プログラミング, Python, 初心者", key="save_tags")
        
        if st.button("保存する", key="save_knowledge", use_container_width=True):
            db = get_database()
            tags = [t.strip() for t in save_tags.split(',') if t.strip()] if save_tags else []
            
            knowledge_id = db.save_knowledge(
                title=save_title,
                source_type=st.session_state.current_source_type,
                source_url=st.session_state.current_source_url,
                original_text=st.session_state.current_text,
                summary_10min=st.session_state.summaries.get('10min'),
                summary_30min=st.session_state.summaries.get('30min'),
                summary_1hour=st.session_state.summaries.get('1hour'),
                key_points=st.session_state.key_points,
                quiz=st.session_state.quiz,
                tags=tags,
            )
            
            st.success(f"✅ 保存しました！（ID: {knowledge_id}）")
            st.balloons()


def show_knowledge_base():
    """ナレッジベース表示"""
    st.markdown("## 📂 ナレッジベース")
    
    if st.button("← 戻る", key="back_from_kb"):
        st.session_state.view_mode = None
        st.rerun()
    
    search_query = st.text_input("🔍 検索", placeholder="キーワードで検索...", key="kb_search")
    
    db = get_database()
    items = db.search_knowledge(search_query) if search_query else db.get_all_knowledge()
    
    if not items:
        st.info("保存された学習はまだありません")
        return
    
    for item in items:
        with st.expander(f"📖 {item['title']} ({item['source_type']})"):
            st.markdown(f"**作成日**: {item['created_at']}")
            if item['tags']:
                st.markdown(f"**タグ**: {', '.join(item['tags'])}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("詳細を見る", key=f"view_{item['id']}"):
                    full_item = db.get_knowledge(item['id'])
                    st.session_state.current_text = full_item['original_text']
                    st.session_state.current_title = full_item['title']
                    st.session_state.current_source_type = full_item['source_type']
                    st.session_state.current_source_url = full_item['source_url']
                    st.session_state.summaries = {
                        k: v for k, v in [
                            ('10min', full_item['summary_10min']),
                            ('30min', full_item['summary_30min']),
                            ('1hour', full_item['summary_1hour']),
                        ] if v
                    }
                    st.session_state.key_points = full_item['key_points']
                    st.session_state.quiz = full_item['quiz']
                    st.session_state.view_mode = None
                    st.rerun()
            
            with col3:
                if st.button("🗑 削除", key=f"delete_{item['id']}"):
                    db.delete_knowledge(item['id'])
                    st.rerun()


def main():
    """メイン関数"""
    init_session_state()
    sidebar()
    main_content()


if __name__ == "__main__":
    main()
