import unittest
from unittest.mock import patch

from app import create_app


class TransactionRoutesTests(unittest.TestCase):

    def setUp(self):

        self.app = create_app()
        self.app.config.update(
            TESTING=True,
        )

        self.client = self.app.test_client()

    # =====================================================
    # Add Transaction
    # =====================================================

    @patch("app.routes.transaction_routes.add_transaction")
    @patch("app.routes.transaction_routes.get_asset")
    def test_add_transaction_passes_dividend_and_bonus(
        self,
        mock_get_asset,
        mock_add_transaction,
    ):

        mock_get_asset.return_value = {
            "symbol": "HAL",
            "asset_class": "Stock",
        }

        response = self.client.post(
            "/add-transaction",
            data={
                "asset_id": "1",
                "transaction_type": "BUY",
                "quantity": "10",
                "price": "400",
                "brokerage": "20",
                "dividend": "0",
                "bonus": "0",
                "transaction_date": "2026-08-10",
                "notes": "Test buy",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        mock_add_transaction.assert_called_once_with(
            asset="HAL",
            asset_type="Stock",
            asset_id=1,
            transaction_type="BUY",
            quantity=10.0,
            price=400.0,
            brokerage=20.0,
            dividend=0.0,
            bonus=0.0,
            transaction_date="2026-08-10",
            notes="Test buy",
        )

    # =====================================================
    # Edit Transaction
    # =====================================================

    @patch("app.routes.transaction_routes.update_transaction")
    @patch("app.routes.transaction_routes.get_asset")
    @patch("app.routes.transaction_routes.get_transaction")
    def test_edit_transaction_passes_dividend_and_bonus(
        self,
        mock_get_transaction,
        mock_get_asset,
        mock_update_transaction,
    ):

        mock_get_transaction.return_value = {
            "id": 10,
            "asset_id": 1,
            "transaction_type": "BUY",
            "quantity": 10,
            "price": 400,
        }

        mock_get_asset.return_value = {
            "symbol": "HAL",
            "asset_class": "Stock",
        }

        response = self.client.post(
            "/edit-transaction/10",
            data={
                "asset_id": "1",
                "transaction_type": "BUY",
                "quantity": "10",
                "price": "450",
                "brokerage": "20",
                "dividend": "0",
                "bonus": "0",
                "transaction_date": "2026-08-10",
                "notes": "Updated buy",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        mock_update_transaction.assert_called_once_with(
            transaction_id=10,
            asset="HAL",
            asset_type="Stock",
            asset_id=1,
            transaction_type="BUY",
            quantity=10.0,
            price=450.0,
            brokerage=20.0,
            dividend=0.0,
            bonus=0.0,
            transaction_date="2026-08-10",
            notes="Updated buy",
        )


if __name__ == "__main__":
    unittest.main()