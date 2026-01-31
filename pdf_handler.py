"""PDF文書の処理"""
import pdfplumber
from io import BytesIO


class PDFHandler:
    """PDFからテキストを抽出するハンドラー"""
    
    @staticmethod
    def extract_text_from_file(file_path: str) -> dict:
        """
        PDFファイルからテキストを抽出する
        
        Args:
            file_path: PDFファイルのパス
        
        Returns:
            dict: {
                'text': 全文テキスト,
                'pages': ページごとのテキストリスト,
                'page_count': ページ数
            }
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    pages.append(text)
                
                full_text = '\n\n'.join(pages)
                
                return {
                    'text': full_text,
                    'pages': pages,
                    'page_count': len(pages),
                }
        except Exception as e:
            raise Exception(f"PDFの読み込みに失敗しました: {str(e)}")
    
    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes) -> dict:
        """
        バイトデータからPDFテキストを抽出する（Streamlitアップロード用）
        
        Args:
            file_bytes: PDFファイルのバイトデータ
        
        Returns:
            dict: {
                'text': 全文テキスト,
                'pages': ページごとのテキストリスト,
                'page_count': ページ数
            }
        """
        try:
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    pages.append(text)
                
                full_text = '\n\n'.join(pages)
                
                return {
                    'text': full_text,
                    'pages': pages,
                    'page_count': len(pages),
                }
        except Exception as e:
            raise Exception(f"PDFの読み込みに失敗しました: {str(e)}")
