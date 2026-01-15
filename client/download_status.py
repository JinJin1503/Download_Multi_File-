class DownloadStatus:
    CONNECTING = "CONNECTING"
    REQUESTING = "REQUESTING"
    DOWNLOADING = "DOWNLOADING"
    SUCCESS = "SUCCESS"
    NOT_FOUND = "NOT_FOUND"
    ERROR = "ERROR"
    TIMEOUT     = "TIMEOUT"       # Het thoi gian
    DISCONNECT  = "DISCONNECT"    # Server ngat ket noi
    IO_ERROR    = "IO_ERROR"      # Loi ghi file