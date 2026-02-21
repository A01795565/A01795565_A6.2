"""Unit tests for the Reservation class."""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))

import hotel as hotel_module
import customer as customer_module
import reservation as reservation_module
from hotel import Hotel
from customer import Customer
from reservation import Reservation


class TestReservation(unittest.TestCase):
    """Tests for Reservation create and cancel operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Point all modules to the same temp directory
        hotel_module.DATA_DIR = self.temp_dir
        hotel_module.HOTELS_FILE = os.path.join(
            self.temp_dir, "hotels.json"
        )
        customer_module.DATA_DIR = self.temp_dir
        customer_module.CUSTOMERS_FILE = os.path.join(
            self.temp_dir, "customers.json"
        )
        reservation_module.DATA_DIR = self.temp_dir
        reservation_module.RESERVATIONS_FILE = os.path.join(
            self.temp_dir, "reservations.json"
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def _setup_hotel_and_customer(self):
        Hotel.create_hotel("Plaza", "CDMX", 10)
        Customer.create_customer("C001", "Alice", "alice@mail.com")

    # =========================================================
    # Positive Tests
    # =========================================================

    def test_create_reservation_success(self):
        self._setup_hotel_and_customer()
        r = Reservation.create_reservation("C001", "Plaza")
        self.assertEqual(r.customer_id, "C001")
        self.assertEqual(r.hotel_name, "Plaza")
        self.assertIsNotNone(r.reservation_id)

    def test_create_reservation_increments_reserved(self):
        self._setup_hotel_and_customer()
        Reservation.create_reservation("C001", "Plaza")
        info = Hotel.display_hotel("Plaza")
        self.assertIn("Reserved Rooms: 1", info)

    def test_cancel_reservation_success(self):
        self._setup_hotel_and_customer()
        r = Reservation.create_reservation("C001", "Plaza")
        Reservation.cancel_reservation(r.reservation_id)
        info = Hotel.display_hotel("Plaza")
        self.assertIn("Reserved Rooms: 0", info)

    def test_multiple_reservations_and_cancellations(self):
        Hotel.create_hotel("Plaza", "CDMX", 10)
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        Customer.create_customer("C002", "Bob", "bob@mail.com")
        r1 = Reservation.create_reservation("C001", "Plaza")
        r2 = Reservation.create_reservation("C002", "Plaza")
        info = Hotel.display_hotel("Plaza")
        self.assertIn("Reserved Rooms: 2", info)
        Reservation.cancel_reservation(r1.reservation_id)
        info = Hotel.display_hotel("Plaza")
        self.assertIn("Reserved Rooms: 1", info)
        Reservation.cancel_reservation(r2.reservation_id)
        info = Hotel.display_hotel("Plaza")
        self.assertIn("Reserved Rooms: 0", info)

    def test_to_dict_and_from_dict(self):
        r = Reservation("R001", "C001", "Plaza")
        data = r.to_dict()
        r2 = Reservation.from_dict(data)
        self.assertEqual(r2.reservation_id, "R001")
        self.assertEqual(r2.customer_id, "C001")
        self.assertEqual(r2.hotel_name, "Plaza")

    # --- Corrupt file handling ---

    def test_load_reservations_corrupt_file_returns_empty(self):
        corrupt_path = os.path.join(self.temp_dir, "reservations.json")
        with open(corrupt_path, "w", encoding="utf-8") as f:
            f.write("NOT VALID JSON {{{")
        result = reservation_module._load_reservations()
        self.assertEqual(result, {})

    def test_load_reservations_corrupt_file_prints_warning(self):
        corrupt_path = os.path.join(self.temp_dir, "reservations.json")
        with open(corrupt_path, "w", encoding="utf-8") as f:
            f.write("NOT VALID JSON {{{")
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            reservation_module._load_reservations()
        self.assertIn("Warning", buf.getvalue())

    # =========================================================
    # Negative Tests
    # =========================================================

    def test_neg_create_reservation_nonexistent_customer_raises(self):
        """Reserving with a customer ID that does not exist must fail."""
        Hotel.create_hotel("Plaza", "CDMX", 10)
        with self.assertRaises(ValueError):
            Reservation.create_reservation("C999", "Plaza")

    def test_neg_create_reservation_nonexistent_hotel_raises(self):
        """Reserving at a hotel that does not exist must fail."""
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        with self.assertRaises(ValueError):
            Reservation.create_reservation("C001", "Ghost")

    def test_neg_create_reservation_hotel_fully_booked_raises(self):
        """Reserving at a hotel with no available rooms must fail."""
        Hotel.create_hotel("Tiny", "CDMX", 1)
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        Reservation.create_reservation("C001", "Tiny")
        Customer.create_customer("C002", "Bob", "bob@mail.com")
        with self.assertRaises(ValueError):
            Reservation.create_reservation("C002", "Tiny")

    def test_neg_create_reservation_empty_customer_id_raises(self):
        """Reserving with an empty customer ID must fail."""
        Hotel.create_hotel("Plaza", "CDMX", 10)
        with self.assertRaises(ValueError):
            Reservation.create_reservation("", "Plaza")

    def test_neg_create_reservation_empty_hotel_name_raises(self):
        """Reserving at an empty hotel name must fail."""
        Customer.create_customer("C001", "Alice", "alice@mail.com")
        with self.assertRaises(ValueError):
            Reservation.create_reservation("C001", "")

    def test_neg_cancel_nonexistent_reservation_raises(self):
        """Cancelling a reservation ID that does not exist must fail."""
        with self.assertRaises(ValueError):
            Reservation.cancel_reservation("FAKE-ID")

    def test_neg_cancel_already_cancelled_reservation_raises(self):
        """Cancelling the same reservation twice must fail."""
        self._setup_hotel_and_customer()
        r = Reservation.create_reservation("C001", "Plaza")
        Reservation.cancel_reservation(r.reservation_id)
        with self.assertRaises(ValueError):
            Reservation.cancel_reservation(r.reservation_id)

    def test_neg_cancel_reservation_empty_id_raises(self):
        """Cancelling with an empty reservation ID must fail."""
        with self.assertRaises(ValueError):
            Reservation.cancel_reservation("")

    def test_neg_create_reservation_both_missing_raises(self):
        """Reserving when both customer and hotel are absent must fail."""
        with self.assertRaises(ValueError):
            Reservation.create_reservation("C999", "Ghost")


if __name__ == "__main__":
    unittest.main()
