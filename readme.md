# Hướng dẫn chi tiết Lab 07 & Lab 08 - ATM Mini-Project

Tài liệu này giải thích chi tiết về logic mã nguồn, cách cài đặt môi trường và thực thi cho Lab 07 (Xây dựng Module Rút tiền) và Lab 08 (Kiểm thử Module).

## 🚀 Lab 07 – Phát triển Module Rút tiền

Mục tiêu của lab này là xây dựng logic nghiệp vụ cho chức năng rút tiền, tương tác trực tiếp với cơ sở dữ liệu MySQL.

### 🧠 Giải thích Logic (withdraw_module.py)

File này chứa hai chức năng chính: xác thực mã PIN và xử lý giao dịch rút tiền.

#### 1. Hàm verify_pin(card_no, pin)

Hàm này chịu trách nhiệm kiểm tra xem mã PIN do người dùng nhập có khớp với mã PIN được lưu trong cơ sở dữ liệu hay không.

**Bảo mật:** Để đảm bảo an toàn, chúng ta không bao giờ lưu mã PIN ở dạng văn bản gốc. Thay vào đó, ta lưu một chuỗi đã được "băm" (hashed) bằng thuật toán an toàn như SHA-256.

**Quy trình logic:**

1. Hàm nhận `card_no` và `pin` (dạng text) làm đầu vào.
2. Nó kết nối tới CSDL và truy vấn bảng `cards` để lấy chuỗi `pin_hash` tương ứng với `card_no`.
3. Nó sử dụng thư viện `hashlib` để băm chuỗi `pin` mà người dùng nhập theo cùng thuật toán SHA-256.
4. Cuối cùng, nó so sánh hai chuỗi hash này. Nếu chúng khớp nhau, hàm trả về `True`; nếu không, trả về `False`.

#### 2. Hàm withdraw(card_no, amount)

Đây là hàm cốt lõi, mô phỏng toàn bộ quy trình rút tiền tại ATM. Logic của nó phải đảm bảo tính toàn vẹn dữ liệu (Data Integrity).

**Giao dịch (Transaction):** Toàn bộ quy trình rút tiền được bọc trong một giao dịch CSDL. Điều này có nghĩa là tất cả các bước (trừ tiền, ghi log) phải thành công, nếu một bước thất bại, toàn bộ sẽ được hủy bỏ (rollback) để CSDL trở về trạng thái ban đầu. Điều này ngăn chặn các lỗi như trừ tiền trong tài khoản nhưng không ghi lại giao dịch.

**Quy trình logic:**

1. Bắt đầu một giao dịch (`conn.start_transaction()`).
2. Truy vấn CSDL để lấy `balance` (số dư) của tài khoản liên kết với `card_no`. Câu lệnh `FOR UPDATE` được sử dụng để khóa hàng dữ liệu này lại, ngăn các giao dịch khác đọc hoặc thay đổi nó cùng lúc, tránh xung đột.
3. Kiểm tra số dư: So sánh `amount` (số tiền muốn rút) với `balance`. Nếu số dư không đủ, một ngoại lệ (Exception) sẽ được ném ra, và quy trình sẽ nhảy đến khối `except`.
4. Cập nhật số dư: Nếu đủ tiền, thực hiện câu lệnh `UPDATE` để trừ số tiền đã rút khỏi tài khoản.
5. Ghi Log: Thực hiện câu lệnh `INSERT` để tạo một bản ghi mới trong bảng `transactions`, lưu lại chi tiết giao dịch.
6. Hoàn tất: Nếu tất cả các bước trên thành công, gọi `conn.commit()` để xác nhận và lưu vĩnh viễn tất cả các thay đổi vào CSDL.
7. Xử lý lỗi: Nếu có bất kỳ lỗi nào xảy ra ở bất kỳ bước nào, khối `except` sẽ được kích hoạt, gọi `conn.rollback()` để hủy bỏ tất cả các thay đổi đã thực hiện trong giao dịch.

### 🛠️ Hướng dẫn Cài đặt & Thực thi

**Chuẩn bị Cơ sở dữ liệu:**

1. Đảm bảo MySQL Server của bạn đang chạy.
2. Sử dụng một công cụ như MySQL Workbench, chạy script SQL đã được cung cấp để tạo database `atm_demo`, các bảng (`accounts`, `cards`, `transactions`), và dữ liệu mẫu.

**Cài đặt thư viện:** Mở terminal và chạy lệnh:

```bash
pip install mysql-connector-python
```

**Cấu hình kết nối:** Mở file `withdraw_module.py` và cập nhật thông tin đăng nhập (đặc biệt là `password`) trong từ điển `DB_CONFIG` cho khớp với MySQL của bạn.

**Chạy chương trình:** Di chuyển đến thư mục chứa file và thực thi bằng lệnh:

```bash
python withdraw_module.py
```

Kết quả trên màn hình sẽ hiển thị quá trình xác thực và kết quả của hai lần rút tiền thử.

---

## 🔬 Lab 08 – Kiểm thử ATM

Mục tiêu của lab này là viết và chạy các kịch bản kiểm thử đơn vị (Unit Test) để đảm bảo các hàm trong `withdraw_module.py` hoạt động đúng logic trong mọi trường hợp.

### 🧠 Giải thích Logic (test_withdraw.py)

Chúng ta sử dụng `pytest` và `unittest.mock` để thực hiện kiểm thử mà không cần kết nối tới CSDL thật.

#### 1. Giả lập (Mocking)

Mocking là kỹ thuật thay thế các đối tượng thật (như kết nối CSDL) bằng các đối tượng giả lập mà chúng ta có thể toàn quyền kiểm soát.

- **`@pytest.fixture`**: Đoạn `mock_db_connection` là một "fixture", một hàm chuẩn bị môi trường cho các test case.
- **`@patch`**: Nó sử dụng `@patch` để "bắt" lệnh `mysql.connector.connect`. Thay vì thực sự kết nối, lệnh này sẽ trả về một đối tượng giả lập `MagicMock`.
- **Kiểm soát đối tượng giả**: Chúng ta có thể lập trình cho đối tượng `MagicMock` này. Ví dụ, chúng ta có thể ra lệnh cho `mock_cursor.fetchone()` trả về một giá trị cụ thể (`['correct_hash']`, `None`, `(1, 1000000)`, v.v.) để giả lập các tình huống khác nhau từ CSDL.

#### 2. Logic của các Test Case

Mỗi hàm `test_*` là một kịch bản kiểm thử độc lập.

**`test_verify_pin_*`:**

- **`_correct`**: Giả lập `fetchone()` trả về hash đúng. `assert` rằng hàm `verify_pin` trả về `True`.
- **`_incorrect`**: Giả lập `fetchone()` trả về hash sai. `assert` rằng hàm trả về `False`.
- **`_card_not_found`**: Giả lập `fetchone()` trả về `None` (không tìm thấy thẻ). `assert` rằng hàm trả về `False`.

**`test_withdraw_*`:**

- **`_sufficient_funds`**: Giả lập `fetchone()` trả về một số dư lớn. Sau khi chạy hàm `withdraw`, `assert` rằng `commit()` đã được gọi một lần và `rollback()` chưa bao giờ được gọi.
- **`_insufficient_funds`**: Giả lập `fetchone()` trả về một số dư nhỏ. Sau khi chạy hàm `withdraw`, `assert` rằng `rollback()` đã được gọi một lần và `commit()` chưa bao giờ được gọi.

### 🛠️ Hướng dẫn Cài đặt & Thực thi

**Cài đặt thư viện:** Mở terminal và chạy lệnh:

```bash
pip install pytest
```

**Xử lý Import:** Vì `test_withdraw.py` và `withdraw_module.py` nằm ở hai thư mục khác nhau, bạn cần thêm một đoạn mã vào đầu file test để Python có thể tìm thấy module cần kiểm thử.

**Chạy kiểm thử:** Di chuyển đến thư mục `lab08-testing` và thực thi bằng lệnh:

```bash
python -m pytest
```

Kết quả mong đợi là một dòng màu xanh lá cây báo rằng tất cả 5 tests đã thành công (passed).
