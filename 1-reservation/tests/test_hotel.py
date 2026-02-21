"""Unit tests for the Hotel class."""
import io
import os
import sys
import json
import unittest
import tempfile
import shutil
from contextlib import redirect_stdout

# Add source directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))

import hotel as hotel_module  # noqa: E402
from hotel import Hotel  # noqa: E402


class TestHotel(unittest.TestCase):
    """Tests for Hotel CRUD operations and room management."""

    # pylint: disable=too-many-public-methods

    def setUp(self):
        """Create a temporary data directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "hotels.json")
        hotel_module.DATA_DIR = self.temp_dir
        hotel_module.HOTELS_FILE = self.temp_file

    def tearDown(self):
        """Remove the temporary data directory."""
        shutil.rmtree(self.temp_dir)

    # =========================================================
    # Positive Tests
    # =========================================================

    # --- Create Hotel ---

    def test_create_hotel_success(self):
        """Hotel is created with correct name, location and room count."""
        h = Hotel.create_hotel("Plaza", "CDMX", 100)
        self.assertEqual(h.name, "Plaza")
        self.assertEqual(h.location, "CDMX")
        self.assertEqual(h.total_rooms, 100)
        self.assertEqual(h.reserved_rooms, 0)

    def test_create_hotel_persists(self):
        """Created hotel is persisted to the JSON file."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        with open(self.temp_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("Plaza", data)

    # --- Delete Hotel ---

    def test_delete_hotel_success(self):
        """Deleted hotel is removed from the JSON file."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        Hotel.delete_hotel("Plaza")
        with open(self.temp_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertNotIn("Plaza", data)

    # --- Display Hotel ---

    def test_display_hotel_success(self):
        """Displayed hotel info contains name, location and room count."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        info = Hotel.display_hotel("Plaza")
        self.assertIn("Plaza", info)
        self.assertIn("CDMX", info)
        self.assertIn("100", info)

    # --- Modify Hotel ---

    def test_modify_hotel_location(self):
        """Hotel location is updated and reflected in display."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        Hotel.modify_hotel("Plaza", new_location="GDL")
        info = Hotel.display_hotel("Plaza")
        self.assertIn("GDL", info)

    def test_modify_hotel_name(self):
        """Hotel name is updated and the hotel is retrievable under the new name."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        Hotel.modify_hotel("Plaza", new_name="Grand Plaza")
        info = Hotel.display_hotel("Grand Plaza")
        self.assertIn("Grand Plaza", info)

    def test_modify_hotel_total_rooms(self):
        """Hotel total rooms is updated and reflected in display."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        Hotel.modify_hotel("Plaza", new_total_rooms=200)
        info = Hotel.display_hotel("Plaza")
        self.assertIn("200", info)

    def test_modify_hotel_new_name_same_as_current(self):
        """Keeping the same name while changing another field works correctly."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        Hotel.modify_hotel("Plaza", new_name="Plaza", new_location="MTY")
        info = Hotel.display_hotel("Plaza")
        self.assertIn("MTY", info)

    # --- Reserve Room ---

    def test_reserve_room_success(self):
        """Reserving a room increments the reserved room count."""
        Hotel.create_hotel("Plaza", "CDMX", 2)
        Hotel.reserve_room("Plaza")
        info = Hotel.display_hotel("Plaza")
        self.assertIn("Reserved Rooms: 1", info)

    # --- Cancel Room ---

    def test_cancel_room_success(self):
        """Cancelling a reservation decrements the reserved room count."""
        Hotel.create_hotel("Plaza", "CDMX", 2)
        Hotel.reserve_room("Plaza")
        Hotel.cancel_room("Plaza")
        info = Hotel.display_hotel("Plaza")
        self.assertIn("Reserved Rooms: 0", info)

    # --- Serialization ---

    def test_to_dict_and_from_dict(self):
        """Round-trip serialization preserves all hotel fields."""
        h = Hotel("Plaza", "CDMX", 100)
        h.reserved_rooms = 5
        data = h.to_dict()
        h2 = Hotel.from_dict(data)
        self.assertEqual(h2.name, "Plaza")
        self.assertEqual(h2.reserved_rooms, 5)

    def test_from_dict_default_reserved_rooms(self):
        """Loading a hotel dict without reserved_rooms defaults to zero."""
        data = {"name": "Old", "location": "MTY", "total_rooms": 10}
        h = Hotel.from_dict(data)
        self.assertEqual(h.reserved_rooms, 0)

    # --- Corrupt file handling ---

    def test_load_hotels_corrupt_file_returns_empty(self):
        """Corrupt JSON file returns an empty dict instead of raising."""
        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write("NOT VALID JSON {{{")
        result = hotel_module._load_hotels()  # pylint: disable=protected-access
        self.assertEqual(result, {})

    def test_load_hotels_corrupt_file_prints_warning(self):
        """Corrupt JSON file prints a warning to stdout."""
        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write("NOT VALID JSON {{{")
        buf = io.StringIO()
        with redirect_stdout(buf):
            hotel_module._load_hotels()  # pylint: disable=protected-access
        self.assertIn("Warning", buf.getvalue())

    def test_create_hotel_after_corrupt_file(self):
        """Hotel can be created even when the data file is corrupt."""
        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write("INVALID")
        h = Hotel.create_hotel("Fresh", "MTY", 5)
        self.assertEqual(h.name, "Fresh")

    def test_multiple_reservations_and_cancellations(self):
        """Multiple reserves and cancels update the room count correctly."""
        Hotel.create_hotel("Plaza", "CDMX", 5)
        for _ in range(3):
            Hotel.reserve_room("Plaza")
        info = Hotel.display_hotel("Plaza")
        self.assertIn("Reserved Rooms: 3", info)
        for _ in range(3):
            Hotel.cancel_room("Plaza")
        info = Hotel.display_hotel("Plaza")
        self.assertIn("Reserved Rooms: 0", info)

    # =========================================================
    # Negative Tests
    # =========================================================

    def test_neg_create_hotel_duplicate_name_raises(self):
        """Creating a hotel with an already-taken name must fail."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        with self.assertRaises(ValueError):
            Hotel.create_hotel("Plaza", "GDL", 50)

    def test_neg_create_hotel_empty_name_raises(self):
        """Creating a hotel with an empty name must fail."""
        with self.assertRaises(ValueError):
            Hotel.create_hotel("", "CDMX", 100)

    def test_neg_create_hotel_empty_location_raises(self):
        """Creating a hotel with an empty location must fail."""
        with self.assertRaises(ValueError):
            Hotel.create_hotel("Plaza", "", 100)

    def test_neg_create_hotel_negative_rooms_raises(self):
        """Creating a hotel with a negative room count must fail."""
        with self.assertRaises(ValueError):
            Hotel.create_hotel("Plaza", "CDMX", -5)

    def test_neg_create_hotel_zero_rooms_raises(self):
        """Creating a hotel with zero rooms must fail."""
        with self.assertRaises(ValueError):
            Hotel.create_hotel("Plaza", "CDMX", 0)

    def test_neg_delete_nonexistent_hotel_raises(self):
        """Deleting a hotel that does not exist must fail."""
        with self.assertRaises(ValueError):
            Hotel.delete_hotel("Ghost")

    def test_neg_display_nonexistent_hotel_raises(self):
        """Displaying a hotel that does not exist must fail."""
        with self.assertRaises(ValueError):
            Hotel.display_hotel("Ghost")

    def test_neg_modify_nonexistent_hotel_raises(self):
        """Modifying a hotel that does not exist must fail."""
        with self.assertRaises(ValueError):
            Hotel.modify_hotel("Ghost", new_location="GDL")

    def test_neg_modify_hotel_rename_to_existing_raises(self):
        """Renaming a hotel to a name already taken must fail."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        Hotel.create_hotel("Grand", "GDL", 50)
        with self.assertRaises(ValueError):
            Hotel.modify_hotel("Plaza", new_name="Grand")

    def test_neg_modify_hotel_invalid_location_raises(self):
        """Updating a hotel with an empty location must fail."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        with self.assertRaises(ValueError):
            Hotel.modify_hotel("Plaza", new_location="")

    def test_neg_modify_hotel_invalid_new_name_raises(self):
        """Updating a hotel with an empty name must fail."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        with self.assertRaises(ValueError):
            Hotel.modify_hotel("Plaza", new_name="")

    def test_neg_modify_hotel_rooms_zero_raises(self):
        """Setting total rooms to zero must fail."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        Hotel.reserve_room("Plaza")
        with self.assertRaises(ValueError):
            Hotel.modify_hotel("Plaza", new_total_rooms=0)

    def test_neg_modify_hotel_rooms_below_reserved_raises(self):
        """Setting total rooms below reserved count must fail."""
        Hotel.create_hotel("Plaza", "CDMX", 10)
        for _ in range(5):
            Hotel.reserve_room("Plaza")
        with self.assertRaises(ValueError):
            Hotel.modify_hotel("Plaza", new_total_rooms=3)

    def test_neg_modify_hotel_invalid_rooms_type_raises(self):
        """Passing a non-integer room count must fail."""
        Hotel.create_hotel("Plaza", "CDMX", 100)
        with self.assertRaises(ValueError):
            Hotel.modify_hotel("Plaza", new_total_rooms="many")

    def test_neg_reserve_room_nonexistent_hotel_raises(self):
        """Reserving a room at a non-existent hotel must fail."""
        with self.assertRaises(ValueError):
            Hotel.reserve_room("Ghost")

    def test_neg_reserve_room_when_full_raises(self):
        """Reserving a room at a fully booked hotel must fail."""
        Hotel.create_hotel("Tiny", "CDMX", 1)
        Hotel.reserve_room("Tiny")
        with self.assertRaises(ValueError):
            Hotel.reserve_room("Tiny")

    def test_neg_cancel_room_nonexistent_hotel_raises(self):
        """Cancelling a room at a non-existent hotel must fail."""
        with self.assertRaises(ValueError):
            Hotel.cancel_room("Ghost")

    def test_neg_cancel_room_none_reserved_raises(self):
        """Cancelling a room when none are reserved must fail."""
        Hotel.create_hotel("Plaza", "CDMX", 2)
        with self.assertRaises(ValueError):
            Hotel.cancel_room("Plaza")


if __name__ == "__main__":
    unittest.main()
