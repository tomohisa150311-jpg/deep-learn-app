import streamlit as st
import time
from datetime import datetime

# --- 外部モジュール (ご環境に合わせて読み込み) ---
# ※ gemini_client などのファイルが同じフォルダにある前提です
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
