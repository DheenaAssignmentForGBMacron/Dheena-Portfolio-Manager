import unittest
from unittest.mock import patch

from app.services import transaction_service


class TransactionServiceTests(unittest.TestCase):

    # =====================================================
    # Add
    # =====================================================

    @patch("app.services.transaction_service.invalidate_portfolio")
    @patch("app.services.transaction_service.repo_add_transaction")
    def test_add_transaction_delegates_and_invalidates(
        self,
        mock_repo_add,
        mock_invalidate,
    ):
        mock_repo_add.return_value = 123

        result = transaction_service.add_transaction(
            asset="HAL",
            asset_type="Stock",
            asset_id=1,
            transaction_type="BUY",
            quantity=10,
            price=400,
            brokerage=20,
            dividend=0,
            bonus=0,
            transaction_date="2026-08-08",
            notes="Test buy",
        )

        self.assertEqual(result, 123)

        mock_repo_add.assert_called_once_with(
            "HAL",
            "Stock",
            1,
            "BUY",
            10,
            400,
            20,
            0,
            0,
            "2026-08-08",
            "Test buy",
        )

        mock_invalidate.assert_called_once()

    # =====================================================
    # Read
    # =====================================================

    @patch("app.services.transaction_service.repo_get_transactions")
    def test_get_transactions_delegates(self, mock_repo):

        mock_repo.return_value = ["tx1", "tx2"]

        result = transaction_service.get_transactions()

        self.assertEqual(result, ["tx1", "tx2"])
        mock_repo.assert_called_once_with()

    @patch("app.services.transaction_service.repo_get_transaction")
    def test_get_transaction_delegates(self, mock_repo):

        mock_repo.return_value = {"id": 10}

        result = transaction_service.get_transaction(10)

        self.assertEqual(result, {"id": 10})
        mock_repo.assert_called_once_with(10)

    @patch("app.services.transaction_service.repo_get_asset_transactions")
    def test_get_asset_transactions_delegates(self, mock_repo):

        mock_repo.return_value = ["tx1"]

        result = transaction_service.get_asset_transactions(5)

        self.assertEqual(result, ["tx1"])
        mock_repo.assert_called_once_with(5)

    # =====================================================
    # Update
    # =====================================================

    @patch("app.services.transaction_service.invalidate_portfolio")
    @patch("app.services.transaction_service.repo_update_transaction")
    def test_update_transaction_delegates_and_invalidates(
        self,
        mock_repo_update,
        mock_invalidate,
    ):
        mock_repo_update.return_value = True

        result = transaction_service.update_transaction(
            transaction_id=10,
            asset="HAL",
            asset_type="Stock",
            asset_id=1,
            transaction_type="BUY",
            quantity=10,
            price=400,
            brokerage=20,
            dividend=0,
            bonus=0,
            transaction_date="2026-08-08",
            notes="Updated",
        )

        self.assertTrue(result)

        mock_repo_update.assert_called_once_with(
            10,
            "HAL",
            "Stock",
            1,
            "BUY",
            10,
            400,
            20,
            0,
            0,
            "2026-08-08",
            "Updated",
        )

        mock_invalidate.assert_called_once()

    # =====================================================
    # Delete
    # =====================================================

    @patch("app.services.transaction_service.invalidate_portfolio")
    @patch("app.services.transaction_service.repo_delete_transaction")
    def test_delete_transaction_delegates_and_invalidates(
        self,
        mock_repo_delete,
        mock_invalidate,
    ):
        mock_repo_delete.return_value = True

        result = transaction_service.delete_transaction(10)

        self.assertTrue(result)

        mock_repo_delete.assert_called_once_with(10)

        mock_invalidate.assert_called_once()

    # =====================================================
    # BUY / SELL Validation
    # =====================================================

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_zero_quantity(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BUY",
                quantity=0,
                price=400,
                brokerage=20,
                dividend=0,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_negative_quantity(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BUY",
                quantity=-10,
                price=400,
                brokerage=20,
                dividend=0,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_negative_price(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BUY",
                quantity=10,
                price=-400,
                brokerage=20,
                dividend=0,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_negative_brokerage(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BUY",
                quantity=10,
                price=400,
                brokerage=-20,
                dividend=0,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_unsupported_transaction_type(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="INVALID",
                quantity=10,
                price=400,
                brokerage=20,
                dividend=0,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_invalid_transaction_date(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BUY",
                quantity=10,
                price=400,
                brokerage=20,
                dividend=0,
                bonus=0,
                transaction_date="not-a-date",
                notes="Invalid",
            )

        mock_repo.assert_not_called()

    # =====================================================
    # BUY / SELL Dividend / Bonus Restrictions
    # =====================================================

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_dividend_on_buy(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BUY",
                quantity=10,
                price=400,
                brokerage=20,
                dividend=100,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid dividend",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_bonus_on_buy(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BUY",
                quantity=10,
                price=400,
                brokerage=20,
                dividend=0,
                bonus=5,
                transaction_date="2026-08-08",
                notes="Invalid bonus",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_dividend_on_sell(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="SELL",
                quantity=10,
                price=400,
                brokerage=20,
                dividend=100,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid dividend",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_bonus_on_sell(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="SELL",
                quantity=10,
                price=400,
                brokerage=20,
                dividend=0,
                bonus=5,
                transaction_date="2026-08-08",
                notes="Invalid bonus",
            )

        mock_repo.assert_not_called()

    # =====================================================
    # Dividend Validation
    # =====================================================

    @patch("app.services.transaction_service.invalidate_portfolio")
    @patch("app.services.transaction_service.repo_add_transaction")
    def test_add_dividend_transaction(
        self,
        mock_repo_add,
        mock_invalidate,
    ):
        mock_repo_add.return_value = 123

        result = transaction_service.add_transaction(
            asset="HAL",
            asset_type="Stock",
            asset_id=1,
            transaction_type="DIVIDEND",
            quantity=0,
            price=0,
            brokerage=0,
            dividend=250,
            bonus=0,
            transaction_date="2026-08-08",
            notes="Dividend received",
        )

        self.assertEqual(result, 123)

        mock_repo_add.assert_called_once_with(
            "HAL",
            "Stock",
            1,
            "DIVIDEND",
            0,
            0,
            0,
            250,
            0,
            "2026-08-08",
            "Dividend received",
        )

        mock_invalidate.assert_called_once()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_zero_dividend(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="DIVIDEND",
                quantity=0,
                price=0,
                brokerage=0,
                dividend=0,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid dividend",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_negative_dividend(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="DIVIDEND",
                quantity=0,
                price=0,
                brokerage=0,
                dividend=-100,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid dividend",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_quantity_on_dividend(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="DIVIDEND",
                quantity=10,
                price=0,
                brokerage=0,
                dividend=250,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid dividend",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_price_on_dividend(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="DIVIDEND",
                quantity=0,
                price=100,
                brokerage=0,
                dividend=250,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid dividend",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_bonus_on_dividend(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="DIVIDEND",
                quantity=0,
                price=0,
                brokerage=0,
                dividend=250,
                bonus=5,
                transaction_date="2026-08-08",
                notes="Invalid dividend",
            )

        mock_repo.assert_not_called()

    # =====================================================
    # Bonus Validation
    # =====================================================

    @patch("app.services.transaction_service.invalidate_portfolio")
    @patch("app.services.transaction_service.repo_add_transaction")
    def test_add_bonus_transaction(
        self,
        mock_repo_add,
        mock_invalidate,
    ):
        mock_repo_add.return_value = 456

        result = transaction_service.add_transaction(
            asset="HAL",
            asset_type="Stock",
            asset_id=1,
            transaction_type="BONUS",
            quantity=0,
            price=0,
            brokerage=0,
            dividend=0,
            bonus=5,
            transaction_date="2026-08-08",
            notes="Bonus shares",
        )

        self.assertEqual(result, 456)

        mock_repo_add.assert_called_once_with(
            "HAL",
            "Stock",
            1,
            "BONUS",
            0,
            0,
            0,
            0,
            5,
            "2026-08-08",
            "Bonus shares",
        )

        mock_invalidate.assert_called_once()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_zero_bonus(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BONUS",
                quantity=0,
                price=0,
                brokerage=0,
                dividend=0,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid bonus",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_negative_bonus(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BONUS",
                quantity=0,
                price=0,
                brokerage=0,
                dividend=0,
                bonus=-5,
                transaction_date="2026-08-08",
                notes="Invalid bonus",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_quantity_on_bonus(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BONUS",
                quantity=10,
                price=0,
                brokerage=0,
                dividend=0,
                bonus=5,
                transaction_date="2026-08-08",
                notes="Invalid bonus",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_price_on_bonus(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BONUS",
                quantity=0,
                price=100,
                brokerage=0,
                dividend=0,
                bonus=5,
                transaction_date="2026-08-08",
                notes="Invalid bonus",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_add_transaction")
    def test_rejects_dividend_on_bonus(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.add_transaction(
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BONUS",
                quantity=0,
                price=0,
                brokerage=0,
                dividend=250,
                bonus=5,
                transaction_date="2026-08-08",
                notes="Invalid bonus",
            )

        mock_repo.assert_not_called()

    # =====================================================
    # Update Validation
    # =====================================================

    @patch("app.services.transaction_service.repo_update_transaction")
    def test_update_rejects_invalid_quantity(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.update_transaction(
                transaction_id=10,
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BUY",
                quantity=0,
                price=400,
                brokerage=20,
                dividend=0,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_update_transaction")
    def test_update_rejects_invalid_transaction_type(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.update_transaction(
                transaction_id=10,
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="INVALID",
                quantity=10,
                price=400,
                brokerage=20,
                dividend=0,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_update_transaction")
    def test_update_rejects_dividend_on_buy(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.update_transaction(
                transaction_id=10,
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BUY",
                quantity=10,
                price=400,
                brokerage=20,
                dividend=100,
                bonus=0,
                transaction_date="2026-08-08",
                notes="Invalid",
            )

        mock_repo.assert_not_called()

    @patch("app.services.transaction_service.repo_update_transaction")
    def test_update_rejects_bonus_on_buy(self, mock_repo):

        with self.assertRaises(ValueError):
            transaction_service.update_transaction(
                transaction_id=10,
                asset="HAL",
                asset_type="Stock",
                asset_id=1,
                transaction_type="BUY",
                quantity=10,
                price=400,
                brokerage=20,
                dividend=0,
                bonus=5,
                transaction_date="2026-08-08",
                notes="Invalid",
            )

        mock_repo.assert_not_called()

    # =====================================================
    # Update Dividend
    # =====================================================

    @patch("app.services.transaction_service.invalidate_portfolio")
    @patch("app.services.transaction_service.repo_update_transaction")
    def test_update_dividend_transaction(
        self,
        mock_repo_update,
        mock_invalidate,
    ):
        mock_repo_update.return_value = True

        result = transaction_service.update_transaction(
            transaction_id=10,
            asset="HAL",
            asset_type="Stock",
            asset_id=1,
            transaction_type="DIVIDEND",
            quantity=0,
            price=0,
            brokerage=0,
            dividend=300,
            bonus=0,
            transaction_date="2026-08-08",
            notes="Updated dividend",
        )

        self.assertTrue(result)

        mock_repo_update.assert_called_once_with(
            10,
            "HAL",
            "Stock",
            1,
            "DIVIDEND",
            0,
            0,
            0,
            300,
            0,
            "2026-08-08",
            "Updated dividend",
        )

        mock_invalidate.assert_called_once()

    # =====================================================
    # Update Bonus
    # =====================================================

    @patch("app.services.transaction_service.invalidate_portfolio")
    @patch("app.services.transaction_service.repo_update_transaction")
    def test_update_bonus_transaction(
        self,
        mock_repo_update,
        mock_invalidate,
    ):
        mock_repo_update.return_value = True

        result = transaction_service.update_transaction(
            transaction_id=10,
            asset="HAL",
            asset_type="Stock",
            asset_id=1,
            transaction_type="BONUS",
            quantity=0,
            price=0,
            brokerage=0,
            dividend=0,
            bonus=10,
            transaction_date="2026-08-08",
            notes="Updated bonus",
        )

        self.assertTrue(result)

        mock_repo_update.assert_called_once_with(
            10,
            "HAL",
            "Stock",
            1,
            "BONUS",
            0,
            0,
            0,
            0,
            10,
            "2026-08-08",
            "Updated bonus",
        )

        mock_invalidate.assert_called_once()


if __name__ == "__main__":
    unittest.main()