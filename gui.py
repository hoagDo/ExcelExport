# gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import os
import re
from text_processor import TextProcessor
from excel_handler import ExcelHandler
from core.deduplicator import Deduplicator
from core.logger import Logger

class QuestionExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Công cụ Trích xuất Câu hỏi từ Văn bản sang Excel")
        self.root.geometry("1000x700")
        
        # Khởi tạo các component
        self.text_processor = TextProcessor()
        self.excel_handler = ExcelHandler()
        self.logger = Logger()
        self.deduplicator = Deduplicator(policy='allow', logger=self.logger)  # Mặc định là allow để test
        
        # Queue cho thread
        self.queue = queue.Queue()
        
        # Biến lưu trữ
        self.questions = []
        self.stats = {'written': 0, 'skipped': 0, 'merged': 0}
        
        # Thiết lập giao diện
        self.setup_ui()
        
        # Bắt đầu kiểm tra queue
        self.root.after(100, self.check_queue)
    
    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cấu hình grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Tiêu đề
        title_label = ttk.Label(
            main_frame, 
            text="CÔNG CỤ TRÍCH XUẤT CÂU HỎI SANG EXCEL",
            font=('Helvetica', 16, 'bold'),
            foreground='#366092'
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Khung nhập văn bản
        input_frame = ttk.LabelFrame(main_frame, text="Nhập văn bản", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        self.text_input = scrolledtext.ScrolledText(
            input_frame, 
            wrap=tk.WORD,
            width=80,
            height=15,
            font=('Consolas', 10)
        )
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Nút chức năng
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        buttons = [
            ("📋 Dán từ Clipboard", self.paste_from_clipboard),
            ("📝 Tải Ví dụ Mẫu", self.load_example),
            ("🐛 Debug", self.debug_extraction),
            ("🗑️ Xóa Tất Cả", self.clear_all),
            ("ℹ️ Thông tin Template", self.show_template_info),
            ("⚙️ Cài đặt", self.open_settings),
            ("🔄 Xử lý & Xuất Excel", self.process_and_export)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.grid(row=0, column=i, padx=2)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Sẵn sàng")
        self.status_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Khung preview
        preview_frame = ttk.LabelFrame(main_frame, text="Thông tin xử lý", padding="10")
        preview_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Notebook cho nhiều tab preview
        self.notebook = ttk.Notebook(preview_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tab tổng quan
        overview_frame = ttk.Frame(self.notebook)
        self.overview_text = scrolledtext.ScrolledText(
            overview_frame,
            wrap=tk.WORD,
            width=60,
            height=10,
            state='disabled'
        )
        self.overview_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(overview_frame, text="Tổng quan")
        
        # Tab cấu trúc template
        template_frame = ttk.Frame(self.notebook)
        template_text = scrolledtext.ScrolledText(
            template_frame,
            wrap=tk.WORD,
            width=60,
            height=10,
            state='disabled'
        )
        template_text.insert('1.0', self.get_template_structure())
        template_text.config(state='disabled')
        template_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(template_frame, text="Cấu trúc Template")
        
        # Tab xem trước
        preview_text_frame = ttk.Frame(self.notebook)
        self.preview_text = scrolledtext.ScrolledText(
            preview_text_frame,
            wrap=tk.WORD,
            width=60,
            height=10,
            state='disabled'
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(preview_text_frame, text="Xem trước")
        
        # Footer
        footer_label = ttk.Label(
            main_frame,
            text="© 2024 Công cụ Trích xuất Câu hỏi | Phiên bản 1.0",
            foreground='gray'
        )
        footer_label.grid(row=6, column=0, columnspan=3, pady=(10, 0))
    
    def paste_from_clipboard(self):
        try:
            text = self.root.clipboard_get()
            self.text_input.delete('1.0', tk.END)
            self.text_input.insert('1.0', text)
            self.update_status("Đã dán văn bản từ clipboard")
        except:
            messagebox.showerror("Lỗi", "Không thể lấy dữ liệu từ clipboard")
    
    def load_example(self):
        example = """Câu 23. Điểm khác biệt ... về việc thực hiện chủ trương phát triển đất nước của Xiêm so với Việt Nam cuối thể kỉ XIX là gì?
A. Các sĩ phu tân học là người đề xướng cải cách.
B. Các đề xướng cải cách chưa hệ thống, chưa toàn diện.
C. Đóng cửa, bế quan tỏa cảng với các nước phương Tây.
D. Tiến hành cải cách theo khuôn mẫu các nước phương Tây.

Câu 1. Một trong những nội dung cải cách về quân sự của vua Ra-ma V là . . 
A. xây dựng quân đội theo kiểu phương Tây.
B. duy trì chế độ quân dịch cũ.
C. bãi bỏ chế độ cung đình.
D. tăng cường quân đội phong kiến.

Câu 2. Nội dung nào dưới đây phản ánh đúng chính sách cải cách của Xiêm?
A. Tiếp tục duy trì chế độ nô lệ.
B. Tăng cường quan hệ với phương Đông.
C. Cải cách theo mô hình phương Tây.
D. Đóng cửa với các nước châu Âu."""
        
        self.text_input.delete('1.0', tk.END)
        self.text_input.insert('1.0', example)
        self.update_status("Đã tải ví dụ mẫu")
    
    def clear_all(self):
        self.text_input.delete('1.0', tk.END)
        self.questions.clear()
        self.update_overview()
        self.update_status("Đã xóa tất cả nội dung")
    
    def show_template_info(self):
        info = """TEMPLATE: TrachNG_CN.xlsx

CẤU TRÚC CỘT:
A: Question Text      - Nội dung câu hỏi
B: Question Type      - Loại câu hỏi (Multiple Choice)
C: Option 1           - Lựa chọn A
D: Option 2           - Lựa chọn B
E: Option 3           - Lựa chọn C
F: Option 4           - Lựa chọn D
G: Correct Answer     - Đáp án đúng
H: Time in seconds    - Thời gian làm bài
I: Image Link         - Link hình ảnh
J: Answer explanation - Giải thích đáp án

LƯU Ý:
- Dữ liệu được ghi từ dòng 3
- Template tự động tạo nếu chưa tồn tại
- Hỗ trợ xử lý dấu ba chấm (... . . ..)
- Kiểm tra trùng lặp thông minh"""
        
        messagebox.showinfo("Thông tin Template", info)
    
    def open_settings(self):
        # Tạo cửa sổ cài đặt
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Cài đặt")
        settings_window.geometry("400x300")
        
        ttk.Label(settings_window, text="Chính sách xử lý trùng lặp:").pack(pady=10)
        
        policy_var = tk.StringVar(value=self.deduplicator.policy)
        
        policies = [
            ("Bỏ qua (Skip)", "skip"),
            ("Thêm hậu tố (Append suffix)", "append"),
            ("Cho phép trùng (Allow duplicates)", "allow")
        ]
        
        for text, value in policies:
            rb = ttk.Radiobutton(
                settings_window,
                text=text,
                variable=policy_var,
                value=value
            )
            rb.pack(anchor=tk.W, padx=20)
        
        def save_settings():
            self.deduplicator.policy = policy_var.get()
            settings_window.destroy()
            self.update_status("Đã lưu cài đặt")
        
        ttk.Button(settings_window, text="Lưu", command=save_settings).pack(pady=20)
    
    def debug_extraction(self):
        """Phương thức debug để kiểm tra trích xuất"""
        text = self.text_input.get('1.0', tk.END)
        
        if not text.strip():
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập văn bản!")
            return
        
        # Hiển thị cửa sổ debug
        debug_window = tk.Toplevel(self.root)
        debug_window.title("Debug - Kiểm tra trích xuất")
        debug_window.geometry("800x600")
        
        # Text widget để hiển thị kết quả
        debug_text = scrolledtext.ScrolledText(debug_window, wrap=tk.WORD, width=90, height=30)
        debug_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Phân tích văn bản
        debug_text.insert('1.0', "=== PHÂN TÍCH VĂN BẢN ===\n\n")
        debug_text.insert('end', f"Độ dài văn bản: {len(text)} ký tự\n")
        
        # Kiểm tra xem có pattern "Câu X." không
        matches = re.findall(r'Câu\s*\d+[\.:\)]', text, re.IGNORECASE)
        debug_text.insert('end', f"\nTìm thấy {len(matches)} pattern 'Câu X.' trong văn bản\n")
        for i, match in enumerate(matches[:10], 1):
            debug_text.insert('end', f"  {i}. {match}\n")
        
        # Kiểm tra bằng phương pháp smart_extract
        debug_text.insert('end', "\n=== KẾT QUẢ TRÍCH XUẤT ===\n")
        
        try:
            if hasattr(self.text_processor, 'smart_extract'):
                questions = self.text_processor.smart_extract(text)
                debug_text.insert('end', f"\nSố câu hỏi trích xuất được: {len(questions)}\n")
                
                if questions:
                    for i, q in enumerate(questions, 1):
                        debug_text.insert('end', f"\n--- Câu {i} ---\n")
                        debug_text.insert('end', f"Question Text: {q['question_text'][:150]}...\n")
                        debug_text.insert('end', f"Options count: {len([opt for opt in q['options'] if opt])}\n")
                        for j, opt in enumerate(q['options']):
                            if opt and opt.strip():
                                debug_text.insert('end', f"  {chr(65+j)}. {opt[:80]}...\n")
                else:
                    debug_text.insert('end', "\nKHÔNG TÌM THẤY CÂU HỎI NÀO!\n")
                    
                    # Kiểm tra lý do
                    debug_text.insert('end', "\n=== PHÂN TÍCH LỖI ===\n")
                    
                    # Kiểm tra nếu văn bản có chứa "Câu" nhưng không phải định dạng đúng
                    if "Câu" in text:
                        debug_text.insert('end', "Tìm thấy từ 'Câu' trong văn bản nhưng không trích xuất được.\n")
                        debug_text.insert('end', "Có thể do định dạng không đúng.\n")
                    
                    # Hiển thị mẫu văn bản để kiểm tra
                    debug_text.insert('end', "\n=== MẪU VĂN BẢN (100 ký tự đầu) ===\n")
                    debug_text.insert('end', text[:100] + "...\n")
            else:
                debug_text.insert('end', "Phương thức smart_extract không tồn tại!\n")
        except Exception as e:
            debug_text.insert('end', f"Lỗi khi trích xuất: {str(e)}\n")
            import traceback
            debug_text.insert('end', f"\nTraceback:\n{traceback.format_exc()}")
    
    def process_and_export(self):
        text = self.text_input.get('1.0', tk.END)
        if not text.strip():
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập văn bản!")
            return
        
        # Reset stats
        self.stats = {'written': 0, 'skipped': 0, 'merged': 0}
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=self._process_thread, args=(text,))
        thread.daemon = True
        thread.start()
    
    def _process_thread(self, text):
        self.queue.put(('status', "Đang xử lý văn bản..."))
        self.queue.put(('progress', 10))
        
        try:
            # Trích xuất câu hỏi bằng smart_extract
            if hasattr(self.text_processor, 'smart_extract'):
                raw_questions = self.text_processor.smart_extract(text)
            else:
                # Fallback nếu không có smart_extract
                raw_questions = self.text_processor.extract_questions_from_text(text)
            
            if not raw_questions:
                self.queue.put(('error', "Không tìm thấy câu hỏi nào trong văn bản!"))
                self.queue.put(('progress', 100))
                return
            
            self.queue.put(('status', f"Đã trích xuất {len(raw_questions)} câu hỏi"))
            self.queue.put(('progress', 40))
            
            # Xử lý trùng lặp
            processed_questions = []
            
            for raw_q in raw_questions:
                if not raw_q:
                    continue
                    
                result = self.deduplicator.add_question(
                    raw_q['question_text'],
                    raw_q['options']
                )
                
                if result:
                    processed_questions.append({
                        'question_text': result[0],
                        'options': result[1]
                    })
                    self.stats['written'] += 1
                else:
                    self.stats['skipped'] += 1
            
            if not processed_questions:
                self.queue.put(('error', "Không có câu hỏi nào được xử lý (có thể do trùng lặp)!"))
                self.queue.put(('progress', 100))
                return
            
            self.queue.put(('progress', 70))
            
            # Xuất Excel
            export_result = self.excel_handler.write_questions(processed_questions)
            
            self.queue.put(('progress', 90))
            
            # Xuất summary
            summary_path = self.excel_handler.export_summary(processed_questions, self.stats)
            
            self.queue.put(('progress', 100))
            self.queue.put(('status', f"Đã xuất {len(processed_questions)} câu hỏi sang Excel"))
            
            # Cập nhật UI
            self.questions = processed_questions
            self.queue.put(('update_ui', processed_questions))
            
            # Ghi log
            self.logger.log_export_stats(self.stats)
            
            # Hiển thị thông báo thành công
            self.queue.put(('message', 
                f"Xuất thành công!\n\n"
                f"• Câu hỏi đã trích xuất: {len(raw_questions)}\n"
                f"• Câu hỏi đã ghi: {self.stats['written']}\n"
                f"• Câu hỏi bị bỏ qua: {self.stats['skipped']}\n"
                f"• File Excel: {export_result['output_path']}\n"
                f"• File Summary: {summary_path}"
            ))
            
        except Exception as e:
            self.queue.put(('error', f"Lỗi xử lý: {str(e)}"))
            import traceback
            traceback.print_exc()
    
    def update_status(self, message):
        self.status_label.config(text=message)
    
    def update_overview(self):
        text = f"""TỔNG QUAN XỬ LÝ

Số câu hỏi đã trích xuất: {len(self.questions)}
Số câu hỏi đã ghi: {self.stats['written']}
Số câu bị bỏ qua: {self.stats['skipped']}
Số câu được merge: {self.stats['merged']}

CHÍNH SÁCH XỬ LÝ TRÙNG LẶP: {self.deduplicator.policy.upper()}

VÍ DỤ CÂU HỎI ĐÃ XỬ LÝ:"""
        
        if self.questions:
            sample = self.questions[0]
            text += f"\n\nCâu hỏi: {sample['question_text'][:100]}..."
            for i, opt in enumerate(sample['options']):
                if opt and opt.strip():
                    text += f"\n{chr(65+i)}. {opt[:50]}..."
        
        self.overview_text.config(state='normal')
        self.overview_text.delete('1.0', tk.END)
        self.overview_text.insert('1.0', text)
        self.overview_text.config(state='disabled')
    
    def update_preview(self, questions):
        if not questions:
            return
        
        preview_text = "CÂU HỎI ĐÃ XỬ LÝ:\n\n"
        for i, q in enumerate(questions[:3], 1):  # Hiển thị 3 câu đầu
            preview_text += f"{i}. {q['question_text'][:80]}...\n"
            for j, opt in enumerate(q['options']):
                if opt and opt.strip():
                    preview_text += f"   {chr(65+j)}. {opt[:50]}...\n"
            preview_text += "\n"
        
        self.preview_text.config(state='normal')
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert('1.0', preview_text)
        self.preview_text.config(state='disabled')
    
    def get_template_structure(self):
        return """CẤU TRÚC TEMPLATE EXCEL:

┌─────────┬───────────────────────┬─────────────────┐
│ Cột     │ Tiêu đề              │ Mô tả           │
├─────────┼───────────────────────┼─────────────────┤
│ A       │ Question Text        │ Nội dung câu hỏi│
│ B       │ Question Type        │ Multiple Choice │
│ C       │ Option 1             │ Lựa chọn A      │
│ D       │ Option 2             │ Lựa chọn B      │
│ E       │ Option 3             │ Lựa chọn C      │
│ F       │ Option 4             │ Lựa chọn D      │
│ G       │ Correct Answer       │ Đáp án đúng     │
│ H       │ Time in seconds      │ Thời gian       │
│ I       │ Image Link           │ Link hình ảnh   │
│ J       │ Answer explanation   │ Giải thích      │
└─────────┴───────────────────────┴─────────────────┘

• Dữ liệu được ghi từ dòng 3
• Header ở dòng 1-2
• Tự động tìm dòng trống"""
    
    def check_queue(self):
        """Kiểm tra queue - SỬA LỖI RECURSION"""
        try:
            # Xử lý tất cả message có sẵn trong queue
            while True:
                try:
                    msg_type, data = self.queue.get_nowait()
                    
                    if msg_type == 'status':
                        self.update_status(data)
                    elif msg_type == 'progress':
                        self.progress_var.set(data)
                    elif msg_type == 'update_ui':
                        self.questions = data
                        self.update_overview()
                        self.update_preview(data)
                    elif msg_type == 'message':
                        messagebox.showinfo("Thành công", data)
                    elif msg_type == 'error':
                        messagebox.showerror("Lỗi", data)
                    
                    self.queue.task_done()
                except queue.Empty:
                    break
        except Exception as e:
            print(f"Lỗi trong check_queue: {e}")
        
        # Lên lịch kiểm tra lại sau 100ms
        self.root.after(100, self.check_queue)


def main():
    root = tk.Tk()
    app = QuestionExtractorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()