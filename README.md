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

Run tests:

```bash
cd A01795565_A6.2/1-reservation
python -m pytest tests/ -v
```

## What It Does

Implements three abstractions (Hotel, Customer, Reservation) with persistent behaviors stored in JSON files. Supports full CRUD operations for hotels and customers, plus room reservation management.

## Classes

### Hotel (`source/hotel.py`)
- **Attributes:** name, location, total_rooms, reserved_rooms
- **Behaviors:**
  - Create Hotel
  - Delete Hotel
  - Display Hotel Information
  - Modify Hotel Information
  - Reserve a Room
  - Cancel a Reservation

## Folder Structure

```
1-reservation/
├── README.md
├── requirements.txt
├── source/          # Source code (files)
├── data/            # Persistent JSON data files (auto-created)
├── tests/           # Unit tests
└── results/         # Output files
```
