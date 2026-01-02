#core/normalizer.py
import re

class TextNormalizer:
    @staticmethod
    def normalize_dots(text):
        """Chuẩn hóa dấu ba chấm"""
        if not text:
            return ""
        
        # Thay thế tất cả các dạng dấu ba chấm bằng dấu chấm đơn
        text = re.sub(r'\.\s*\.\s*\.', '.', text)  # . . . -> .
        text = re.sub(r'\.\s*\.', '.', text)       # . . -> .
        text = re.sub(r'\.\.\.', '.', text)        # ... -> .
        text = re.sub(r'\s+', ' ', text)          # Nén khoảng trắng
        
        return text.strip()
    
    @staticmethod
    def normalize_text(text):
        """Chuẩn hóa văn bản để tạo fingerprint"""
        if not text:
            return ""
        
        # Chuyển về chữ thường
        text = text.lower()
        
        # Loại bỏ dấu và ký tự đặc biệt
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def clean_question_text(text):
        """Làm sạch nội dung câu hỏi"""
        # Loại bỏ số thứ tự câu
        text = re.sub(r'^Câu\s*\d+[\.:\)]\s*', '', text, flags=re.IGNORECASE)
        
        # Chuẩn hóa dấu câu
        text = TextNormalizer.normalize_dots(text)
        
        return text.strip()
    
    @staticmethod
    def clean_option_text(text):
        """Làm sạch nội dung lựa chọn"""
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text).strip()
        return text