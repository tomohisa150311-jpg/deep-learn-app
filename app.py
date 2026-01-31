import streamlit as st
import time

# --- ここはご自身のモジュールに合わせて調整してください ---
# 既存のクラスが引数を受け取れるように、少し工夫が必要です。
# もし client側の変更が難しい場合は、テキスト自体に指示を埋め込む手法をとっています。
from gemini_client import GeminiClient
from youtube_handler import YouTubeHandler
from pdf_handler import PDFHandler
from database import Database

# --- 1. ページ設定 (必ず最初に記述) ---
st.set_page_config(
    page_title="DeepLearn | AI Learning Assistant",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. 高度なCSSデザイン (Glassmorphism & Animation) ---
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&family=Exo+2:wght@700&display=swap');

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

    /* 結果表示エリアの文字装飾 */
    .result-content {
        line-height: 1.8;
        font-size: 1.05rem;
        white-space: pre-wrap;
    }
    
    /* ボタンカスタマイズ */
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

    /* プログレスバー */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #00c6ff, #0072ff);
    }
    
    /* ユーティリティ */
    .badge-easy {
        display: inline-block;
        background: #00b09b; /* 緑系 */
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 10px;
        box-shadow: 0 0 10px rgba(0, 176, 155, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ヘルパー関数: プロンプト修飾 (これが「やさしい機能」の核) ---
def get_instruction_suffix(is_easy_mode):
    """
    ユーザーの設定に応じて、Geminiへの指示を追加する。
    これにより、既存のClientコードを大きく書き換えずに機能追加可能。
    """
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
    # Session State 初期化
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'current_text' not in st.session_state: st.session_state.current_text = None
    if 'active_tool' not in st.session_state: st.session_state.active_tool = None
    if 'result_cache' not in st.session_state: st.session_state.result_cache = None
    
    # ツールキャッシュ管理 (モード切替時にキャッシュをクリアするため)
    if 'last_easy_mode' not in st.session_state: st.session_state.last_easy_mode = False

    client = GeminiClient()
    db = Database()

    # --- サイドバー設定 (設定 & ナビゲーション) ---
    with st.sidebar:
        st.markdown("### ⚙️ 設定")
        # 🔰 デジタル識字率対応スイッチ
        easy_mode = st.toggle("🔰 やさしいモード", value=False, help="ONにすると、専門用語を使わず、誰にでもわかる言葉で解説します。")
        
        # モードが切り替わったら結果キャッシュをクリアして再生成を促す
        if easy_mode != st.session_state.last_easy_mode:
            st.session_state.result_cache = None
            st.session_state.last_easy_mode = easy_mode
            st.rerun()

        st.markdown("---")
        st.markdown("### 📚 履歴")
        st.caption("最近の学習履歴がここに表示されます (Demo)")
        # ここにDBから履歴を表示する機能を後で追加可能

    # --- メインエリア ---
    # ヘッダー表示
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
                        # プログレスバー演出
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        try:
                            res = YouTubeHandler().get_transcript_from_url(url)
                            st.session_state.current_text = res['text']
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
             # 現在の状態表示
            mode_badge = '<span class="badge-easy">🔰 やさしいモード ON</span>' if easy_mode else ""
            st.markdown(f'<div style="text-align:right; padding-top:5px;">{mode_badge}</div>', unsafe_allow_html=True)

        # メインコントロールパネル
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown("### 🛠️ 学習ツールを選択")
        
        c1, c2, c3, c4 = st.columns(4)
        
        # ボタンクリック時のハンドリング
        def set_tool(tool_name):
            st.session_state.active_tool = tool_name
            st.session_state.result_cache = None # ツール変更時はキャッシュクリア

        if c1.button("📝 要約する", use_container_width=True): set_tool("sum")
        if c2.button("🎯 重要ポイント", use_container_width=True): set_tool("point")
        if c3.button("❓ クイズ作成", use_container_width=True): set_tool("quiz")
        if c4.button("💾 保存する", use_container_width=True):
            db.save_knowledge("学習データ", st.session_state.current_text)
            st.toast("✅ データベースに保存しました！", icon="💾")

        st.markdown('</div>', unsafe_allow_html=True)

        # 結果表示エリア
        if st.session_state.active_tool:
            # まだ結果がなく、計算が必要な場合
            if st.session_state.result_cache is None:
                instruction = get_instruction_suffix(easy_mode)
                
                # GeminiClientのメソッド呼び出し時に、instructionを含めたテキストを渡す
                # ※client側のコードを変更せずに挙動を変えるハックです
                text_payload = st.session_state.current_text + instruction

                with st.spinner("💎 Gemini 1.5 Flash が思考中..."):
                    try:
                        if st.session_state.active_tool == "sum":
                            # client.summarizeの引数仕様に合わせて調整してください
                            # もしclientが単純にtextしか受け取らないなら、上記text_payloadを渡すだけでOK
                            st.session_state.result_cache = client.summarize(text_payload, '30min')
                        
                        elif st.session_state.active_tool == "point":
                            st.session_state.result_cache = client.extract_key_points(text_payload)
                        
                        elif st.session_state.active_tool == "quiz":
                            st.session_state.result_cache = client.generate_quiz(text_payload)
                    except Exception as e:
                        st.error(f"AI生成エラー: {e}")
            
            # 結果の表示（フェードインアニメーション付き）
            if st.session_state.result_cache:
                title_map = {"sum": "📝 要約結果", "point": "🎯 重要ポイント", "quiz": "❓ 理解度クイズ"}
                current_title = title_map.get(st.session_state.active_tool, "結果")
                
                st.markdown(f"""
                <div class="glass-panel">
                    <h3 style="border-bottom:1px solid rgba(255,255,255,0.2); padding-bottom:10px; margin-bottom:15px;">
                        {current_title}
                    </h3>
                    <div class="result-content">
                        {st.session_state.result_cache}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # クリップボードコピー用（簡易的な実装としてTextAreaを表示）
                with st.expander("📋 テキストをコピーする"):
                    st.text_area("以下のテキストをコピーしてください", value=st.session_state.result_cache, height=100)

if __name__ == "__main__":
    main()
