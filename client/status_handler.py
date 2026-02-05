import threading

# Biến chứa hàm của GUI
_gui_callback = None
lock = threading.Lock()

def set_callback(func):
    """GUI sẽ gọi hàm này để đăng ký nhận thông báo"""
    global _gui_callback
    with lock:
        _gui_callback = func

def update_status(filename, status, percent=None):
    # 1. Báo cho GUI biết (nếu GUI đang chạy)
    with lock:
        if _gui_callback:
            try:
                # Gọi hàm update của GUI
                _gui_callback(filename, status, percent)
            except Exception as e:
                print(f"Lỗi callback GUI: {e}")

    # 2. In ra màn hình console (để debug)
    if percent is not None:
        print(f"[{filename}] {status} - {percent}%")
    else:
        print(f"[{filename}] {status}")