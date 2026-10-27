class SeatManager:
    """In-memory seat ownership. Seats start available every time the app launches."""
    def __init__(self):
        self._owners = {}

    def status(self, seat_id):
        return "occupied" if seat_id in self._owners else "available"

    def owner(self, seat_id):
        return self._owners.get(seat_id)

    def occupy(self, seat_id, student_number):
        if seat_id in self._owners:
            return False, "This seat is already occupied."
        self._owners[seat_id] = student_number
        return True, "Seat occupied."

    def release(self, seat_id, student_number):
        owner = self._owners.get(seat_id)
        if owner is None:
            return False, "This seat is already available."
        if owner != student_number:
            return False, "Only the same student number that occupied this seat can log out."
        del self._owners[seat_id]
        return True, "Seat is now available."
