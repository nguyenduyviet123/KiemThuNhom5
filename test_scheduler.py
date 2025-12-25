import unittest
from unittest.mock import patch, MagicMock
from app import start_scheduler
from app import auto_delete_old_items


class TestAutoDeleteScheduler(unittest.TestCase):

    @patch("app.get_connection")
    def test_05_auto_delete(self, mock_get_conn):
        # Mock connection & cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Run function
        auto_delete_old_items()

        # Assert SQL được gọi
        mock_cursor.execute.assert_called_once()
        sql = mock_cursor.execute.call_args[0][0]

        self.assertIn("DELETE FROM SANPHAM", sql)
        self.assertIn("TrangThai = 0", sql)
        self.assertIn("DATEADD(day, -30", sql)

        # Assert commit + close
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("app.BackgroundScheduler")
    def test_06_scheduler(self, mock_scheduler_cls):
        mock_scheduler = mock_scheduler_cls.return_value

        start_scheduler()

        mock_scheduler.add_job.assert_called_once()
        args, kwargs = mock_scheduler.add_job.call_args

        self.assertEqual(kwargs["hours"], 24)
        self.assertEqual(args[1], "interval")

        mock_scheduler.start.assert_called_once()

if __name__ == "__main__":
    unittest.main()