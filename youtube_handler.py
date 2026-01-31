"""YouTube動画の文字起こし処理"""
import re
from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeHandler:
    """YouTube動画から字幕を取得するハンドラー"""
    
    def __init__(self):
        self.api = YouTubeTranscriptApi()
    
    @staticmethod
    def extract_video_id(url: str) -> str | None:
        """YouTubeのURLから動画IDを抽出する"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_transcript(self, video_id: str, languages: list[str] = None) -> dict:
        """
        動画IDから字幕を取得する
        
        Args:
            video_id: YouTube動画ID
            languages: 優先する言語のリスト（デフォルト: ['ja', 'en']）
        
        Returns:
            dict: {
                'text': 全文テキスト,
                'segments': タイムスタンプ付きセグメントのリスト,
                'language': 取得した言語
            }
        """
        if languages is None:
            languages = ['ja', 'en']
        
        try:
            # 新しいAPI: インスタンスのfetchメソッドを使用
            fetched_transcript = self.api.fetch(video_id, languages=languages)
            
            # FetchedTranscriptオブジェクトから生データを取得
            segments = fetched_transcript.to_raw_data()
            
            # 全文テキストを生成
            full_text = ' '.join([seg['text'] for seg in segments])
            
            # 使用された言語
            used_language = fetched_transcript.language
            
            return {
                'text': full_text,
                'segments': segments,
                'language': used_language,
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'disabled' in error_msg:
                raise Exception("この動画では字幕が無効になっています")
            elif 'unavailable' in error_msg or 'not found' in error_msg:
                raise Exception("動画が見つかりません")
            elif 'no transcript' in error_msg:
                raise Exception("利用可能な字幕が見つかりません")
            else:
                raise Exception(f"字幕の取得に失敗しました: {str(e)}")
    
    def get_transcript_from_url(self, url: str) -> dict:
        """URLから字幕を取得する"""
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError("有効なYouTube URLではありません")
        
        return self.get_transcript(video_id)


# シングルトンインスタンスを作成（後方互換性のため）
_handler = None

def get_handler() -> YouTubeHandler:
    global _handler
    if _handler is None:
        _handler = YouTubeHandler()
    return _handler
