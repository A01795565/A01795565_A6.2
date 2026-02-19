"""Customer class with persistent storage."""
import json
import os


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_customers():
    _ensure_data_dir()
    if not os.path.exists(CUSTOMERS_FILE):
        return {}
    with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_customers(customers):
    _ensure_data_dir()
    with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, indent=2)


class Customer:
    """Represents a customer who can make reservations."""

    def __init__(self, customer_id, name, email):
        self.customer_id = customer_id
        self.name = name
        self.email = email

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["customer_id"], data["name"], data["email"])

    @staticmethod
    def create_customer(customer_id, name, email):
        """Create a new customer and persist it."""
        if not customer_id or not isinstance(customer_id, str):
            raise ValueError("Customer ID must be a non-empty string.")
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string.")
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string.")
        customers = _load_customers()
        if customer_id in customers:
            raise ValueError(
                f"Customer '{customer_id}' already exists."
            )
        customer = Customer(customer_id, name, email)
        customers[customer_id] = customer.to_dict()
        _save_customers(customers)
        return customer

    @staticmethod
    def delete_customer(customer_id):
        """Delete a customer by ID."""
        customers = _load_customers()
        if customer_id not in customers:
            raise ValueError(f"Customer '{customer_id}' not found.")
        del customers[customer_id]
        _save_customers(customers)

    @staticmethod
    def display_customer(customer_id):
        """Return customer information as a formatted string."""
        customers = _load_customers()
        if customer_id not in customers:
            raise ValueError(f"Customer '{customer_id}' not found.")
        c = customers[customer_id]
        return (
            f"Customer ID: {c['customer_id']}\n"
            f"Name: {c['name']}\n"
            f"Email: {c['email']}"
        )

    @staticmethod
    def modify_customer(customer_id, new_name=None, new_email=None):
        """Modify customer information."""
        customers = _load_customers()
        if customer_id not in customers:
            raise ValueError(f"Customer '{customer_id}' not found.")
        c = customers[customer_id]
        if new_name is not None:
            if not new_name or not isinstance(new_name, str):
                raise ValueError("Name must be a non-empty string.")
            c["name"] = new_name
        if new_email is not None:
            if not new_email or not isinstance(new_email, str):
                raise ValueError("Email must be a non-empty string.")
            c["email"] = new_email
        customers[customer_id] = c
        _save_customers(customers)
