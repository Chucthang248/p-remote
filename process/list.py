import psutil

def list_running_applications():
    print("Danh sách các ứng dụng đang chạy:")
    for process in psutil.process_iter(['pid', 'name', 'username']):
        try:
            print(f"PID: {process.info['pid']}, Tên: {process.info['name']}, Người dùng: {process.info['username']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

list_running_applications()