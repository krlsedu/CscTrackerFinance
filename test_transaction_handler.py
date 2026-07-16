import unittest
from unittest.mock import MagicMock
from service.TransactionHandler import TransactionHandler


class TestTransactionHandler(unittest.TestCase):
    def setUp(self):
        self.remote_repository = MagicMock()
        self.http_repository = MagicMock()
        self.http_repository.get_headers.return_value = {"Authorization": "Bearer test-token"}
        self.remote_repository.get_objects.return_value = []  # No existing transactions, to avoid 'Ignored'
        self.handler = TransactionHandler(self.remote_repository, self.http_repository)

    def test_devolucao_iof_cashback(self):
        json_info = {
            "packageName": "com.test.app",
            "appName": "TestApp",
            "postTime": "1773752400000",  # some epoch timestamp
            "key": "test_key"
        }
        text_str = "Devolvemos o IOF de R$ 0,15 referente à compra na Paypal *Jetbrainsam. Continue aproveitando o cartão com o menor custo do mercado."
        
        self.handler.transaction(text_str, json_info)
        
        # Verify that insert was called
        self.remote_repository.insert.assert_called_once()
        inserted_data = self.remote_repository.insert.call_args[1]["data"]
        
        # Assertions
        self.assertEqual(inserted_data["type"], "income")
        self.assertEqual(inserted_data["value"], 0.15)
        self.assertEqual(inserted_data.get("category"), "Cashback")
        self.assertEqual(inserted_data["name"], "TestApp")
        self.assertEqual(inserted_data["app_name"], "TestApp")
        self.assertEqual(inserted_data["text"], text_str)

    def test_standard_purchase(self):
        json_info = {
            "packageName": "com.test.app",
            "appName": "TestApp",
            "postTime": "1773752400000",
            "key": "test_key"
        }
        text_str = "Compra de R$ 50,00 em Loja Teste às 15:30."
        
        self.handler.transaction(text_str, json_info)
        
        self.remote_repository.insert.assert_called_once()
        inserted_data = self.remote_repository.insert.call_args[1]["data"]
        
        self.assertEqual(inserted_data["type"], "outcome")
        self.assertEqual(inserted_data["value"], 50.00)
        self.assertIsNone(inserted_data.get("category"))
        self.assertEqual(inserted_data["name"], "Loja Teste")


if __name__ == "__main__":
    unittest.main()
