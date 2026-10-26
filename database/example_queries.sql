
USE harborwing_air;

-- QUERY 1: View reservations with passengers,
-- agents, payments, and flight legs.
SELECT
    r.reservation_id,
    p.first_name,
    p.last_name,
    ba.agent_name,
    r.reservation_status_code,
    r.party_size,
    pay.payment_ids,
    leg.leg_ids
FROM reservation r
JOIN passenger p
    ON p.passenger_id = r.passenger_id
LEFT JOIN booking_agent ba
    ON ba.agent_id = r.agent_id
LEFT JOIN (
    SELECT rp.reservation_id,
           GROUP_CONCAT(rp.payment_id) AS payment_ids
    FROM reservation_payment rp
    GROUP BY rp.reservation_id
) pay ON pay.reservation_id = r.reservation_id
LEFT JOIN (
    SELECT rl.reservation_id,
           GROUP_CONCAT(rl.leg_id) AS leg_ids
    FROM reservation_leg rl
    GROUP BY rl.reservation_id
) leg ON leg.reservation_id = r.reservation_id;


-- QUERY 2: Find reservations using a particular leg.
SELECT r.reservation_id, r.party_size
FROM reservation r
JOIN reservation_leg rl
    ON rl.reservation_id = r.reservation_id
WHERE rl.leg_id = 1;


-- QUERY 3: Find payments linked to a reservation.
SELECT
    p.payment_id,
    p.payment_status_code,
    p.payment_date,
    p.payment_amount
FROM payment p
JOIN reservation_payment rp
    ON rp.payment_id = p.payment_id
WHERE rp.reservation_id = 1;


-- QUERY 4: Find a flight cost for a flight,
-- aircraft type, and travel date.
SELECT
    flight_number,
    aircraft_type_code,
    valid_from,
    valid_to,
    cost_amount
FROM flight_cost
WHERE flight_number = 'HW001'
  AND aircraft_type_code = 'AT01'
  AND valid_from <= '2026-06-15'
  AND valid_to >= '2026-06-15'
ORDER BY valid_from DESC;
