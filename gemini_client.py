"""Gemini API クライアント"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def get_api_key():
    """APIキーを取得（Streamlit Cloud / ローカル両対応）"""
    # Streamlit Cloudのsecretsを優先
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
    except Exception:
        pass
    
    # ローカルの.envファイル
    return os.getenv("GEMINI_API_KEY")


class GeminiClient:
    """Google Gemini APIとの通信を担当するクライアント"""
    
    def __init__(self):
        api_key = get_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません。.env ファイルまたはStreamlit Secretsを確認してください。")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
    
    def generate(self, prompt: str) -> str:
        """プロンプトを送信してレスポンスを取得"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API エラー: {str(e)}")
    
    def summarize(self, text: str, level: str) -> str:
        """テキストを指定されたレベルで要約する"""
        level_instructions = {
            "10min": """
【10分で読める要約】
以下の内容を10分で理解できるように要約してください：
- 核心となる結論を最初に
- 最も重要なポイントを3つ
- 1行で表す本質
""",
            "30min": """
【30分で読める要約】
以下の内容を30分で深く理解できるように要約してください：
- 主要な論点とその根拠
- 具体的な例や事例
- 実践するための方法
- 重要な引用や数字
""",
            "1hour": """
【1時間で読める要約】
以下の内容を1時間かけてじっくり学べるように詳細に要約してください：
- 全体の構造と流れ
- 各章/セクションの詳細な解説
- 背景知識と文脈
- 具体例と応用方法
- 著者の主張と根拠
- 関連する概念や理論
- 実践のためのアクションプラン
"""
        }
        
        instruction = level_instructions.get(level, level_instructions["30min"])
        
        prompt = f"""{instruction}

===== コンテンツ =====
{text}
===== ここまで =====

日本語で、読みやすく構造化して回答してください。
マークダウン形式で見出しや箇条書きを使ってください。
"""
        return self.generate(prompt)
    
    def generate_quiz(self, text: str, num_questions: int = 5) -> str:
        """理解度確認クイズを生成する"""
        prompt = f"""以下のコンテンツに基づいて、理解度を確認するためのクイズを{num_questions}問作成してください。

【形式】
各問題は以下の形式で出力してください：

## 問題1
（問題文）

A) 選択肢1
B) 選択肢2
C) 選択肢3
D) 選択肢4

**正解**: （正解の選択肢）
**解説**: （なぜその答えが正しいのかの解説）

---

===== コンテンツ =====
{text}
===== ここまで =====

・表面的な知識ではなく、本質的な理解を問う問題にしてください
・「人に説明できるか」を確認できる問題を含めてください
・日本語で出力してください
"""
        return self.generate(prompt)
    
    def explain_like_teaching(self, text: str) -> str:
        """人に教えるように説明を生成する（Feynmanテクニック）"""
        prompt = f"""あなたは優秀な教師です。以下の内容を、誰かに教えるつもりで説明してください。

【要件】
1. 専門用語は必ず簡単な言葉で言い換える
2. 具体的な例え話や身近な例を使う
3. 「つまり〜ということです」という形でまとめる
4. 相手が「なるほど！」と思えるような説明
5. 難しい概念は段階的に説明

===== コンテンツ =====
{text}
===== ここまで =====

日本語で、話しかけるような口調で説明してください。
"""
        return self.generate(prompt)
    
    def extract_key_points(self, text: str) -> str:
        """キーポイントを抽出する"""
        prompt = f"""以下のコンテンツから、最も重要なキーポイントを抽出してください。

【形式】
## キーポイント

1. **（キーワード）**: （1-2文での説明）
2. **（キーワード）**: （1-2文での説明）
...

## 一言でまとめると
（このコンテンツの本質を一文で）

## 覚えておくべき数字・事実
- （重要な数字や事実があれば）

===== コンテンツ =====
{text}
===== ここまで =====

日本語で出力してください。
"""
        return self.generate(prompt)
