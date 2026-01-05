"""
Định nghĩa giao thức truyền dữ liệu giữa Client và Server
"""

# Status codes
STATUS_OK = "200"
STATUS_NOT_FOUND = "404"
STATUS_SERVER_ERROR = "500"

# Commands
CMD_DOWNLOAD = "DOWNLOAD"
CMD_FILE = "FILE"
CMD_END_FILE = "END_FILE"
CMD_ERROR = "ERROR"

# Buffer size
BUFFER_SIZE = 4096

# Separators
SEPARATOR = "|"
FILE_LIST_SEPARATOR = ","

class Protocol:
    """Xử lý giao thức truyền dữ liệu"""

    @staticmethod
    def create_download_request(file_list):
        """
        Tạo yêu cầu download
        Format: DOWNLOAD|file1.txt,file2.pdf
        """
        files = FILE_LIST_SEPARATOR.join(file_list)
        return f"{CMD_DOWNLOAD}{SEPARATOR}{files}"

    @staticmethod
    def parse_download_request(message):
        """
        Phân tích yêu cầu download
        Returns: list of filenames
        """
        try:
            parts = message.split(SEPARATOR)
            if parts[0] != CMD_DOWNLOAD:
                return None
            files = parts[1].split(FILE_LIST_SEPARATOR)
            return [f.strip() for f in files if f.strip()]
        except:
            return None

    @staticmethod
    def create_file_header(filename, filesize, status=STATUS_OK):
        """
        Tạo header cho file
        Format: FILE|filename|SIZE|filesize|STATUS|200
        """
        return f"{CMD_FILE}{SEPARATOR}{filename}{SEPARATOR}SIZE{SEPARATOR}{filesize}{SEPARATOR}STATUS{SEPARATOR}{status}"

    @staticmethod
    def parse_file_header(message):
        """
        Phân tích header file
        Returns: (filename, filesize, status)
        """
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

    @staticmethod
    def create_error_message(filename, error_msg):
        """
        Tạo thông báo lỗi
        Format: ERROR|filename|error_message
        """
        return f"{CMD_ERROR}{SEPARATOR}{filename}{SEPARATOR}{error_msg}"

    @staticmethod
    def create_end_message():
        """Tạo thông báo kết thúc file"""
        return CMD_END_FILE

    @staticmethod
    def encode_message(message):
        """Mã hóa message thành bytes với độ dài cố định ở đầu"""
        msg_bytes = message.encode('utf-8')
        msg_length = len(msg_bytes)
        # 8 bytes cho độ dài (fixed header)
        header = msg_length.to_bytes(8, byteorder='big')
        return header + msg_bytes

    @staticmethod
    def receive_message(sock):
        """Nhận message có độ dài cố định ở đầu"""
        # Nhận 8 bytes header
        header = b''
        while len(header) < 8:
            chunk = sock.recv(8 - len(header))
            if not chunk:
                return None
            header += chunk

        msg_length = int.from_bytes(header, byteorder='big')

        # Nhận message
        message = b''
        while len(message) < msg_length:
            chunk = sock.recv(min(msg_length - len(message), BUFFER_SIZE))
            if not chunk:
                return None
            message += chunk

        return message.decode('utf-8')