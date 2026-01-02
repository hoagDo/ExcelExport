# core/deduplicator.py

from .normalizer import TextNormalizer
from .logger import Logger
import hashlib

class Deduplicator:
    def __init__(self, policy='allow', logger=None):
        self.policy = policy 
        self.fingerprint_map = {}
        self.conflicts = []
        self.logger = logger or Logger()
    
    def get_fingerprint(self, text, options):
        """
        Tạo fingerprint dựa trên CẢ CÂU HỎI VÀ ĐÁP ÁN.
        Điều này giúp phân biệt 2 câu có đề bài giống nhau nhưng đáp án khác nhau.
        """

        norm_text = TextNormalizer.normalize_text(text)
        
        valid_opts = [TextNormalizer.normalize_text(opt) for opt in options if opt]
        opts_str = "".join(valid_opts)
        
        raw_id = f"{norm_text}|{opts_str}"
        
        return hashlib.md5(raw_id.encode('utf-8')).hexdigest()

    def process_duplicate(self, question_text, options, existing_data):
        """Xử lý câu hỏi trùng lặp hoàn toàn (cả câu hỏi lẫn đáp án)"""
        existing_question, existing_options = existing_data
        
        if self.policy == 'skip':
            return None  # Bỏ qua
        
        elif self.policy == 'append':
            suffix = 1
            base_text = question_text
            while True:
                new_text = f"{base_text} ({suffix})"

                new_fingerprint = self.get_fingerprint(new_text, options)
                
                if new_fingerprint not in self.fingerprint_map:
                    return (new_text, options)
                suffix += 1
        
        elif self.policy == 'allow':

            return (question_text, options)
        
        return None

    def add_question(self, question_text, options):
        """Thêm câu hỏi vào hệ thống, xử lý trùng lặp"""

        fingerprint = self.get_fingerprint(question_text, options)
        
        if fingerprint in self.fingerprint_map:

            result = self.process_duplicate(question_text, options, 
                                            self.fingerprint_map[fingerprint])
            if result:

                return result
            return None
        else:

            self.fingerprint_map[fingerprint] = (question_text, options)
            return (question_text, options)

    def merge_options(self, existing_options, new_options):
        """
        Hàm này ít được dùng hơn trong logic mới vì fingerprint đã phân biệt options.
        Giữ lại để tương thích nếu cần mở rộng sau này.
        """
        merged = list(existing_options)
        for i in range(4):
            if i < len(new_options):
                new_opt = new_options[i]
                if new_opt and new_opt.strip():
                    if i >= len(existing_options) or not existing_options[i] or not existing_options[i].strip():
                        if i >= len(merged):
                            merged.append(new_opt)
                        else:
                            merged[i] = new_opt
        while len(merged) < 4:
            merged.append("")
        return merged[:4]
