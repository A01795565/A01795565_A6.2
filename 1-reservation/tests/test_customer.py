"""Unit tests for the Customer class."""
import os
import sys
import json
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))

import customer as customer_module
from customer import Customer


class TestCustomer(unittest.TestCase):
    """Tests for Customer CRUD operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "customers.json")
        customer_module.DATA_DIR = self.temp_dir
        customer_module.CUSTOMERS_FILE = self.temp_file

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # =========================================================
    # Positive Tests
    # =========================================================

    # --- Create Customer ---

    def test_create_customer_success(self):
        c = Customer.create_customer("C001", "Alice", "alice@mail.com")
        self.assertEqual(c.customer_id, "C001")
        self.assertEqual(c.name, "Alice")
        self.assertEqual(c.email, "alice@mail.com")

    def test_create_customer_persists(self):
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        with open(self.temp_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("C001", data)

    # --- Delete Customer ---

    def test_delete_customer_success(self):
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        Customer.delete_customer("C001")
        with open(self.temp_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertNotIn("C001", data)

    # --- Display Customer ---

    def test_display_customer_success(self):
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        info = Customer.display_customer("C001")
        self.assertIn("C001", info)
        self.assertIn("Alice", info)
        self.assertIn("alice@mail.com", info)

    # --- Modify Customer ---

    def test_modify_customer_name(self):
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        Customer.modify_customer("C001", new_name="Alicia")
        info = Customer.display_customer("C001")
        self.assertIn("Alicia", info)

    def test_modify_customer_email(self):
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        Customer.modify_customer("C001", new_email="new@mail.com")
        info = Customer.display_customer("C001")
        self.assertIn("new@mail.com", info)

    # --- Serialization ---

    def test_to_dict_and_from_dict(self):
        c = Customer("C001", "Alice", "alice@mail.com")
        data = c.to_dict()
        c2 = Customer.from_dict(data)
        self.assertEqual(c2.customer_id, "C001")
        self.assertEqual(c2.name, "Alice")
        self.assertEqual(c2.email, "alice@mail.com")

    # --- Corrupt file handling ---

    def test_load_customers_corrupt_file_returns_empty(self):
        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write("NOT VALID JSON {{{")
        result = customer_module._load_customers()
        self.assertEqual(result, {})

    def test_load_customers_corrupt_file_prints_warning(self):
        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write("NOT VALID JSON {{{")
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            customer_module._load_customers()
        self.assertIn("Warning", buf.getvalue())

    def test_create_customer_after_corrupt_file(self):
        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write("INVALID")
        c = Customer.create_customer("C001", "Alice", "alice@mail.com")
        self.assertEqual(c.customer_id, "C001")

    # =========================================================
    # Negative Tests
    # =========================================================

    def test_neg_create_customer_duplicate_id_raises(self):
        """Creating a customer with an already-taken ID must fail."""
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        with self.assertRaises(ValueError):
            Customer.create_customer("C001", "Bob", "bob@mail.com")

    def test_neg_create_customer_empty_id_raises(self):
        """Creating a customer with an empty ID must fail."""
        with self.assertRaises(ValueError):
            Customer.create_customer("", "Alice", "alice@mail.com")

    def test_neg_create_customer_empty_name_raises(self):
        """Creating a customer with an empty name must fail."""
        with self.assertRaises(ValueError):
            Customer.create_customer("C001", "", "alice@mail.com")

    def test_neg_create_customer_empty_email_raises(self):
        """Creating a customer with an empty email must fail."""
        with self.assertRaises(ValueError):
            Customer.create_customer("C001", "Alice", "")

    def test_neg_create_customer_non_string_id_raises(self):
        """Creating a customer with a non-string ID must fail."""
        with self.assertRaises(ValueError):
            Customer.create_customer(123, "Alice", "alice@mail.com")

    def test_neg_delete_nonexistent_customer_raises(self):
        """Deleting a customer that does not exist must fail."""
        with self.assertRaises(ValueError):
            Customer.delete_customer("C999")

    def test_neg_display_nonexistent_customer_raises(self):
        """Displaying a customer that does not exist must fail."""
        with self.assertRaises(ValueError):
            Customer.display_customer("C999")

    def test_neg_modify_nonexistent_customer_raises(self):
        """Modifying a customer that does not exist must fail."""
        with self.assertRaises(ValueError):
            Customer.modify_customer("C999", new_name="Bob")

    def test_neg_modify_customer_empty_name_raises(self):
        """Updating a customer with an empty name must fail."""
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        with self.assertRaises(ValueError):
            Customer.modify_customer("C001", new_name="")

    def test_neg_modify_customer_empty_email_raises(self):
        """Updating a customer with an empty email must fail."""
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        with self.assertRaises(ValueError):
            Customer.modify_customer("C001", new_email="")


if __name__ == "__main__":
    unittest.main()
