import unittest
from unittest.mock import MagicMock
from service.TransactionHandler import TransactionHandler
from csctracker_py_core.utils.utils import Utils


class TestTransactionHandler(unittest.TestCase):
    def setUp(self):
        self.remote_repository = MagicMock()
        self.http_repository = MagicMock()
        self.http_repository.get_headers.return_value = {"Authorization": "Bearer test-token"}
        self.remote_repository.get_objects.return_value = []  # No existing transactions, to avoid 'Ignored'
        Utils.inform_to_client = MagicMock()
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

    def test_nubank_cashback_outcome(self):
        json_info = {
            "packageName": "com.nubank",
            "appName": "Nubank",
            "postTime": "1773752400000",
            "key": "nubank_key"
        }
        text_str = "Compra de R$ 100,00 em Loja Teste às 15:30."
        
        self.handler.transaction(text_str, json_info)
        
        # Verify that insert was called twice (once for original, once for cashback)
        self.assertEqual(self.remote_repository.insert.call_count, 2)
        
        # Check first insert (original transaction)
        first_call_args = self.remote_repository.insert.call_args_list[0]
        inserted_data_1 = first_call_args[1]["data"]
        self.assertEqual(inserted_data_1["type"], "outcome")
        self.assertEqual(inserted_data_1["value"], 100.00)
        self.assertEqual(inserted_data_1["app_name"], "Nubank")
        self.assertIsNone(inserted_data_1.get("category"))
        self.assertEqual(inserted_data_1["text"], text_str)
        
        # Check second insert (cashback transaction)
        second_call_args = self.remote_repository.insert.call_args_list[1]
        inserted_data_2 = second_call_args[1]["data"]
        self.assertEqual(inserted_data_2["type"], "income")
        self.assertEqual(inserted_data_2["name"], "Nubank")
        self.assertEqual(inserted_data_2["app_name"], "Nubank")
        self.assertEqual(inserted_data_2["value"], 1.25)
        self.assertEqual(inserted_data_2["text"], f"Cashback de 1.25 referente a {text_str}")
        self.assertEqual(inserted_data_2["key"], "nubank_key_cashback")

    def test_nubank_cashback_ignored(self):
        # Setup get_objects to return some existing transaction, making it ignored
        self.remote_repository.get_objects.return_value = [{"id": 123}]
        
        json_info = {
            "packageName": "com.nubank",
            "appName": "Nubank",
            "postTime": "1773752400000",
            "key": "nubank_key"
        }
        text_str = "Compra de R$ 100,00 em Loja Teste às 15:30."
        
        self.handler.transaction(text_str, json_info)
        
        # Verify that insert was called only once (because the cashback was not generated since category is Ignored)
        self.assertEqual(self.remote_repository.insert.call_count, 1)
        inserted_data = self.remote_repository.insert.call_args[1]["data"]
        self.assertEqual(inserted_data["category"], "Ignored")

    def test_nubank_cashback_not_new_but_no_cashback_exists(self):
        # We call save_transaction directly with a transaction that has an 'id'
        # Under the new logic, since no cashback exists, it should still generate cashback!
        transaction = {
            "id": "existing-id",
            "type": "outcome",
            "value": 100.00,
            "app_name": "Nubank",
            "text": "Compra de R$ 100,00 em Loja Teste às 15:30.",
            "key": "nubank_key",
            "date": "2026-07-16"
        }
        
        # Make get_objects return empty list for cashback check
        self.remote_repository.get_objects.return_value = []
        
        self.handler.save_transaction(transaction)
        
        # Verify that insert was called twice (once for original, once for cashback)
        self.assertEqual(self.remote_repository.insert.call_count, 2)

    def test_nubank_cashback_already_exists_not_ignored(self):
        # If cashback already exists and is not 'Ignored', it should NOT generate another cashback
        transaction = {
            "type": "outcome",
            "value": 100.00,
            "app_name": "Nubank",
            "text": "Compra de R$ 100,00 em Loja Teste às 15:30.",
            "key": "nubank_key",
            "date": "2026-07-16"
        }
        
        # Mock get_objects to return an existing cashback transaction that is not Ignored
        def mock_get_objects(table, keys=None, data=None, headers=None):
            if data and data.get('key') == "nubank_key_cashback":
                return [{"id": "cashback-id", "category": "Cashback"}]
            return []
            
        self.remote_repository.get_objects.side_effect = mock_get_objects
        
        self.handler.save_transaction(transaction)
        
        # Verify that insert was called only once (no cashback generated)
        self.assertEqual(self.remote_repository.insert.call_count, 1)

    def test_nubank_cashback_already_exists_but_ignored(self):
        # If cashback already exists but is 'Ignored', it SHOULD generate another cashback
        transaction = {
            "type": "outcome",
            "value": 100.00,
            "app_name": "Nubank",
            "text": "Compra de R$ 100,00 em Loja Teste às 15:30.",
            "key": "nubank_key",
            "date": "2026-07-16"
        }
        
        # Mock get_objects to return an existing cashback transaction that is Ignored
        def mock_get_objects(table, keys=None, data=None, headers=None):
            if data and data.get('key') == "nubank_key_cashback":
                return [{"id": "cashback-id", "category": "Ignored"}]
            return []
            
        self.remote_repository.get_objects.side_effect = mock_get_objects
        
        self.handler.save_transaction(transaction)
        
        # Verify that insert was called twice (original + new cashback)
        self.assertEqual(self.remote_repository.insert.call_count, 2)

    def test_nubank_cashback_installments(self):
        json_info = {
            "packageName": "com.nubank",
            "appName": "Nubank",
            "postTime": "1773752400000",
            "key": "nubank_key"
        }
        # A transaction with (3x) installments
        text_str = "Compra de R$ 300,00 em Loja Teste às 15:30 (3x)."
        
        self.handler.transaction(text_str, json_info)
        
        # Verify that insert was called 4 times:
        # - 3 times for the original split transactions
        # - 1 time for the full cashback transaction (triggered only on the first installment)
        self.assertEqual(self.remote_repository.insert.call_count, 4)
        
        # Let's verify the first installment and its cashback
        # First insert: installment 1 (mutated reference or final loop text depending on implementation, but let's check its value)
        inserted_1 = self.remote_repository.insert.call_args_list[0][1]["data"]
        self.assertEqual(inserted_1["type"], "outcome")
        self.assertEqual(inserted_1["value"], 100.00)
        
        # Second insert: cashback for installment 1 (copied, so preserves the installment text and gets full cashback value)
        inserted_2 = self.remote_repository.insert.call_args_list[1][1]["data"]
        self.assertEqual(inserted_2["type"], "income")
        self.assertEqual(inserted_2["name"], "Nubank")
        self.assertEqual(inserted_2["value"], 3.75)  # 1.25% of 300.00
        self.assertTrue("1/3" in inserted_2["text"])
        self.assertEqual(inserted_2["text"], f"Cashback de 3.75 referente a Compra de R$ 300,00 em Loja Teste às 15:30 (3x). 1/3")


if __name__ == "__main__":
    unittest.main()
