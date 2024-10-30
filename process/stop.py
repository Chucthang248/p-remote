import psutil

def list_running_applications():
    print("Danh sách các ứng dụng đang chạy:")
    for process in psutil.process_iter(['pid', 'name', 'username']):
        try:
            print(f"PID: {process.info['pid']}, Tên: {process.info['name']}, Người dùng: {process.info['username']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def stop_application(app_name):
    stopped = False
    for process in psutil.process_iter(['pid', 'name']):
        try:
            if process.info['name'] == app_name:
                print(f"Dừng ứng dụng {app_name} (PID: {process.info['pid']})")
                process.kill()  # Dừng tiến trình một cách mạnh hơn
                stopped = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    if stopped:
        print(f"Đã dừng tất cả các tiến trình của {app_name}")
    else:
        print(f"Không tìm thấy ứng dụng '{app_name}' đang chạy.")

# Hiển thị danh sách các ứng dụng đang chạy
list_running_applications()

# Nhập tên ứng dụng cần dừng
app_name = input("Nhập tên ứng dụng cần dừng (ví dụ: opera.exe): ")
stop_application(app_name)
