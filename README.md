# A6.2 - Reservation System

Python program that implements a hotel reservation system with persistent storage.

Name: **Ramiro González Carrillo**

Student No: **A01795565**

Email: **a01795565@tec.mx**

Professors

Associate Professor: **Dr. Gerardo Padilla Zárate**

Assistant Professor: **Mtra. Viridiana Rodríguez González**

Faculty Tutor: **Mtra. Circe Diana Carrillo Martínez**

## Usage

Run tests with coverage (from project root):

```bash
python -m pytest 1-reservation/tests/ -v --cov=1-reservation/source --cov-report=term-missing
```

Run tests with coverage (from inside `1-reservation/`):

```bash
cd 1-reservation
python -m pytest tests/ -v --cov=source --cov-report=term-missing
```

Run tests only:

```bash
python -m pytest 1-reservation/tests/ -v
```

## What It Does

Implements three abstractions (Hotel, Customer, Reservation) with persistent
behaviors stored in JSON files. Supports full CRUD operations for hotels and
customers, plus room reservation management. Corrupted or missing data files
are handled gracefully — a warning is printed to the console and execution
continues with an empty store.

## Classes

### Hotel (`source/hotel.py`)

- **Attributes:** `name`, `location`, `total_rooms`, `reserved_rooms`
- **Behaviors:**
  - Create Hotel
  - Delete Hotel
  - Display Hotel Information
  - Modify Hotel Information (name, location, total rooms)
  - Reserve a Room
  - Cancel a Room Reservation

### Customer (`source/customer.py`)

- **Attributes:** `customer_id`, `name`, `email`
- **Behaviors:**
  - Create Customer
  - Delete Customer
  - Display Customer Information
  - Modify Customer Information (name, email)

### Reservation (`source/reservation.py`)

- **Attributes:** `reservation_id`, `customer_id`, `hotel_name`
- **Behaviors:**
  - Create a Reservation (validates Customer and Hotel, reserves a room)
  - Cancel a Reservation (frees the room back at the hotel)

## Persistence

All data is stored as JSON files in the `data/` directory (auto-created at
runtime):

- `hotels.json` — Hotel records
- `customers.json` — Customer records
- `reservations.json` — Reservation records

If any file is corrupt or malformed, a warning is printed and the program
continues with an empty store for that entity.

## Tests

70 unit tests covering all CRUD operations, input validation, edge cases,
serialization, and corrupt file handling:

- `tests/test_hotel.py` — 34 tests
- `tests/test_customer.py` — 20 tests
- `tests/test_reservation.py` — 16 tests

### Code Quality

| Check | Result |
|---|---|
| Line coverage | **100%** |
| Flake8 | **0 warnings** |
| PyLint | **10.00 / 10** |

## Folder Structure

```
1-reservation/
├── README.md
├── requirements.txt
├── source/          # Source code (hotel.py, customer.py, reservation.py)
├── data/            # Persistent JSON data files (auto-created at runtime)
├── tests/           # Unit tests (test_hotel.py, test_customer.py, test_reservation.py)
└── results/         # Output files
```