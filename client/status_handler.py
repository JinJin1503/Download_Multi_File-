def update_status(filename, status, percent=None):
    if percent is not None:
        print(f"[{filename}] {status} - {percent:.2f}%")
    else:
        print(f"[{filename}] {status}")
