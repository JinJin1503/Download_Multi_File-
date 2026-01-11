import os
import sys

# Thêm thư mục cha của dự án vào sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))

import socket
from shared.protocol import Protocol

def test_protocol():
    print("--- CLIENT TEST PHASE 2 ---")
    
    # TEST CASE 1: Yêu cầu file CÓ tồn tại (Bạn nhớ tạo file này)
    file_exists = "test_protocol.txt" 
    # TEST CASE 2: Yêu cầu file KHÔNG tồn tại
    file_not_exists = "khong_co_file_nay.xyz"
    
    # Chọn 1 trong 2 file trên để test
    target_file = file_exists 
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 5000))
        
        # 1. Gửi yêu cầu
        req = Protocol.create_download_request(target_file)
        client.sendall(Protocol.encode_message(req))
        print(f"[Client] Gửi yêu cầu: {req}")
        
        # 2. Nhận phản hồi Protocol từ Server
        response = Protocol.receive_message(client)
        print(f"[Client] Server phản hồi GỐC: {response}")
        
        # 3. Kiểm tra logic Protocol
        if response:
            if "FILE" in response:
                print("✅ TEST PASS: Server báo CÓ file")
                # Thử parse header
                name, size, status = Protocol.parse_file_header(response)
                print(f"   Chi tiết: Name={name}, Size={size}, Status={status}")
                
            elif "ERROR" in response:
                print("✅ TEST PASS: Server báo LỖI 404")
            else:
                print("❌ TEST FAIL: Phản hồi lạ, không đúng protocol.")
        else:
            print("❌ TEST FAIL: Không nhận được phản hồi.")
            
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Tạo file giả để test trường hợp có file
    with open("test_protocol.txt", "w") as f:
        f.write("Day la file test giao thuc.")
        
    test_protocol()