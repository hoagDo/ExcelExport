#core/normalizer.py
import re

class TextNormalizer:
    @staticmethod
    def normalize_dots(text):
        """Chuẩn hóa dấu ba chấm"""
        if not text:
            return ""
        
        text = re.sub(r'\.\s*\.\s*\.', '.', text)  
        text = re.sub(r'\.\s*\.', '.', text)      
        text = re.sub(r'\.\.\.', '.', text)     
        text = re.sub(r'\s+', ' ', text)        
        
        return text.strip()
    
    @staticmethod
    def normalize_text(text):
        """Chuẩn hóa văn bản để tạo fingerprint"""
        if not text:
            return ""
        
        text = text.lower()
        
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def clean_question_text(text):
        """Làm sạch nội dung câu hỏi"""
        text = re.sub(r'^Câu\s*\d+[\.:\)]\s*', '', text, flags=re.IGNORECASE)
        
        text = TextNormalizer.normalize_dots(text)
        
        return text.strip()
    
    @staticmethod
    def clean_option_text(text):
        """Làm sạch nội dung lựa chọn"""

        text = re.sub(r'\s+', ' ', text).strip()
        return text
