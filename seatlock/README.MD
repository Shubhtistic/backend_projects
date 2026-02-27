# SeatLock API

A backend service for a ticket booking system built with FastAPI and PostgreSQL. This project focuses on the hard parts of backend engineering — strict relational data modeling, ACID-compliant transactions, and preventing race conditions (double-booking) in a concurrent environment.

This is not a tutorial project. Every architectural decision here is intentional and targets a specific real-world backend problem.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (Python) |
| Database | PostgreSQL |
| Infrastructure | Docker & Docker Compose |
| Language | Python 3.11+ |
| DB Driver | asyncpg (async PostgreSQL) |

---

## Core Engineering Objectives

This system is being developed incrementally to master specific backend architecture patterns:

- [ ] **Phase 1: Relational Schema Design** — Normalizing Users, Venues, Shows, and Seats with strict foreign key constraints and well-thought-out indexing.
- [ ] **Phase 2: State & Concurrency** — Implementing pessimistic locking (`SELECT FOR UPDATE`) to prevent double-booking anomalies during simultaneous checkout requests.
- [ ] **Phase 3: Containerization** — Structuring the application and database within isolated Docker bridge networks with environment-based configuration.

---

## The Core Problem This Solves

Imagine two users try to book the same seat at the exact same moment. Without proper handling, both requests read the seat as available, both proceed to book, and you end up with two confirmed bookings for one seat — a classic race condition.

SeatLock solves this using **pessimistic locking** at the database level. When a booking request comes in, the row is locked with `SELECT FOR UPDATE` before any state change happens. Any concurrent request trying to touch the same row is blocked until the first transaction completes. This guarantees that only one booking can succeed.


---

## Data Model Overview

```
Users ──< Bookings >── Seats
                         │
                       Shows
                         │
                       Venues
```

- A **User** can have many **Bookings**.
- A **Booking** belongs to one **Seat** and one **Show**.
- A **Show** takes place at a **Venue** and has many **Seats**.
- A **Seat** can only have one active **Booking** at a time (enforced at DB level).



---

## API Endpoints (Planned)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/users/register` | Register a new user |
| `GET` | `/shows` | List all available shows |
| `GET` | `/shows/{id}/seats` | Get available seats for a show |
| `POST` | `/bookings` | Book a seat (with locking) |
| `DELETE` | `/bookings/{id}` | Cancel a booking |

---

## Why PostgreSQL

This project specifically uses PostgreSQL because:

- ACID-compliant transactions are required for safe seat booking.
- `SELECT FOR UPDATE` pessimistic locking is a first-class, well-documented feature.
- Foreign key constraints enforce relational integrity across all entities.
- Row-level locking behavior is predictable and battle-tested at scale.
- Relational data modeling is a primary learning objective of this project.

A key-value or document store like Redis or MongoDB would not provide the transactional guarantees this use case demands without significant workarounds.

---

## Current Status

**Version:** V1 — Local Development  
**Stage:** In Progress  
**Next milestone:** Phase 1 schema finalized and migrated