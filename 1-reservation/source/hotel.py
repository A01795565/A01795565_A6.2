"""Hotel class with persistent storage."""
import json
import os

# Path to the shared data directory (one level above source/)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
# Absolute path to the hotels JSON file
HOTELS_FILE = os.path.join(DATA_DIR, "hotels.json")


def _ensure_data_dir():
    """Create the data directory if it does not exist."""
    # exist_ok=True avoids an error when the directory already exists
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_hotels():
    """Load hotels from JSON. Returns empty dict on missing or corrupt file."""
    _ensure_data_dir()
    # Return an empty store when the file has not been created yet
    if not os.path.exists(HOTELS_FILE):
        return {}
    try:
        # Open in read mode with UTF-8 to handle special characters
        with open(HOTELS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as err:
        # Warn the user and continue with an empty store
        print(f"Warning: hotels file is corrupt ({err}). Using empty store.")
        return {}


def _save_hotels(hotels):
    """Persist the hotels dictionary to the JSON file."""
    _ensure_data_dir()
    # Overwrite the file with the latest state; indent=2 for readability
    with open(HOTELS_FILE, "w", encoding="utf-8") as f:
        json.dump(hotels, f, indent=2)


class Hotel:
    """Represents a hotel with rooms that can be reserved.

    Attributes:
        name (str): Unique name that identifies the hotel.
        location (str): City or address where the hotel is located.
        total_rooms (int): Total number of rooms in the hotel.
        reserved_rooms (int): Number of rooms currently reserved.
    """

    def __init__(self, name, location, total_rooms):
        # Store identifying and capacity information for the hotel
        self.name = name
        self.location = location
        self.total_rooms = total_rooms
        # New hotels start with zero rooms reserved
        self.reserved_rooms = 0

    def to_dict(self):
        """Serialize the hotel instance to a plain dictionary."""
        return {
            "name": self.name,
            "location": self.location,
            "total_rooms": self.total_rooms,
            "reserved_rooms": self.reserved_rooms,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a hotel from a plain dictionary."""
        # Reconstruct the instance from stored field values
        hotel = cls(data["name"], data["location"], data["total_rooms"])
        # Default to 0 if the key is absent in older records
        hotel.reserved_rooms = data.get("reserved_rooms", 0)
        return hotel

    @staticmethod
    def create_hotel(name, location, total_rooms):
        """Create a new hotel and persist it to storage.

        Args:
            name (str): Unique hotel name.
            location (str): Hotel location.
            total_rooms (int): Total rooms (must be > 0).

        Returns:
            Hotel: The newly created Hotel instance.

        Raises:
            ValueError: If inputs are invalid or the name already exists.
        """
        # Validate that the name is a non-empty string
        if not name or not isinstance(name, str):
            raise ValueError("Hotel name must be a non-empty string.")
        # Validate that the location is a non-empty string
        if not location or not isinstance(location, str):
            raise ValueError("Location must be a non-empty string.")
        # Validate that room count is a positive integer
        if not isinstance(total_rooms, int) or total_rooms <= 0:
            raise ValueError("Total rooms must be a positive integer.")
        hotels = _load_hotels()
        # Prevent duplicate hotel names
        if name in hotels:
            raise ValueError(f"Hotel '{name}' already exists.")
        hotel = Hotel(name, location, total_rooms)
        # Serialize and add to the in-memory dictionary
        hotels[name] = hotel.to_dict()
        _save_hotels(hotels)
        return hotel

    @staticmethod
    def delete_hotel(name):
        """Delete a hotel from storage by name.

        Args:
            name (str): Name of the hotel to delete.

        Raises:
            ValueError: If the hotel does not exist.
        """
        hotels = _load_hotels()
        # Cannot delete a hotel that does not exist
        if name not in hotels:
            raise ValueError(f"Hotel '{name}' not found.")
        del hotels[name]
        _save_hotels(hotels)

    @staticmethod
    def display_hotel(name):
        """Return hotel information as a formatted string.

        Args:
            name (str): Name of the hotel to display.

        Returns:
            str: Multi-line string with hotel details.

        Raises:
            ValueError: If the hotel does not exist.
        """
        hotels = _load_hotels()
        # Cannot display a hotel that does not exist
        if name not in hotels:
            raise ValueError(f"Hotel '{name}' not found.")
        h = hotels[name]
        # Compute available rooms from total minus reserved
        available = h["total_rooms"] - h.get("reserved_rooms", 0)
        return (
            f"Hotel: {h['name']}\n"
            f"Location: {h['location']}\n"
            f"Total Rooms: {h['total_rooms']}\n"
            f"Reserved Rooms: {h.get('reserved_rooms', 0)}\n"
            f"Available Rooms: {available}"
        )

    @staticmethod
    def modify_hotel(name, new_name=None, new_location=None,
                     new_total_rooms=None):
        """Modify one or more fields of an existing hotel.

        Args:
            name (str): Current name of the hotel to modify.
            new_name (str, optional): New name for the hotel.
            new_location (str, optional): New location for the hotel.
            new_total_rooms (int, optional): New total room count.

        Raises:
            ValueError: If the hotel is not found, inputs are invalid,
                new_name belongs to another hotel, or new_total_rooms
                is below the current reserved count.
        """
        hotels = _load_hotels()
        # Cannot modify a hotel that does not exist
        if name not in hotels:
            raise ValueError(f"Hotel '{name}' not found.")
        hotel_data = hotels[name]
        # Only update location when a new value is explicitly provided
        if new_location is not None:
            if not new_location or not isinstance(new_location, str):
                raise ValueError("Location must be a non-empty string.")
            hotel_data["location"] = new_location
        # Only update room count when a new value is explicitly provided
        if new_total_rooms is not None:
            if not isinstance(new_total_rooms, int) or new_total_rooms <= 0:
                raise ValueError("Total rooms must be a positive integer.")
            # Prevent shrinking below the number of already-reserved rooms
            if new_total_rooms < hotel_data.get("reserved_rooms", 0):
                raise ValueError(
                    "Cannot set total rooms below reserved rooms."
                )
            hotel_data["total_rooms"] = new_total_rooms
        # Only rename when a different name is explicitly provided
        if new_name is not None and new_name != name:
            if not new_name or not isinstance(new_name, str):
                raise ValueError("Hotel name must be a non-empty string.")
            # Prevent clashing with an existing hotel
            if new_name in hotels:
                raise ValueError(f"Hotel '{new_name}' already exists.")
            hotel_data["name"] = new_name
            # Remove the old key and insert under the new key
            del hotels[name]
            hotels[new_name] = hotel_data
        else:
            # No rename: write the modified entry back under the same key
            hotels[name] = hotel_data
        _save_hotels(hotels)

    @staticmethod
    def reserve_room(name):
        """Increment the reserved room count by one.

        Args:
            name (str): Name of the hotel to reserve a room at.

        Raises:
            ValueError: If the hotel is not found or has no free rooms.
        """
        hotels = _load_hotels()
        # Cannot reserve a room at a non-existent hotel
        if name not in hotels:
            raise ValueError(f"Hotel '{name}' not found.")
        h = hotels[name]
        # Check whether all rooms are already taken
        if h.get("reserved_rooms", 0) >= h["total_rooms"]:
            raise ValueError(f"No available rooms at '{name}'.")
        # Increment the reserved count by one
        h["reserved_rooms"] = h.get("reserved_rooms", 0) + 1
        hotels[name] = h
        _save_hotels(hotels)

    @staticmethod
    def cancel_room(name):
        """Decrement the reserved room count by one.

        Args:
            name (str): Name of the hotel where a reservation is cancelled.

        Raises:
            ValueError: If the hotel is not found or has no reservations.
        """
        hotels = _load_hotels()
        # Cannot cancel a room at a non-existent hotel
        if name not in hotels:
            raise ValueError(f"Hotel '{name}' not found.")
        h = hotels[name]
        # Check whether there are any reservations to cancel
        if h.get("reserved_rooms", 0) <= 0:
            raise ValueError(f"No reservations to cancel at '{name}'.")
        # Decrement the reserved count by one
        h["reserved_rooms"] = h["reserved_rooms"] - 1
        hotels[name] = h
        _save_hotels(hotels)
