# file: withdraw_module.py
import mysql.connector
import hashlib
from decimal import Decimal

# --- Cấu hình kết nối CSDL ---
DB_CONFIG = {
    'user': 'root',
    'password': 'sa123', # Thay bằng mật khẩu của bạn
    'host': '127.0.0.1',
    'database': 'atm_demo'
}

def get_db_connection():
    """Tạo và trả về một kết nối CSDL."""
    return mysql.connector.connect(**DB_CONFIG)

def verify_pin(card_no, pin):
    """Xác thực mã PIN của thẻ bằng cách so sánh với hash trong CSDL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Lấy pin_hash từ CSDL [cite: 83]
        query = "SELECT pin_hash FROM cards WHERE card_no = %s"
        cursor.execute(query, (card_no,))
        result = cursor.fetchone() # [cite: 85]
        
        if result:
            pin_hash_from_db = result[0]
            # Băm mã PIN người dùng nhập và so sánh
            entered_pin_hash = hashlib.sha256(pin.encode()).hexdigest() # [cite: 87]
            return pin_hash_from_db == entered_pin_hash
        return False
    finally:
        cursor.close()
        conn.close() # [cite: 86]

def withdraw(card_no, amount):
    """Thực hiện giao dịch rút tiền."""
    # Chuyển đổi amount sang Decimal để tính toán chính xác
    withdraw_amount = Decimal(amount)
    if withdraw_amount <= 0:
        print("Lỗi: Số tiền rút phải lớn hơn 0.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Bắt đầu một transaction để đảm bảo tính toàn vẹn dữ liệu [cite: 93]
        conn.start_transaction()
        
        # Lấy thông tin tài khoản và khóa dòng dữ liệu để tránh xung đột [cite: 94, 95]
        query = """
            SELECT a.account_id, a.balance 
            FROM accounts a JOIN cards c ON a.account_id = c.account_id 
            WHERE c.card_no = %s FOR UPDATE
        """
        cursor.execute(query, (card_no,))
        account = cursor.fetchone() # [cite: 96]
        
        if not account:
            raise Exception("Không tìm thấy tài khoản cho thẻ này.")

        account_id, balance = account
        balance = Decimal(balance)

        # Kiểm tra số dư [cite: 97]
        if balance < withdraw_amount:
            raise Exception("Số dư không đủ.") # [cite: 98]
        
        # Cập nhật số dư mới
        new_balance = balance - withdraw_amount
        update_query = "UPDATE accounts SET balance = %s WHERE account_id = %s"
        cursor.execute(update_query, (new_balance, account_id)) # [cite: 99, 100]
        
        # Ghi lại lịch sử giao dịch [cite: 101, 102]
        insert_query = """
            INSERT INTO transactions (account_id, card_no, atm_id, tx_type, amount, balance_after) 
            VALUES (%s, %s, 1, 'WITHDRAW', %s, %s)
        """
        cursor.execute(insert_query, (account_id, card_no, withdraw_amount, new_balance)) # [cite: 103]
        
        # Nếu mọi thứ thành công, commit transaction
        conn.commit() # [cite: 104]
        print(f"Rút tiền thành công! Số dư mới: {new_balance}") # [cite: 105]

    except Exception as e:
        # Nếu có lỗi, rollback để hủy mọi thay đổi [cite: 107]
        conn.rollback()
        print(f"Lỗi giao dịch: {e}") # [cite: 108]
    finally:
        # Đảm bảo kết nối luôn được đóng [cite: 110]
        cursor.close()
        conn.close()

# --- Hàm main để chạy thử ---
if __name__ == "__main__":
    card_number_demo = "1111222233334444"
    pin_demo = "1234"
    
    print(f"Đang xác thực thẻ: {card_number_demo}...")
    if verify_pin(card_number_demo, pin_demo):
        print("Xác thực PIN thành công!")
        
        # Test case 1: Rút tiền thành công
        print("\n--- Thử rút 500,000 ---")
        withdraw(card_number_demo, 500000)
        
        # Test case 2: Rút số tiền lớn hơn số dư
        print("\n--- Thử rút 1,000,000,000 ---")
        withdraw(card_number_demo, 1000000000)
    else:
        print("Xác thực PIN thất bại!")