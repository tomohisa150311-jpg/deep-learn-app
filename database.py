"""ナレッジベースのデータベース管理"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path


class Database:
    """SQLiteを使用したナレッジベースの管理"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # デフォルトはプロジェクトルートのdata/knowledge.db
            db_dir = Path(__file__).parent.parent / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "knowledge.db")
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """データベースの初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    source_type TEXT NOT NULL,  -- 'youtube', 'pdf', 'text'
                    source_url TEXT,
                    original_text TEXT,
                    summary_10min TEXT,
                    summary_30min TEXT,
                    summary_1hour TEXT,
                    key_points TEXT,
                    quiz TEXT,
                    tags TEXT,  -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    knowledge_id INTEGER,
                    score INTEGER,
                    total INTEGER,
                    taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (knowledge_id) REFERENCES knowledge (id)
                )
            """)
            
            conn.commit()
    
    def save_knowledge(
        self,
        title: str,
        source_type: str,
        original_text: str,
        source_url: str = None,
        summary_10min: str = None,
        summary_30min: str = None,
        summary_1hour: str = None,
        key_points: str = None,
        quiz: str = None,
        tags: list[str] = None,
    ) -> int:
        """ナレッジを保存する"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO knowledge (
                    title, source_type, source_url, original_text,
                    summary_10min, summary_30min, summary_1hour,
                    key_points, quiz, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    source_type,
                    source_url,
                    original_text,
                    summary_10min,
                    summary_30min,
                    summary_1hour,
                    key_points,
                    quiz,
                    json.dumps(tags or []),
                )
            )
            conn.commit()
            return cursor.lastrowid
    
    def update_knowledge(self, knowledge_id: int, **kwargs):
        """ナレッジを更新する"""
        allowed_fields = [
            'title', 'summary_10min', 'summary_30min', 'summary_1hour',
            'key_points', 'quiz', 'tags'
        ]
        
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                if field == 'tags':
                    values.append(json.dumps(value))
                else:
                    values.append(value)
        
        if not updates:
            return
        
        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(knowledge_id)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"UPDATE knowledge SET {', '.join(updates)} WHERE id = ?",
                values
            )
            conn.commit()
    
    def get_knowledge(self, knowledge_id: int) -> dict | None:
        """IDでナレッジを取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM knowledge WHERE id = ?",
                (knowledge_id,)
            )
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['tags'] = json.loads(result['tags'] or '[]')
                return result
            return None
    
    def get_all_knowledge(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """すべてのナレッジを取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT id, title, source_type, source_url, tags, created_at
                FROM knowledge
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['tags'] = json.loads(result['tags'] or '[]')
                results.append(result)
            return results
    
    def search_knowledge(self, query: str) -> list[dict]:
        """ナレッジを検索"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT id, title, source_type, source_url, tags, created_at
                FROM knowledge
                WHERE title LIKE ? OR original_text LIKE ? OR key_points LIKE ?
                ORDER BY created_at DESC
                """,
                (f"%{query}%", f"%{query}%", f"%{query}%")
            )
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['tags'] = json.loads(result['tags'] or '[]')
                results.append(result)
            return results
    
    def delete_knowledge(self, knowledge_id: int):
        """ナレッジを削除"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM quiz_results WHERE knowledge_id = ?", (knowledge_id,))
            conn.execute("DELETE FROM knowledge WHERE id = ?", (knowledge_id,))
            conn.commit()
    
    def save_quiz_result(self, knowledge_id: int, score: int, total: int):
        """クイズ結果を保存"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO quiz_results (knowledge_id, score, total) VALUES (?, ?, ?)",
                (knowledge_id, score, total)
            )
            conn.commit()
    
    def get_quiz_history(self, knowledge_id: int) -> list[dict]:
        """クイズ履歴を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM quiz_results
                WHERE knowledge_id = ?
                ORDER BY taken_at DESC
                """,
                (knowledge_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
