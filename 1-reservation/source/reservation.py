"""Reservation class with persistent storage."""
import json
import os
import uuid

# Import Hotel class to reserve/cancel rooms and its loader helper
from hotel import Hotel, _load_hotels
# Import the customer loader helper for existence checks
from customer import _load_customers

# Path to the shared data directory (one level above source/)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
# Absolute path to the reservations JSON file
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.json")


def _ensure_data_dir():
    """Create the data directory if it does not exist."""
    # exist_ok=True avoids an error when the directory already exists
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_reservations():
    """Load reservations from JSON. Returns empty dict on missing/corrupt."""
    _ensure_data_dir()
    # Return an empty store when the file has not been created yet
    if not os.path.exists(RESERVATIONS_FILE):
        return {}
    try:
        # Open in read mode with UTF-8 to handle special characters
        with open(RESERVATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as err:
        # Warn the user and continue with an empty store
        print(
            "Warning: reservations file is corrupt "
            f"({err}). Using empty store."
        )
        return {}


def _save_reservations(reservations):
    """Persist the reservations dictionary to the JSON file."""
    _ensure_data_dir()
    # Overwrite the file with the latest state; indent=2 for readability
    with open(RESERVATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(reservations, f, indent=2)


class Reservation:
    """Represents a reservation linking a customer to a hotel room.

    Attributes:
        reservation_id (str): Unique 8-character identifier (UUID prefix).
        customer_id (str): ID of the customer who made the reservation.
        hotel_name (str): Name of the hotel where the room is reserved.
    """

    def __init__(self, reservation_id, customer_id, hotel_name):
        # Store all identifying information for this reservation
        self.reservation_id = reservation_id
        self.customer_id = customer_id
        self.hotel_name = hotel_name

    def to_dict(self):
        """Serialize the reservation instance to a plain dictionary."""
        return {
            "reservation_id": self.reservation_id,
            "customer_id": self.customer_id,
            "hotel_name": self.hotel_name,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a reservation from a plain dictionary."""
        # Reconstruct the Reservation from stored field values
        return cls(
            data["reservation_id"],
            data["customer_id"],
            data["hotel_name"],
        )

    @staticmethod
    def create_reservation(customer_id, hotel_name):
        """Create a reservation for a customer at a hotel.

        Validates both the customer and hotel, reserves one room, then
        persists the new reservation record.

        Args:
            customer_id (str): ID of the customer making the reservation.
            hotel_name (str): Name of the hotel to reserve a room at.

        Returns:
            Reservation: The newly created Reservation instance.

        Raises:
            ValueError: If the customer or hotel does not exist, or if
                the hotel has no available rooms.
        """
        customers = _load_customers()
        # Verify the customer exists before proceeding
        if customer_id not in customers:
            raise ValueError(f"Customer '{customer_id}' not found.")
        hotels = _load_hotels()
        # Verify the hotel exists before proceeding
        if hotel_name not in hotels:
            raise ValueError(f"Hotel '{hotel_name}' not found.")
        # Reserve a room; raises ValueError if the hotel is fully booked
        Hotel.reserve_room(hotel_name)
        # Use the first 8 characters of a UUID as a short unique ID
        reservation_id = str(uuid.uuid4())[:8]
        reservation = Reservation(reservation_id, customer_id, hotel_name)
        reservations = _load_reservations()
        # Add the new record to the in-memory dictionary
        reservations[reservation_id] = reservation.to_dict()
        _save_reservations(reservations)
        return reservation

    @staticmethod
    def cancel_reservation(reservation_id):
        """Cancel an existing reservation and free the hotel room.

        Removes the reservation record and decrements the hotel's
        reserved room count.

        Args:
            reservation_id (str): ID of the reservation to cancel.

        Raises:
            ValueError: If the reservation does not exist.
        """
        reservations = _load_reservations()
        # Cannot cancel a reservation that does not exist
        if reservation_id not in reservations:
            raise ValueError(f"Reservation '{reservation_id}' not found.")
        r = reservations[reservation_id]
        # Release the room back to the hotel (decrements reserved count)
        Hotel.cancel_room(r["hotel_name"])
        # Remove the reservation record from the dictionary
        del reservations[reservation_id]
        _save_reservations(reservations)
