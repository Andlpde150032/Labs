# Hướng dẫn chi tiết Lab 07 & Lab 08 - Mini App Quản Lý Đơn Hàng

Tài liệu này giải thích chi tiết về logic mã nguồn, cách cài đặt môi trường và thực thi cho Lab 07 (Xây dựng Module Cập nhật Trạng thái Đơn hàng) và Lab 08 (Kiểm thử Module).

-----

## 🚀 Lab 07 – Module Cập nhật Trạng thái Đơn hàng

Mục tiêu của lab này là xây dựng logic nghiệp vụ cho chức năng **"Cập nhật Trạng thái Đơn hàng"**, bám sát theo Sơ đồ Tuần tự và kiến trúc `Controller -> Service`.

### 🧠 Giải thích Logic (`order_management_module.py`)

File này mô phỏng kiến trúc nhiều lớp để xử lý một yêu cầu nghiệp vụ.

#### 1\. Các Lớp (Classes)

  * **`NotificationService`**: Đóng vai trò giả lập một dịch vụ gửi thông báo. Trong một dự án thực tế, lớp này sẽ chứa code để gửi email, SMS hoặc thông báo đẩy (push notification). Ở đây, nó chỉ in một thông báo ra màn hình để xác nhận luồng hoạt động.
  * **`OrderService`**: Đây là nơi chứa logic nghiệp vụ cốt lõi. Hàm `update_order_status` của nó thực hiện một chuỗi các hành động quan trọng:
      * **Bắt đầu Giao dịch (Transaction):** Toàn bộ quá trình được bọc trong một transaction để đảm bảo tính nhất quán của dữ liệu. Nếu bất kỳ bước nào thất bại, toàn bộ thay đổi sẽ được hoàn tác (`rollback`).
      * **Truy vấn & Kiểm tra:** Lấy thông tin đơn hàng từ CSDL. Nếu không tìm thấy, nó sẽ báo lỗi và dừng lại.
      * **Cập nhật Dữ liệu:** Thực thi câu lệnh `UPDATE` để thay đổi trạng thái của đơn hàng trong CSDL.
      * **Gọi Dịch vụ khác:** Gọi đến `NotificationService` để thực hiện nhiệm vụ gửi thông báo.
      * **Hoàn tất Giao dịch:** Nếu mọi thứ suôn sẻ, nó sẽ `commit()` giao dịch để lưu các thay đổi.
  * **`OrderController`**: Lớp này hoạt động như một bộ điều phối. Nó nhận yêu cầu từ bên ngoài (ví dụ: từ giao diện người dùng), sau đó gọi đến phương thức phù hợp trong `OrderService` để xử lý và nhận lại kết quả.

### 🛠️ Hướng dẫn Cài đặt & Thực thi

1.  **Chuẩn bị Cơ sở dữ liệu:**
      * Đảm bảo MySQL Server của bạn đang hoạt động.
      * Sử dụng script SQL đã được cung cấp để tạo database `shop_order_management` và các bảng liên quan.
      * Thêm ít nhất một khách hàng, một người dùng và một đơn hàng mẫu để có dữ liệu thử nghiệm.
2.  **Cài đặt thư viện:** Mở terminal và chạy lệnh:
    ```bash
    pip install mysql-connector-python
    ```
3.  **Cấu hình kết nối:** Mở file `order_management_module.py` và cập nhật thông tin (`password` và `database`) trong từ điển `DB_CONFIG`.
4.  **Chạy chương trình:** Di chuyển đến thư mục chứa file và thực thi bằng lệnh:
    ```bash
    python order_management_module.py
    ```
    Kết quả trên màn hình sẽ hiển thị các log từ Controller, Service, và Notification Service, mô phỏng quá trình cập nhật thành công và thất bại.

-----

## 🔬 Lab 08 – Kiểm thử Module Quản lý Đơn hàng

Mục tiêu của lab này là viết các kịch bản kiểm thử đơn vị (Unit Test) để xác minh rằng lớp `OrderService` hoạt động đúng logic trong các kịch bản khác nhau mà không cần CSDL thật.

### 🧠 Giải thích Logic (`test_order_management.py`)

Chúng ta sử dụng `pytest` và `unittest.mock` để cô lập và kiểm thử logic nghiệp vụ.

#### 1\. Mocking (Giả lập)

Mocking cho phép chúng ta thay thế các thành phần phụ thuộc (như CSDL, dịch vụ bên ngoài) bằng các đối tượng giả mà chúng ta có thể kiểm soát hoàn toàn.

  * **`@pytest.fixture`**: Fixture `mock_services` thực hiện việc "vá" (`patch`) hai thành phần:
    1.  `get_db_connection`: Thay thế hàm kết nối CSDL thật bằng một đối tượng `MagicMock`.
    2.  `NotificationService`: Thay thế lớp dịch vụ thông báo thật bằng một `MagicMock`.
  * **Kiểm soát đối tượng giả:** Trong mỗi test case, chúng ta sẽ lập trình cho các đối tượng mock này. Ví dụ, chúng ta có thể ra lệnh cho `mock_cursor.fetchone()` trả về dữ liệu mẫu hoặc `None` để giả lập việc tìm thấy hoặc không tìm thấy đơn hàng.

#### 2\. Logic của các Test Case

Mỗi kịch bản kiểm thử một khía cạnh cụ thể của hàm `update_order_status`:

  * **`test_update_status_success`**: Kiểm tra luồng hoạt động thành công. Nó giả lập rằng đơn hàng được tìm thấy và câu lệnh `UPDATE` thành công. Sau đó, nó **khẳng định (assert)** rằng hàm trả về `True`, `commit()` được gọi, và `send_update_notification()` cũng được gọi.
  * **`test_update_status_order_not_found`**: Kiểm tra trường hợp `order_id` không tồn tại. Nó giả lập `fetchone()` trả về `None`. Sau đó, nó khẳng định rằng hàm trả về `False`, `rollback()` được gọi, và dịch vụ thông báo **không** được gọi.
  * **`test_update_status_db_error_on_update`**: Kiểm tra khả năng xử lý lỗi từ CSDL. Nó giả lập việc CSDL ném ra một ngoại lệ (`Exception`) trong quá trình `UPDATE`. Sau đó, nó khẳng định rằng hàm trả về `False` và `rollback()` được gọi.

### 🛠️ Hướng dẫn Cài đặt & Thực thi

1.  **Cấu trúc thư mục:** Đảm bảo các file lab 7 và lab 8 được đặt trong các thư mục riêng biệt (`lab07-module`, `lab08-testing`) nằm cùng cấp để việc import hoạt động chính xác.
2.  **Cài đặt thư viện:** Mở terminal và chạy lệnh:
    ```bash
    pip install pytest
    ```
3.  **Chạy kiểm thử:** Di chuyển đến thư mục `lab08-testing` và thực thi bằng lệnh:
    ```bash
    python -m pytest
    ```
    Kết quả mong đợi là một dòng màu xanh lá cây báo rằng tất cả **3 tests đã thành công (passed)**.