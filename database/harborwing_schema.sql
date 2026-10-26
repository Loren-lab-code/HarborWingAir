
CREATE DATABASE IF NOT EXISTS harborwing_air;
USE harborwing_air;

CREATE TABLE booking_agent (
    agent_id INT AUTO_INCREMENT PRIMARY KEY,
    agent_name VARCHAR(150) NOT NULL,
    contact_email VARCHAR(255),
    phone VARCHAR(30),
    other_details TEXT
) ENGINE=InnoDB;

CREATE TABLE passenger (
    passenger_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    second_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(255),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province_county VARCHAR(100),
    country VARCHAR(100),
    other_details TEXT,
    INDEX idx_passenger_name (last_name, first_name)
) ENGINE=InnoDB;

CREATE TABLE airport (
    airport_code VARCHAR(10) PRIMARY KEY,
    airport_name VARCHAR(150) NOT NULL,
    location VARCHAR(255) NOT NULL,
    other_details TEXT
) ENGINE=InnoDB;

CREATE TABLE calendar_date (
    calendar_day DATE PRIMARY KEY,
    day_of_month TINYINT NOT NULL,
    is_business_day BOOLEAN NOT NULL,
    CHECK (day_of_month BETWEEN 1 AND 31)
) ENGINE=InnoDB;

CREATE TABLE flight_schedule (
    flight_number VARCHAR(20) PRIMARY KEY,
    airline_code VARCHAR(10) NOT NULL,
    usual_aircraft_type_code VARCHAR(20) NOT NULL,
    origin_airport_code VARCHAR(10) NOT NULL,
    destination_airport_code VARCHAR(10) NOT NULL,
    scheduled_departure DATETIME NOT NULL,
    scheduled_arrival DATETIME NOT NULL,
    CHECK (origin_airport_code <> destination_airport_code),
    CHECK (scheduled_arrival > scheduled_departure),
    FOREIGN KEY (origin_airport_code)
        REFERENCES airport(airport_code) ON DELETE RESTRICT,
    FOREIGN KEY (destination_airport_code)
        REFERENCES airport(airport_code) ON DELETE RESTRICT,
    INDEX idx_schedule_route (origin_airport_code, destination_airport_code),
    INDEX idx_schedule_departure (scheduled_departure)
) ENGINE=InnoDB;

CREATE TABLE flight_leg (
    leg_id INT AUTO_INCREMENT PRIMARY KEY,
    flight_number VARCHAR(20) NOT NULL,
    origin_airport_code VARCHAR(10) NOT NULL,
    destination_airport_code VARCHAR(10) NOT NULL,
    actual_departure DATETIME,
    actual_arrival DATETIME,
    CHECK (origin_airport_code <> destination_airport_code),
    CHECK (
        actual_departure IS NULL OR actual_arrival IS NULL
        OR actual_arrival >= actual_departure
    ),
    FOREIGN KEY (flight_number)
        REFERENCES flight_schedule(flight_number) ON DELETE RESTRICT,
    FOREIGN KEY (origin_airport_code)
        REFERENCES airport(airport_code) ON DELETE RESTRICT,
    FOREIGN KEY (destination_airport_code)
        REFERENCES airport(airport_code) ON DELETE RESTRICT,
    INDEX idx_leg_flight (flight_number)
) ENGINE=InnoDB;

CREATE TABLE reservation (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    passenger_id INT NOT NULL,
    agent_id INT NULL,
    reservation_status_code VARCHAR(30) NOT NULL,
    ticket_type_code VARCHAR(30) NOT NULL,
    travel_class_code VARCHAR(30) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    party_size INT NOT NULL,
    CHECK (party_size > 0),
    FOREIGN KEY (passenger_id)
        REFERENCES passenger(passenger_id) ON DELETE RESTRICT,
    FOREIGN KEY (agent_id)
        REFERENCES booking_agent(agent_id) ON DELETE RESTRICT,
    INDEX idx_reservation_passenger (passenger_id),
    INDEX idx_reservation_agent (agent_id),
    INDEX idx_reservation_status (reservation_status_code)
) ENGINE=InnoDB;

CREATE TABLE payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_status_code VARCHAR(30) NOT NULL,
    payment_date DATETIME NOT NULL,
    payment_amount DECIMAL(12,2) NOT NULL,
    CHECK (payment_amount > 0)
) ENGINE=InnoDB;

CREATE TABLE flight_cost (
    flight_number VARCHAR(20) NOT NULL,
    aircraft_type_code VARCHAR(20) NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    cost_amount DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (flight_number, aircraft_type_code, valid_from),
    CHECK (valid_to >= valid_from),
    CHECK (cost_amount >= 0),
    FOREIGN KEY (flight_number)
        REFERENCES flight_schedule(flight_number) ON DELETE RESTRICT,
    FOREIGN KEY (valid_from)
        REFERENCES calendar_date(calendar_day) ON DELETE RESTRICT,
    FOREIGN KEY (valid_to)
        REFERENCES calendar_date(calendar_day) ON DELETE RESTRICT,
    INDEX idx_cost_lookup (aircraft_type_code, valid_from, valid_to)
) ENGINE=InnoDB;

CREATE TABLE reservation_payment (
    reservation_id INT NOT NULL,
    payment_id INT NOT NULL,
    PRIMARY KEY (reservation_id, payment_id),
    FOREIGN KEY (reservation_id)
        REFERENCES reservation(reservation_id) ON DELETE CASCADE,
    FOREIGN KEY (payment_id)
        REFERENCES payment(payment_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE reservation_leg (
    reservation_id INT NOT NULL,
    leg_id INT NOT NULL,
    PRIMARY KEY (reservation_id, leg_id),
    FOREIGN KEY (reservation_id)
        REFERENCES reservation(reservation_id) ON DELETE CASCADE,
    FOREIGN KEY (leg_id)
        REFERENCES flight_leg(leg_id) ON DELETE CASCADE
) ENGINE=InnoDB;







