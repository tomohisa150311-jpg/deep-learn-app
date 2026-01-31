# 🧠 DeepLearn - 学習支援アプリ

本や動画の内容を深く理解し、**人に教えられるレベル**まで学習をサポートするAIアプリです。

![DeepLearn](https://img.shields.io/badge/Powered%20by-Gemini%20AI-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 特徴

- 🎬 **YouTube動画** - URLを貼るだけで字幕を自動取得
- 📄 **PDF文書** - アップロードしてテキスト抽出
- ✍️ **テキスト入力** - 記事やメモを直接貼り付け

## 📚 3段階の学習レベル

| レベル | 時間 | 内容 |
|--------|------|------|
| ⚡ クイック | 10分 | 核心と重要ポイント3つ |
| 📖 スタンダード | 30分 | 主要な論点、具体例、実践方法 |
| 📚 ディープ | 1時間 | 全体像、詳細解説、応用 |

## 🎯 理解を深める機能

- **キーポイント抽出** - 重要な概念をリスト化
- **クイズ生成** - 理解度をテスト
- **教えるモード** - Feynmanテクニックで学習
- **ナレッジベース** - 学んだ内容を保存・復習

## 🔗 共有機能

- Twitter / LINE でワンクリック共有
- クリップボードにコピー

---

## 🚀 ローカルで使う

### 1. インストール

```bash
git clone https://github.com/YOUR_USERNAME/deeplearn.git
cd deeplearn
pip install -r requirements.txt
```

### 2. APIキーを設定

```bash
cp .env.example .env
# .env を編集して GEMINI_API_KEY を設定
```

APIキーは [Google AI Studio](https://makersuite.google.com/app/apikey) から取得できます。

### 3. 起動

```bash
streamlit run src/app.py
```

ブラウザで http://localhost:8501 にアクセス！

---

## ☁️ Streamlit Cloudでデプロイ

### 1. GitHubにプッシュ

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/deeplearn.git
git push -u origin main
```

### 2. Streamlit Cloudで公開

1. [Streamlit Cloud](https://share.streamlit.io/) にログイン
2. "New app" をクリック
3. GitHubリポジトリを選択
4. Main file path: `src/app.py`
5. **Settings > Secrets** に以下を追加:

```toml
GEMINI_API_KEY = "your_api_key_here"
```

6. "Deploy!" をクリック

数分でアプリが公開されます！🎉

---

## 📁 プロジェクト構成

```
deeplearn/
├── .streamlit/
│   └── config.toml      # Streamlit設定
├── src/
│   ├── app.py           # メインUI
│   ├── gemini_client.py # Gemini API連携
│   ├── youtube_handler.py # YouTube字幕取得
│   ├── pdf_handler.py   # PDF処理
│   └── database.py      # ナレッジベース
├── .env.example         # 環境変数テンプレート
├── requirements.txt     # 依存パッケージ
└── README.md
```

---

## 🛠️ 技術スタック

- **Frontend**: Streamlit
- **AI**: Google Gemini API
- **YouTube**: youtube-transcript-api
- **PDF**: pdfplumber
- **Database**: SQLite

---

## 📝 ライセンス

MIT License

---

## 🙏 クレジット

Made with ❤️ and AI
