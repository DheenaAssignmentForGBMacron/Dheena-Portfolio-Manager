import unittest
from unittest.mock import patch

from app.repositories.portfolio_repository import PortfolioRepository


class PortfolioRepositoryTests(unittest.TestCase):

    @patch("app.repositories.portfolio_repository.PortfolioEngine")
    def test_get_portfolio_builds_and_caches(self, mock_engine):

        portfolio = {
            "holdings": {},
            "summary": {},
        }

        mock_engine.return_value.process.return_value = portfolio

        repository = PortfolioRepository()

        first_result = repository.get_portfolio()
        second_result = repository.get_portfolio()

        self.assertIs(first_result, portfolio)
        self.assertIs(second_result, portfolio)

        mock_engine.assert_called_once_with()
        mock_engine.return_value.process.assert_called_once_with()

    @patch("app.repositories.portfolio_repository.PortfolioEngine")
    def test_invalidate_forces_rebuild(self, mock_engine):

        first_portfolio = {
            "holdings": {},
            "summary": {"value": 100},
        }

        second_portfolio = {
            "holdings": {},
            "summary": {"value": 200},
        }

        mock_engine.return_value.process.side_effect = [
            first_portfolio,
            second_portfolio,
        ]

        repository = PortfolioRepository()

        first_result = repository.get_portfolio()

        repository.invalidate()

        second_result = repository.get_portfolio()

        self.assertIs(first_result, first_portfolio)
        self.assertIs(second_result, second_portfolio)

        self.assertEqual(
            mock_engine.return_value.process.call_count,
            2,
        )

    @patch("app.repositories.portfolio_repository.PortfolioEngine")
    def test_cached_portfolio_is_returned_without_rebuilding(
        self,
        mock_engine,
    ):

        portfolio = {
            "holdings": {1: "holding"},
            "summary": {"value": 500},
        }

        mock_engine.return_value.process.return_value = portfolio

        repository = PortfolioRepository()

        result_1 = repository.get_portfolio()
        result_2 = repository.get_portfolio()
        result_3 = repository.get_portfolio()

        self.assertIs(result_1, result_2)
        self.assertIs(result_2, result_3)

        mock_engine.return_value.process.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()