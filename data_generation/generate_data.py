"""
HarborWing Air synthetic data generator.

Target schema: the 11 core tables from harborwing_schema.sql.
Dependencies: Faker, mysql-connector-python

IMPORTANT:
- Review DB_CONFIG before running.
- Run with --reset to clear existing rows from these 11 tables and repopulate them.
- The reset deletes table data, not the tables themselves.
- Uses fictional/demo data and a fixed random seed for repeatability.
"""

import argparse
import random
from datetime import date, datetime, time, timedelta

import mysql.connector
from faker import Faker

SEED = 42
random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "root",  # XAMPP default is often blank; change if you configured a password.
    "database": "harborwing_air",
}

ROW_COUNT = 50
CALENDAR_START = date(2026, 1, 1)
CALENDAR_DAYS = 400
AIRCRAFT_CODES = [f"AT{i:02d}" for i in range(1, 11)]
AIRLINE_CODES = ["HWA", "HWB", "HWC", "HWD", "HWE"]


def make_email(first, last, number):
    return f"{first.lower()}.{last.lower()}.{number}@example.com"


def execute_many(cursor, sql, rows):
    if rows:
        cursor.executemany(sql, rows)


def reset_tables(cursor):
    """Delete data child-first so foreign-key constraints remain valid."""
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in (
        "reservation_leg",
        "reservation_payment",
        "flight_cost",
        "flight_leg",
        "reservation",
        "payment",
        "flight_schedule",
        "calendar_date",
        "airport",
        "passenger",
        "booking_agent",
    ):
        cursor.execute(f"DELETE FROM `{table}`")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def populate(connection):
    cursor = connection.cursor()
    try:
        reset_tables(cursor)

        # 1. Parent/reference data: airports and calendar dates.
        airports = []
        for i in range(1, ROW_COUNT + 1):
            city = fake.unique.city()
            airports.append((
                f"AP{i:03d}",
                f"{city} Regional Airport",
                f"{city}, {fake.country()}",
                "Fictional demonstration airport",
            ))
        execute_many(
            cursor,
            """INSERT INTO airport
               (airport_code, airport_name, location, other_details)
               VALUES (%s, %s, %s, %s)""",
            airports,
        )

        calendar_rows = []
        for offset in range(CALENDAR_DAYS):
            d = CALENDAR_START + timedelta(days=offset)
            calendar_rows.append((d, d.day, d.weekday() < 5))
        execute_many(
            cursor,
            """INSERT INTO calendar_date
               (calendar_day, day_of_month, is_business_day)
               VALUES (%s, %s, %s)""",
            calendar_rows,
        )
        calendar_dates = [row[0] for row in calendar_rows]

        # 2. Booking agents and passengers.
        agents = []
        for i in range(1, ROW_COUNT + 1):
            first, last = fake.first_name(), fake.last_name()
            agents.append((
                i,
                f"{fake.company()} Travel Desk",
                make_email(first, last, i),
                fake.phone_number()[:30],
                "Fictional booking agent",
            ))
        execute_many(
            cursor,
            """INSERT INTO booking_agent
               (agent_id, agent_name, contact_email, phone, other_details)
               VALUES (%s, %s, %s, %s, %s)""",
            agents,
        )

        passengers = []
        for i in range(1, ROW_COUNT + 1):
            first, last = fake.first_name(), fake.last_name()
            passengers.append((
                i, first, fake.first_name() if i % 3 == 0 else None, last,
                fake.phone_number()[:30], make_email(first, last, i),
                fake.street_address(), None if i % 2 else fake.secondary_address(),
                fake.city(), fake.state(), fake.country(),
                "Fictional passenger generated for coursework",
            ))
        execute_many(
            cursor,
            """INSERT INTO passenger
               (passenger_id, first_name, second_name, last_name, phone, email,
                address_line1, address_line2, city, state_province_county,
                country, other_details)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            passengers,
        )

        # 3. Scheduled flights. Every route has different origin/destination.
        airport_codes = [row[0] for row in airports]
        schedules = []
        for i in range(1, ROW_COUNT + 1):
            origin = airport_codes[(i - 1) % len(airport_codes)]
            destination = airport_codes[(i + 6) % len(airport_codes)]
            depart_day = CALENDAR_START + timedelta(days=(i - 1) % 300)
            depart_dt = datetime.combine(depart_day, time(7 + (i % 10), (i * 7) % 60))
            arrive_dt = depart_dt + timedelta(minutes=75 + (i * 13) % 240)
            schedules.append((
                f"HW{i:03d}",
                AIRLINE_CODES[(i - 1) % len(AIRLINE_CODES)],
                AIRCRAFT_CODES[(i - 1) % len(AIRCRAFT_CODES)],
                origin, destination, depart_dt, arrive_dt,
            ))
        execute_many(
            cursor,
            """INSERT INTO flight_schedule
               (flight_number, airline_code, usual_aircraft_type_code,
                origin_airport_code, destination_airport_code,
                scheduled_departure, scheduled_arrival)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            schedules,
        )

        # 4. Flight legs: 50 rows, with actual times sometimes unknown.
        legs = []
        for i, flight in enumerate(schedules, start=1):
            scheduled_departure = flight[5]
            has_actual = (i % 4 != 0)
            actual_departure = (
                scheduled_departure + timedelta(minutes=(i % 18))
                if has_actual else None
            )
            actual_arrival = (
                flight[6] + timedelta(minutes=(i % 25))
                if has_actual else None
            )
            legs.append((
                i, flight[0], flight[3], flight[4],
                actual_departure, actual_arrival,
            ))
        execute_many(
            cursor,
            """INSERT INTO flight_leg
               (leg_id, flight_number, origin_airport_code,
                destination_airport_code, actual_departure, actual_arrival)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            legs,
        )

        # 5. Reservations and payments.
        reservations = []
        for i in range(1, ROW_COUNT + 1):
            reservations.append((
                i, i, None if i % 3 == 0 else ((i - 1) % ROW_COUNT) + 1,
                ["CONFIRMED", "PENDING", "CANCELLED"][i % 3],
                ["STANDARD", "FLEX", "BUSINESS"][i % 3],
                ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS"][i % 3],
                datetime(2026, 1, 1, 8, 0) + timedelta(days=i),
                1 + (i % 5),
            ))
        execute_many(
            cursor,
            """INSERT INTO reservation
               (reservation_id, passenger_id, agent_id,
                reservation_status_code, ticket_type_code, travel_class_code,
                created_at, party_size)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            reservations,
        )

        payments = []
        for i in range(1, ROW_COUNT + 1):
            payment_day = CALENDAR_START + timedelta(days=(i - 1) % 300)
            payments.append((
                i,
                ["PAID", "PENDING", "REFUNDED"][i % 3],
                datetime.combine(payment_day, time(10 + (i % 8), (i * 3) % 60)),
                round(75 + random.uniform(10, 900), 2),
            ))
        execute_many(
            cursor,
            """INSERT INTO payment
               (payment_id, payment_status_code, payment_date, payment_amount)
               VALUES (%s, %s, %s, %s)""",
            payments,
        )

        # 6. Flight costs: each start/end date exists in calendar_date.
        costs = []
        for i, flight in enumerate(schedules, start=1):
            valid_from = calendar_dates[(i - 1) % 300]
            valid_to = valid_from + timedelta(days=30 + (i % 90))
            costs.append((
                flight[0], AIRCRAFT_CODES[(i - 1) % len(AIRCRAFT_CODES)],
                valid_from, valid_to, round(100 + random.uniform(0, 2500), 2),
            ))
        execute_many(
            cursor,
            """INSERT INTO flight_cost
               (flight_number, aircraft_type_code, valid_from, valid_to, cost_amount)
               VALUES (%s, %s, %s, %s, %s)""",
            costs,
        )

        # 7. Link tables: 100 unique pairs each. Each reservation has
        # two payments and two legs; payments/legs are shared across bookings.
        reservation_payment = []
        reservation_leg = []
        for i in range(1, ROW_COUNT + 1):
            next_id = (i % ROW_COUNT) + 1
            reservation_payment.append((i, i))
            reservation_payment.append((i, next_id))
            reservation_leg.append((i, i))
            reservation_leg.append((i, next_id))

        execute_many(
            cursor,
            """INSERT INTO reservation_payment (reservation_id, payment_id)
               VALUES (%s, %s)""",
            reservation_payment,
        )
        execute_many(
            cursor,
            """INSERT INTO reservation_leg (reservation_id, leg_id)
               VALUES (%s, %s)""",
            reservation_leg,
        )

        connection.commit()
        print("\nData generation completed successfully.")
        print("Core tables populated. Row counts:")
        for table in (
            "booking_agent", "passenger", "airport", "calendar_date",
            "flight_schedule", "flight_leg", "reservation", "payment",
            "flight_cost", "reservation_payment", "reservation_leg",
        ):
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            print(f"  {table:<22} {count:>5}")
            if count < ROW_COUNT:
                raise RuntimeError(f"{table} has fewer than {ROW_COUNT} rows.")

    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def main():
    parser = argparse.ArgumentParser(description="Generate HarborWing Air demo data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing rows from the 11 core tables before inserting demo data.",
    )
    args = parser.parse_args()

    if not args.reset:
        print("Safety stop: this script resets the 11 core tables before seeding.")
        print("Review DB_CONFIG, back up anything important, then run with --reset.")
        print("Example: python generate_data.py --reset")
        return

    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        populate(connection)
    except mysql.connector.Error as exc:
        print(f"\nDatabase error: {exc}")
        print("Check that MariaDB/MySQL is running and DB_CONFIG is correct.")
        print("For XAMPP, the usual settings are host 127.0.0.1, port 3306, user root.")
        raise SystemExit(1)
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
