"""
Protocol hop dong giao thuc Client - Server
"""

STATUS_OK = "200"
STATUS_NOT_FOUND = "404"

CMD_DOWNLOAD = "DOWNLOAD"
CMD_FILE = "FILE"
CMD_ERROR = "ERROR"

SEPARATOR = "|"
BUFFER_SIZE = 4096


class Protocol:

    # -------- CLIENT -> SERVER --------
    @staticmethod
    def create_download_request(filename):
        # DOWNLOAD|filename
        return f"{CMD_DOWNLOAD}{SEPARATOR}{filename}"

    @staticmethod
    def parse_download_request(message):
        parts = message.split(SEPARATOR)
        if len(parts) != 2 or parts[0] != CMD_DOWNLOAD:
            return None
        return parts[1]


    # -------- SERVER -> CLIENT --------
    @staticmethod
    def create_file_header(filename, filesize):
        # FILE|filename|SIZE|filesize|STATUS|200
        return f"{CMD_FILE}{SEPARATOR}{filename}{SEPARATOR}SIZE{SEPARATOR}{filesize}{SEPARATOR}STATUS{SEPARATOR}{STATUS_OK}"

    @staticmethod
    def create_error_message(filename):
        # ERROR|filename|404
        return f"{CMD_ERROR}{SEPARATOR}{filename}{SEPARATOR}{STATUS_NOT_FOUND}"

    @staticmethod
    def parse_file_header(message):
        try:
            parts = message.split(SEPARATOR)
            if parts[0] != CMD_FILE:
                return None, None, None
            filename = parts[1]
            filesize = int(parts[3])
            status = parts[5]
            return filename, filesize, status
        except:
            return None, None, None


    # -------- COMMON --------
    @staticmethod
    def encode_message(message):
        data = message.encode("utf-8")
        length = len(data)
        return length.to_bytes(8, "big") + data

    @staticmethod
    def receive_message(sock):
        header = sock.recv(8)
        if not header:
            return None
        length = int.from_bytes(header, "big")

        data = b''
        while len(data) < length:
            chunk = sock.recv(min(BUFFER_SIZE, length - len(data)))
            if not chunk:
                return None
            data += chunk

        return data.decode("utf-8")

#-----------CLIENT NHẬN FILE --------------
    @staticmethod
    def receive_file_content(sock, file_handle, filesize):
        """
        Hàm nhận dữ liệu file và ghi trực tiếp vào file_handle
        Trả về: True nếu nhận đủ, False nếu mất kết nối giữa chừng
        """
        received = 0
        try:
            while received < filesize:
                # Tính toán lượng byte cần nhận (không quá BUFFER_SIZE)
                chunk_size = min(BUFFER_SIZE, filesize - received)

                chunk = sock.recv(chunk_size)
                if not chunk:
                    return False # Mất kết nối đột ngột

                file_handle.write(chunk)
                received += len(chunk)
            return True
        except Exception as e:
            print(f"Lỗi khi nhận data: {e}")
            return False
