# text_processor.py
import re
from core.normalizer import TextNormalizer

class TextProcessor:
    def __init__(self):
        self.normalizer = TextNormalizer()
    
    def extract_questions_from_text(self, text):
        questions = []
        
        # --- REGEX HAI CHẾ ĐỘ (V11) ---
        # 1. Số đầu dòng (1., 2.) -> Tránh bắt nhầm năm/trang
        # 2. Chữ "Câu" (Câu 1, Câu 2) -> Bắt mọi nơi
        pattern = r'(?:^|[\n\r])\s*\d+[.:)]|Câu\s*\d+(?:[.:,)|-]|\s)'
        
        question_matches = list(re.finditer(pattern, text, re.IGNORECASE))
        
        if not question_matches:
            return questions
            
        start_indices = []
        for match in question_matches:
            start = match.start()
            if text[start] in ['\n', '\r']:
                start_indices.append(start + 1)
            else:
                start_indices.append(start)
        
        for i, start_pos in enumerate(start_indices):
            if i < len(start_indices) - 1:
                end_pos = start_indices[i + 1]
            else:
                end_pos = len(text)
            
            question_block = text[start_pos:end_pos].strip()
            if len(question_block) < 5: continue
                
            question_data = self._process_question_block_smart(question_block)
            
            if question_data:
                valid_opts = [opt for opt in question_data['options'] if opt]
                if len(valid_opts) >= 2:
                    questions.append(question_data)
        
        return questions

    def _process_question_block_smart(self, block):
        try:
            # 1. Trích xuất số câu
            num_match = re.search(r'(?:Câu\s*)?(\d+)', block[:15], re.IGNORECASE)
            question_number = int(num_match.group(1)) if num_match else None
            
            # Chuẩn hóa
            clean_block = re.sub(r'\n', ' ', block)
            clean_block = re.sub(r'\s+', ' ', clean_block)
            
            # 2. Tách Đáp án (Last Win Logic)
            candidates = list(re.finditer(r'(?<=[\s])[aA][.:)]', clean_block))
            best_candidate = None
            max_score = -1
            
            for cand in candidates:
                start_index = cand.start()
                search_area = clean_block[start_index:]
                score = 0
                if re.search(r'(?<=[\s])[bB][.:)]', search_area): score += 1
                if re.search(r'(?<=[\s])[cC][.:)]', search_area): score += 1
                if re.search(r'(?<=[\s])[dD][.:)]', search_area): score += 1
                
                if score >= max_score:
                    max_score = score
                    best_candidate = cand

            if best_candidate:
                split_idx = best_candidate.start()
                raw_question = clean_block[:split_idx]
                raw_options = clean_block[split_idx:]
            else:
                raw_question = clean_block
                raw_options = ""

            # 3. LÀM SẠCH CÂU HỎI (CẬP NHẬT MỚI NHẤT)
            # Regex cũ: [.:)\s-]* --> Thiếu dấu phẩy (,) và gạch đứng (|)
            # Regex mới: [.:,)|\]\s-]* --> Đã thêm , | ]
            
            # Logic: Xóa [Dấu chấm/space đầu] + [Câu (nếu có)] + [Số] + [DẤU RÁC]
            temp_q = re.sub(r'^[\.\s]*(?:Câu\s*)?\d+[.:,)|\]\s-]*', '', raw_question, flags=re.IGNORECASE).strip()
            
            if raw_question.strip().startswith('"') or raw_question.strip().startswith('“'):
                 pass 
            else:
                 # Xóa số rác dính liền
                 temp_q = re.sub(r'^\d+\s*', '', temp_q).strip()
            
            question_text = self.normalizer.clean_question_text(temp_q)

            # 4. Trích xuất Options (Slicing - Bắt đủ A,B,C,D)
            options_dict = {}
            targets = ['A', 'B', 'C', 'D']
            
            found_markers = []
            for char in targets:
                pattern = rf'(?:^|\s)([{char.lower()}{char.upper()}][.:)])'
                for m in re.finditer(pattern, raw_options):
                    found_markers.append({
                        'char': char,
                        'start': m.start(1),
                        'end': m.end(1)
                    })
            
            found_markers.sort(key=lambda x: x['start'])
            
            for i, marker in enumerate(found_markers):
                char = marker['char']
                start_content = marker['end']
                
                if i < len(found_markers) - 1:
                    end_content = found_markers[i+1]['start']
                else:
                    end_content = len(raw_options)
                
                content = raw_options[start_content:end_content].strip()
                options_dict[char] = self.normalizer.clean_option_text(content)
            
            ordered_options = [options_dict.get(k, "") for k in targets]

            return {
                'question_text': question_text,
                'options': ordered_options,
                'question_number': question_number
            }
        except Exception as e:
            return None

    def smart_extract(self, text):
        return self.extract_questions_from_text(text)