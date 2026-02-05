import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys

import client 
from shared.protocol import STATUS_OK
from download_status import DownloadStatus
import status_handler

# --- CẤU HÌNH MÀU SẮC ---
COLOR_BG = "#f4f6f9"
COLOR_WHITE = "#ffffff"
COLOR_BLUE = "#0d6efd"
COLOR_GREEN = "#198754"
COLOR_RED = "#dc3545"
COLOR_GRAY = "#6c757d"
COLOR_DARK = "#343a40"

class FileRow:
    def __init__(self, parent_frame, filename, index, app_ref):
        self.filename = filename
        self.app = app_ref
        self.internal_status = "READY" 
        
        self.wrapper = tk.Frame(parent_frame, bg=COLOR_WHITE)
        
        self.content_frame = tk.Frame(self.wrapper, bg=COLOR_WHITE, pady=8, padx=10)
        self.content_frame.pack(fill="x", expand=True)

        # Checkbox
        self.var_check = tk.BooleanVar()
        self.chk = tk.Checkbutton(self.content_frame, variable=self.var_check, bg=COLOR_WHITE, cursor="hand2")
        self.chk.pack(side="left")

        # Tên file
        self.lbl_name = tk.Label(self.content_frame, text=filename, width=30, anchor="w", 
                                 bg=COLOR_WHITE, font=("Segoe UI", 11))
        self.lbl_name.pack(side="left", padx=10)

        # Nút Hành động
        self.btn_action = tk.Button(self.content_frame, text="Download", bg=COLOR_BLUE, fg="white", 
                                    width=12, command=self.handle_action, relief="flat", 
                                    font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.btn_action.pack(side="left", padx=15)

        # Thanh tiến trình
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("green.Horizontal.TProgressbar", foreground=COLOR_GREEN, background=COLOR_GREEN)
        
        self.progress = ttk.Progressbar(self.content_frame, orient="horizontal", length=200, 
                                        mode="determinate", style="green.Horizontal.TProgressbar")
        self.progress.pack(side="left", padx=10, fill="x", expand=True)

        # Label trạng thái
        self.lbl_status = tk.Label(self.content_frame, text="Ready", width=15, anchor="e", 
                                   bg=COLOR_WHITE, fg=COLOR_GRAY, font=("Segoe UI", 9))
        self.lbl_status.pack(side="left", padx=5)
        
        # 2. Phần Đường Kẻ (Nằm dưới đáy Wrapper)
        self.separator = tk.Frame(self.wrapper, height=1, bg="#e0e0e0")
        self.separator.pack(fill="x", side="bottom")

    def handle_action(self):
        if self.internal_status == "SUCCESS":
            self.open_file()
        else:
            self.start_download()

    def start_download(self):
        self.btn_action.config(state="disabled", text="Connecting...", bg=COLOR_GRAY)
        self.update_gui_status(DownloadStatus.REQUESTING, 0)
        
        t = threading.Thread(target=client.download_file, args=(self.filename,))
        t.daemon = True
        t.start()
        self.app.update_stats()

    def update_gui_status(self, status_code, percent=None):
        self.internal_status = status_code
        
        display_text = status_code
        if percent is not None:
            self.progress["value"] = percent
            display_text = f"{percent}%"
        
        if status_code == DownloadStatus.SUCCESS:
            self.lbl_status.config(text="Completed", fg=COLOR_GREEN, font=("Segoe UI", 9, "bold"))
            self.btn_action.config(state="normal", text="Open File", bg=COLOR_GREEN, fg="white")
            self.progress["value"] = 100
            
        elif status_code == DownloadStatus.VERIFYING:
            self.lbl_status.config(text="Verifying...", fg="#fd7e14") # Màu cam
        
        elif status_code == DownloadStatus.CORRUPTED:
            self.lbl_status.config(text="File Corrupted", fg=COLOR_RED, font=("Segoe UI", 9, "bold"))
            self.btn_action.config(state="normal", text="Retry", bg=COLOR_BLUE, fg="white")
            self.progress["value"] = 0
            
        elif status_code in [DownloadStatus.ERROR, DownloadStatus.NOT_FOUND, DownloadStatus.IO_ERROR, DownloadStatus.DISCONNECT, DownloadStatus.TIMEOUT]:
            self.lbl_status.config(text=status_code, fg=COLOR_RED)
            self.btn_action.config(state="normal", text="Retry", bg=COLOR_BLUE, fg="white")
            
        elif status_code == DownloadStatus.DOWNLOADING:
            self.lbl_status.config(text=display_text, fg=COLOR_BLUE)
        else:
            self.lbl_status.config(text=display_text, fg=COLOR_GRAY)
            
        self.app.update_stats()

    def open_file(self):
        file_path = os.path.join(client.SAVE_DIR, self.filename)
        if not os.path.exists(file_path):
            messagebox.showerror("Lỗi", "File không tồn tại!")
            return
        try:
            if sys.platform == 'win32': os.startfile(file_path)
            else:
                import subprocess
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, file_path])
        except Exception as e:
            messagebox.showwarning("Lỗi", f"Không mở được file: {e}")

class DownloadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP File Manager")
        self.root.geometry("950x650") 
        self.root.configure(bg=COLOR_BG)

        self.file_rows = {}    
        self.all_filenames = [] 

        self.setup_ui()
        status_handler.set_callback(self.on_backend_update)
        
        self.root.after(500, self.refresh_server_files)

    def setup_ui(self):
        # HEADER
        header_frame = tk.Frame(self.root, bg=COLOR_BG, pady=15, padx=15)
        header_frame.pack(fill="x")

        self.lbl_title = tk.Label(header_frame, text="Server Files", bg=COLOR_BG, font=("Segoe UI", 16, "bold"), fg="#333")
        self.lbl_title.pack(side="left")

        search_frame = tk.Frame(header_frame, bg=COLOR_BG)
        search_frame.pack(side="left", padx=40, fill="x", expand=True)

        self.entry_search = tk.Entry(search_frame, font=("Segoe UI", 11), width=30)
        self.entry_search.pack(side="left", fill="x", expand=True)
        self.entry_search.bind("<Return>", lambda e: self.perform_search()) 

        btn_search = tk.Button(search_frame, text="Search", bg=COLOR_BLUE, fg="white", 
                               command=self.perform_search, font=("Segoe UI", 10))
        btn_search.pack(side="left", padx=5)

        self.btn_right = tk.Button(header_frame, text="↻ Refresh", bg="#6c757d", fg="white", 
                                   command=self.refresh_server_files, font=("Segoe UI", 10), padx=10)
        self.btn_right.pack(side="right")

        # BODY
        container = tk.Frame(self.root, bg=COLOR_BG)
        container.pack(fill="both", expand=True, padx=15, pady=5)

        self.canvas = tk.Canvas(container, bg=COLOR_WHITE, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.list_frame = tk.Frame(self.canvas, bg=COLOR_WHITE)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # FOOTER
        footer_frame = tk.Frame(self.root, bg="#e9ecef", height=50)
        footer_frame.pack(fill="x", side="bottom")

        self.lbl_stats = tk.Label(footer_frame, text="Ready", bg="#e9ecef", font=("Segoe UI", 10))
        self.lbl_stats.pack(side="left", padx=20, pady=15)

        btn_dl_all = tk.Button(footer_frame, text="Download Selected", bg=COLOR_GREEN, fg="white",
                               font=("Segoe UI", 10, "bold"), padx=15, command=self.download_selected)
        btn_dl_all.pack(side="right", padx=20, pady=10)

    def refresh_server_files(self):
        self.entry_search.delete(0, 'end')
        self.btn_right.config(text="↻ Refresh", command=self.refresh_server_files, bg="#6c757d")
        
        for widget in self.list_frame.winfo_children(): widget.destroy()
        self.file_rows.clear()
        self.all_filenames.clear()
        
        def fetch():
            files = client.get_server_file_list()
            self.root.after(0, lambda: self.init_full_list(files))
        
        threading.Thread(target=fetch, daemon=True).start()

    def init_full_list(self, files):
        if not files:
            tk.Label(self.list_frame, text="(Không tìm thấy file nào hoặc lỗi kết nối)", 
                     bg=COLOR_WHITE, fg=COLOR_RED, font=("Segoe UI", 11), pady=20).pack()
            self.update_stats()
            return

        for f in files:
            filename = f.strip()
            if filename:
                row = FileRow(self.list_frame, filename, len(self.file_rows), self)
                self.file_rows[filename] = row
                self.all_filenames.append(filename)
                row.wrapper.pack(fill="x", pady=1, expand=True)

        self.update_stats()

    def perform_search(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            return 
        
        self.btn_right.config(text="← Back to List", command=self.back_to_full_list, bg=COLOR_DARK)
        
        keywords = [k.strip() for k in query.split(",")]
        
        has_result = False
        for filename in self.all_filenames:
            row = self.file_rows[filename]
            
            match = False
            for k in keywords:
                if k and k in filename.lower():
                    match = True
                    break
            
            if match:
                row.wrapper.pack(fill="x", pady=1, expand=True) 
                has_result = True
            else:
                row.wrapper.pack_forget()

        if not has_result:
             messagebox.showinfo("Search", "Không tìm thấy file nào khớp!")

    def back_to_full_list(self):
        self.entry_search.delete(0, 'end')
        self.btn_right.config(text="↻ Refresh", command=self.refresh_server_files, bg="#6c757d")
        
        for filename in self.all_filenames:
            row = self.file_rows[filename]
            row.wrapper.pack(fill="x", pady=1, expand=True)

    def download_selected(self):
        count = 0
        for row in self.file_rows.values():
            if row.wrapper.winfo_ismapped() and row.var_check.get() and row.internal_status != "SUCCESS":
                row.start_download()
                count += 1
        if count == 0:
            messagebox.showinfo("Info", "Hãy chọn file cần tải.")

    def update_stats(self):
        running = sum(1 for r in self.file_rows.values() if r.internal_status in ["DOWNLOADING", "REQUESTING"])
        completed = sum(1 for r in self.file_rows.values() if r.internal_status == "SUCCESS")
        total = len(self.file_rows)
        self.lbl_stats.config(text=f"Total Files: {total} | Running: {running} | Completed: {completed}")

    def on_backend_update(self, filename, status, percent):
        self.root.after(0, lambda: self._safe_update_ui(filename, status, percent))

    def _safe_update_ui(self, filename, status, percent):
        if filename in self.file_rows:
            self.file_rows[filename].update_gui_status(status, percent)

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloadApp(root)
    root.mainloop()