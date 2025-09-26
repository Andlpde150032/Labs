# file: test_withdraw.py
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

# Thêm dòng này để import được withdraw_module từ thư mục lab07
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lab07-withdraw-module')))
import withdraw_module

@pytest.fixture
def mock_db_connection():
    """
    Fixture đã được sửa lỗi: Giả lập kết nối CSDL và con trỏ,
    đồng thời liên kết mock_cursor với mock_conn.
    """
    with patch('withdraw_module.mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Liên kết mock_cursor.connection ngược lại với mock_conn
        mock_cursor.connection = mock_conn
        
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_cursor

# --- Tests cho hàm verify_pin ---
def test_verify_pin_correct(mock_db_connection):
    """Test case: Mã PIN nhập đúng."""
    # SỬA LỖI: Cập nhật đúng hash SHA-256 của chuỗi "1234"
    mock_db_connection.fetchone.return_value = ['03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4']
    assert withdraw_module.verify_pin("123", "1234") == True

def test_verify_pin_incorrect(mock_db_connection):
    """Test case: Mã PIN nhập sai."""
    mock_db_connection.fetchone.return_value = ['wrong_hash']
    assert withdraw_module.verify_pin("123", "1234") == False

def test_verify_pin_card_not_found(mock_db_connection):
    """Test case: Thẻ không tồn tại."""
    mock_db_connection.fetchone.return_value = None
    assert withdraw_module.verify_pin("123", "1234") == False

# --- Tests cho hàm withdraw ---
def test_withdraw_sufficient_funds(mock_db_connection):
    """Test case: Rút tiền thành công khi đủ số dư."""
    mock_db_connection.fetchone.return_value = (1, Decimal('1000000'))
    
    withdraw_module.withdraw("123", 500000)
    
    # Code kiểm tra này bây giờ sẽ hoạt động đúng
    mock_db_connection.connection.commit.assert_called_once()
    mock_db_connection.connection.rollback.assert_not_called()

def test_withdraw_insufficient_funds(mock_db_connection):
    """Test case: Rút tiền thất bại khi không đủ số dư."""
    mock_db_connection.fetchone.return_value = (1, Decimal('300000'))
    
    withdraw_module.withdraw("123", 500000)
    
    # Code kiểm tra này bây giờ sẽ hoạt động đúng
    mock_db_connection.connection.commit.assert_not_called()
    mock_db_connection.connection.rollback.assert_called_once()