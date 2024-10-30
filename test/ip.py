import socket

def get_local_ip():
    # Tạo một socket tạm để xác định địa chỉ IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Kết nối đến một địa chỉ ngoài mạng (ví dụ: Google DNS)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]  # Lấy IP từ socket
    finally:
        s.close()
    return local_ip

# # Sử dụng hàm này để lấy IP
# server_ip = get_local_ip()
# print("Địa chỉ IP nội bộ của server là:", server_ip)
