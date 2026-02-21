"""Customer class with persistent storage."""
import json
import os

# Path to the shared data directory (one level above source/)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
# Absolute path to the customers JSON file
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")


def _ensure_data_dir():
    """Create the data directory if it does not exist."""
    # exist_ok=True avoids an error when the directory already exists
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_customers():
    """Load customers from JSON. Returns empty dict on missing/corrupt file."""
    _ensure_data_dir()
    # Return an empty store when the file has not been created yet
    if not os.path.exists(CUSTOMERS_FILE):
        return {}
    try:
        # Open in read mode with UTF-8 to handle special characters
        with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as err:
        # Warn the user and continue with an empty store
        print(
            f"Warning: customers file is corrupt ({err}). Using empty store."
        )
        return {}


def _save_customers(customers):
    """Persist the customers dictionary to the JSON file."""
    _ensure_data_dir()
    # Overwrite the file with the latest state; indent=2 for readability
    with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, indent=2)


class Customer:
    """Represents a customer who can make hotel reservations.

    Attributes:
        customer_id (str): Unique identifier for the customer.
        name (str): Full name of the customer.
        email (str): Email address of the customer.
    """

    def __init__(self, customer_id, name, email):
        # Store all identifying information for the customer
        self.customer_id = customer_id
        self.name = name
        self.email = email

    def to_dict(self):
        """Serialize the customer instance to a plain dictionary."""
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a customer from a plain dictionary."""
        # Reconstruct the Customer from the stored field values
        return cls(data["customer_id"], data["name"], data["email"])

    @staticmethod
    def create_customer(customer_id, name, email):
        """Create a new customer and persist it to storage.

        Args:
            customer_id (str): Unique identifier for the customer.
            name (str): Full name of the customer.
            email (str): Email address of the customer.

        Returns:
            Customer: The newly created Customer instance.

        Raises:
            ValueError: If any input is invalid or the ID already exists.
        """
        # Validate that the customer ID is a non-empty string
        if not customer_id or not isinstance(customer_id, str):
            raise ValueError("Customer ID must be a non-empty string.")
        # Validate that the name is a non-empty string
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string.")
        # Validate that the email is a non-empty string
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string.")
        customers = _load_customers()
        # Prevent duplicate customer IDs
        if customer_id in customers:
            raise ValueError(f"Customer '{customer_id}' already exists.")
        customer = Customer(customer_id, name, email)
        # Serialize and add to the in-memory dictionary
        customers[customer_id] = customer.to_dict()
        _save_customers(customers)
        return customer

    @staticmethod
    def delete_customer(customer_id):
        """Delete a customer from storage by ID.

        Args:
            customer_id (str): ID of the customer to delete.

        Raises:
            ValueError: If the customer does not exist.
        """
        customers = _load_customers()
        # Cannot delete a customer that does not exist
        if customer_id not in customers:
            raise ValueError(f"Customer '{customer_id}' not found.")
        del customers[customer_id]
        _save_customers(customers)

    @staticmethod
    def display_customer(customer_id):
        """Return customer information as a formatted string.

        Args:
            customer_id (str): ID of the customer to display.

        Returns:
            str: Multi-line string with customer details.

        Raises:
            ValueError: If the customer does not exist.
        """
        customers = _load_customers()
        # Cannot display a customer that does not exist
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
        """Modify one or more fields of an existing customer.

        Args:
            customer_id (str): ID of the customer to modify.
            new_name (str, optional): New name for the customer.
            new_email (str, optional): New email for the customer.

        Raises:
            ValueError: If the customer is not found or inputs are invalid.
        """
        customers = _load_customers()
        # Cannot modify a customer that does not exist
        if customer_id not in customers:
            raise ValueError(f"Customer '{customer_id}' not found.")
        c = customers[customer_id]
        # Only update name when a new value is explicitly provided
        if new_name is not None:
            if not new_name or not isinstance(new_name, str):
                raise ValueError("Name must be a non-empty string.")
            c["name"] = new_name
        # Only update email when a new value is explicitly provided
        if new_email is not None:
            if not new_email or not isinstance(new_email, str):
                raise ValueError("Email must be a non-empty string.")
            c["email"] = new_email
        # Write the modified entry back into the dictionary
        customers[customer_id] = c
        _save_customers(customers)
