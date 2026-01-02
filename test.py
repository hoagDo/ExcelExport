# test_v7.py
import sys
import io
import os

if sys.stdout:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from text_processor import TextProcessor

# Dữ liệu bạn cung cấp
TEST_DATA = """
1. 'I haven't got my phone.' 'That's OK. __________ you mine.'
A. I’m going to lend
B. lend
C. I’ll lend
2. It's Julia's birthday next week, so __________ her some flowers.
A. we’re going to buy
B. we’ll buy
C. buy
15.17__________ anything like this before?
3
A. Have you seen
B. Did you see
C. Did you seen
17. 9I __________ him behave like this before.
A. see
B. never saw
C. ‘ve never seen
"""

def run_test():
    print("="*60)
    print("TEST FIX LỖI THIẾU CÂU C & ĐỊNH DẠNG SỐ")
    print("="*60)
    
    processor = TextProcessor()
    questions = processor.extract_questions_from_text(TEST_DATA)
    
    print(f"👉 Tìm thấy: {len(questions)} câu hỏi.\n")
    
    for q in questions:
        print(f"🟦 [CÂU {q['question_number']}]")
        print(f"   🔻 Nội dung: \"{q['question_text']}\"")
        
        opts = q['options']
        # In các đáp án tìm được
        print(f"   ✅ A: {opts[0]}")
        print(f"   ✅ B: {opts[1]}")
        print(f"   ✅ C: {opts[2]}")
        print(f"   ✅ D: {opts[3]}")
        
        if opts[2]: # Nếu có đáp án C
             print("   🌟 TRẠNG THÁI: ĐÃ LẤY ĐƯỢC CÂU C!")
        else:
             print("   ❌ LỖI: Vẫn mất câu C")
             
        print("-" * 50)

if __name__ == "__main__":
    run_test()