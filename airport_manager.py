######################## IMPORTANT ########################
""" Do not rename the variables or functions.
Do not change the function parameters.
Do not add input() calls inside airport_manager.py.
The file must be importable by the tests. """
###########################################################


# ---------------------------------------------------------------------------
# Result codes returned by the functions below.
# ---------------------------------------------------------------------------
OK = "OK"
FLIGHT_NOT_FOUND = "FLIGHT_NOT_FOUND"
EMPTY_NAME = "EMPTY_NAME"
DUPLICATE = "DUPLICATE"
FULL = "FULL"
RESTRICTED = "RESTRICTED"
PASSENGER_NOT_FOUND = "PASSENGER_NOT_FOUND"
INVALID_GATE = "INVALID_GATE"


# ---------------------------------------------------------------------------
# Airport data
# ---------------------------------------------------------------------------

# tuple -> (code, terminal, date): the airport identity never changes.
airport_info = ("OUL", 1, "14-09-2026")

# set -> membership tests are O(1) and duplicate gates/destinations
# cannot be stored twice.
allowed_gates = {"A1", "A2", "A3", "A4", "B1", "B2"}
restricted_destinations = {"Moscow", "Pyongyang"}

# dict -> flight number (key) mapped to a flight record.
# Each record is itself a dict; the passenger names are kept in a list so the
# manifest stays ordered and can grow/shrink as people check in and out.
flights = {
    "AY450": {
        "destination": "Helsinki",
        "departure": "08:30",
        "gate": "A2",
        "capacity": 5,
        "passengers": [
            "Alice Wong",
            "David Kim",
            "Fatima Ali"
        ]
    },
    "SK271": {
        "destination": "Stockholm",
        "departure": "10:15",
        "gate": "B1",
        "capacity": 4,
        "passengers": [
            "Chen Wei",
            "George Smith"
        ]
    },
    "LH2491": {
        "destination": "Munich",
        "departure": "12:40",
        "gate": "A4",
        "capacity": 5,
        "passengers": [
            "Hana Lee",
            "Maria Garcia",
            "Noah Wilson"
        ]
    }
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalise(value):
    """Return *value* as a trimmed, single-spaced, upper-case string.

    Anything that is not a string (including None) becomes "" so that the
    public functions never crash on unexpected input.
    """
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).upper()


def _display_name(value):
    """Return the canonical stored form of a passenger name ("Alice Wong")."""
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).title()


def _passenger_list(flight):
    """Return the passenger list of *flight*, creating it when missing."""
    passengers = flight.get("passengers")
    if not isinstance(passengers, list):
        passengers = []
        flight["passengers"] = passengers
    return passengers


def _is_restricted(destination, restricted_destinations):
    """True when *destination* is in the restricted set (case-insensitive)."""
    if not restricted_destinations:
        return False

    target = _normalise(destination)

    if not target:
        return False

    for restricted in restricted_destinations:
        if _normalise(restricted) == target:
            return True

    return False


## Logic to find if a flight exists
def find_flight(flights, flight_number):
    """Return the normalised flight key stored in *flights*, or None."""
    if not isinstance(flights, dict):
        return None

    target = _normalise(flight_number)

    if not target:
        return None

    # Fast path: the key is already stored in its normalised form.
    if target in flights:
        return target

    # Slow path: the stored key needs normalising (extra spaces / lower case).
    for key in flights:
        if _normalise(key) == target:
            return key

    return None


## Logic to find if a passenger exists
def passenger_exists(passengers, passenger_name):
    """Return True/False - case-insensitive passenger lookup."""
    if not passengers:
        return False

    target = _normalise(passenger_name)

    if not target:
        return False

    for passenger in passengers:
        if _normalise(passenger) == target:
            return True

    return False


## Logic to check in a passenger
def check_in_passenger(
    flights,
    flight_number,
    passenger_name,
    restricted_destinations
):
    """Check a passenger in and return the matching result code."""
    flight_key = find_flight(flights, flight_number)

    if flight_key is None:
        return FLIGHT_NOT_FOUND

    name = _display_name(passenger_name)

    if not name:
        return EMPTY_NAME

    flight = flights[flight_key]
    passengers = _passenger_list(flight)

    if passenger_exists(passengers, name):
        return DUPLICATE

    capacity = flight.get("capacity", 0)

    if not isinstance(capacity, int):
        capacity = 0

    if len(passengers) >= capacity:
        return FULL

    if _is_restricted(flight.get("destination"), restricted_destinations):
        return RESTRICTED

    passengers.append(name)

    return OK


## Logic to remove a passenger from a flight
def remove_passenger(
    flights,
    flight_number,
    passenger_name
):
    """Remove a passenger from a flight and return the result code."""
    flight_key = find_flight(flights, flight_number)

    if flight_key is None:
        return FLIGHT_NOT_FOUND

    passengers = _passenger_list(flights[flight_key])

    target = _normalise(passenger_name)

    if not target:
        return PASSENGER_NOT_FOUND

    for index, passenger in enumerate(passengers):
        if _normalise(passenger) == target:
            passengers.pop(index)
            return OK

    return PASSENGER_NOT_FOUND


# Logic to change the gate of a flight
def change_gate(
    flights,
    flight_number,
    new_gate,
    allowed_gates
):
    """Move a flight to *new_gate* when that gate is allowed."""
    flight_key = find_flight(flights, flight_number)

    if flight_key is None:
        return FLIGHT_NOT_FOUND

    target = _normalise(new_gate)

    if not target or not allowed_gates:
        return INVALID_GATE

    # Keep the gate exactly as it is spelled in allowed_gates.
    for gate in allowed_gates:
        if _normalise(gate) == target:
            flights[flight_key]["gate"] = gate
            return OK

    return INVALID_GATE


# Logic to get the status of a flight
def flight_status(flight):
    """Return AVAILABLE, ALMOST FULL or FULL for *flight*."""
    capacity = flight.get("capacity", 0)

    if not isinstance(capacity, int) or capacity <= 0:
        return FULL

    passengers = flight.get("passengers") or []

    percentage = len(passengers) / capacity * 100

    if percentage == 100:
        return FULL

    if percentage >= 75:
        return "ALMOST FULL"

    return "AVAILABLE"


# Logic to get the sorted manifest of a flight
def sorted_manifest(
    flights,
    flight_number
):
    """Return a new alphabetically sorted list of names, or None."""
    flight_key = find_flight(flights, flight_number)

    if flight_key is None:
        return None

    passengers = flights[flight_key].get("passengers") or []

    return sorted(passengers)


# Logic to get the total number of passengers across all flights
def total_passengers(flights):
    """Return the total number of checked-in passengers."""
    if not flights:
        return 0

    total = 0

    for flight in flights.values():
        total += len(flight.get("passengers") or [])

    return total


# Logic to check if any flight is full
def any_full_flight(flights):
    """Return True when at least one flight has no seats left."""
    if not flights:
        return False

    for flight in flights.values():
        capacity = flight.get("capacity", 0)

        if not isinstance(capacity, int):
            capacity = 0

        if len(flight.get("passengers") or []) >= capacity:
            return True

    return False


# Logic to check if all flights have at least one passenger
def all_flights_have_passengers(flights):
    """Return True when every flight has at least one passenger."""
    for flight in (flights or {}).values():
        if not flight.get("passengers"):
            return False

    return True
