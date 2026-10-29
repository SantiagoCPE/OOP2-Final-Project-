import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timedelta

MAX_RESERVATIONS_PER_DAY = 5
MAX_RESERVATION_MINUTES = 30

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
STATE_FILE = os.path.join(DATA_DIR, "seat_state.json")
_FMT = "%Y-%m-%dT%H:%M:%S"


class SeatManager:
    """Seat data shared by EVERY running copy of the app (student, entrance, librarian).

    State lives in data/seat_state.json. Every query first checks whether the file changed
    (another window/computer wrote to it) and reloads, so all versions show the same live
    green/yellow/red status. Every change is saved immediately.
    """

    def __init__(self, state_file=STATE_FILE):
        self.state_file = state_file
        self._owners = {}          # seat_id -> student number          (occupied / red)
        self._reservations = {}    # seat_id -> [ {student,date,start,end} ]  (reserved / yellow)
        self._since = {}           # seat_id -> datetime the occupant logged in
        self._stamp = None
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        self._sync(force=True)

    # ---------- persistence / cross-window sync ----------
    def _file_stamp(self):
        try:
            st = os.stat(self.state_file)
            return (st.st_mtime_ns, st.st_size)
        except OSError:
            return None

    def _sync(self, force=False):
        stamp = self._file_stamp()
        if not force and stamp == self._stamp:
            return
        self._owners, self._reservations, self._since = {}, {}, {}
        if stamp is not None:
            try:
                with open(self.state_file, encoding="utf-8") as f:
                    raw = json.load(f)
                self._owners = dict(raw.get("owners", {}))
                for seat, when in raw.get("since", {}).items():
                    self._since[seat] = datetime.strptime(when, _FMT)
                for seat, lst in raw.get("reservations", {}).items():
                    self._reservations[seat] = [
                        {"student": r["student"], "date": r["date"],
                         "start": datetime.strptime(r["start"], _FMT),
                         "end": datetime.strptime(r["end"], _FMT)} for r in lst]
            except (OSError, ValueError, KeyError):
                self._owners, self._reservations, self._since = {}, {}, {}   # unreadable file -> start clean
        self._stamp = stamp

    def _save(self):
        raw = {"owners": self._owners,
               "since": {seat: when.strftime(_FMT) for seat, when in self._since.items()},
               "reservations": {seat: [{"student": r["student"], "date": r["date"],
                                        "start": r["start"].strftime(_FMT), "end": r["end"].strftime(_FMT)}
                                       for r in lst] for seat, lst in self._reservations.items()}}
        tmp = self.state_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2)
        os.replace(tmp, self.state_file)
        self._stamp = self._file_stamp()

    @contextmanager
    def _transaction(self):
        """Lock -> reload newest data -> (caller changes it) -> save. Prevents two windows overwriting each other."""
        lock = self.state_file + ".lock"
        deadline = time.time() + 3
        fd = None
        while fd is None:
            try:
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(lock) > 5:   # stale lock from a crashed window
                        os.remove(lock); continue
                except OSError:
                    pass
                if time.time() > deadline:
                    break
                time.sleep(0.03)
        try:
            self._sync(force=True)
            yield
        finally:
            if fd is not None:
                os.close(fd)
                try: os.remove(lock)
                except OSError: pass

    # ---------- queries ----------
    def status(self, seat_id):
        self._sync()
        if seat_id in self._owners:
            return "occupied"
        if self._reservations.get(seat_id):
            return "reserved"
        return "available"

    def owner(self, seat_id):
        self._sync()
        return self._owners.get(seat_id)

    def owner_since(self, seat_id):
        self._sync()
        return self._since.get(seat_id)

    def seat_of(self, student_number):
        self._sync()
        for seat_id, owner in self._owners.items():
            if owner == student_number:
                return seat_id
        return None

    def reservations_for(self, seat_id):
        self._sync()
        return list(self._reservations.get(seat_id, []))

    def has_reservation(self, seat_id, student_number):
        self._sync()
        return any(r["student"] == student_number for r in self._reservations.get(seat_id, []))

    def get_date_reservation_count(self, date_str):
        self._sync()
        return sum(1 for lst in self._reservations.values() for r in lst if r["date"] == date_str)

    def is_date_overbooked(self, date_str):
        return self.get_date_reservation_count(date_str) >= MAX_RESERVATIONS_PER_DAY

    def check_time_overlap(self, seat_id, date_str, new_start, new_end):
        for res in self._reservations.get(seat_id, []):
            if res["date"] == date_str and max(res["start"], new_start) < min(res["end"], new_end):
                return True
        return False

    @staticmethod
    def reservation_minutes(res):
        return int((res["end"] - res["start"]).total_seconds() // 60)

    @classmethod
    def reservation_problem(cls, res):
        """Returns a short warning if the librarian should remove this reservation, else ''."""
        if cls.reservation_minutes(res) > MAX_RESERVATION_MINUTES:
            return f"OVER {MAX_RESERVATION_MINUTES}-MIN LIMIT"
        if datetime.now() > res["end"]:
            return "EXPIRED"
        return ""

    # ---------- student / entrance actions ----------
    def reserve(self, seat_id, student_number, date_str, start_dt, duration_minutes):
        if not 1 <= duration_minutes <= MAX_RESERVATION_MINUTES:
            return False, f"A reservation can only last up to {MAX_RESERVATION_MINUTES} minutes."
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        with self._transaction():
            if self.is_date_overbooked(date_str):
                return False, f"This date is fully booked (maximum {MAX_RESERVATIONS_PER_DAY} reservations per day)."
            if self.check_time_overlap(seat_id, date_str, start_dt, end_dt):
                return False, "The selected time slot overlaps with an existing reservation for this seat."
            self._reservations.setdefault(seat_id, []).append(
                {"student": student_number, "date": date_str, "start": start_dt, "end": end_dt})
            self._save()
        return True, f"Seat {seat_id} reserved for {date_str} ({duration_minutes} min)."

    def occupy(self, seat_id, student_number):
        with self._transaction():
            if seat_id in self._owners:
                return False, "This seat is already occupied."
            current = next((s for s, o in self._owners.items() if o == student_number), None)
            if current:                                   # RULE: one chair per student
                return False, f"Student {student_number} is already logged in at seat {current}. Check out there first."
            reservations = self._reservations.get(seat_id, [])
            if reservations and not any(r["student"] == student_number for r in reservations):
                return False, "This seat is reserved by another student."   # RULE: only the reserver may check in
            self._owners[seat_id] = student_number
            self._since[seat_id] = datetime.now()
            if reservations:                              # RULE: check-in uses up today's reservation
                today = datetime.now().strftime("%Y-%m-%d")
                left = [r for r in reservations if not (r["student"] == student_number and r["date"] == today)]
                if left: self._reservations[seat_id] = left
                else: del self._reservations[seat_id]
            self._save()
        return True, f"Seat {seat_id} occupied by {student_number}."

    def release(self, seat_id, student_number):
        """Check out of a seat. Only the number used to log in can do this."""
        with self._transaction():
            if seat_id not in self._owners:
                return False, "This seat is already available."
            if self._owners[seat_id] != student_number:
                return False, "Only the student number that logged into this seat can check out."
            del self._owners[seat_id]
            self._since.pop(seat_id, None)
            self._save()
        return True, f"Seat {seat_id} is now available."

    def cancel_own_reservations(self, seat_id, student_number):
        with self._transaction():
            before = self._reservations.get(seat_id, [])
            after = [r for r in before if r["student"] != student_number]
            if len(after) == len(before):
                return False, "You have no reservation on this seat."
            self._set_reservations(seat_id, after); self._save()
        return True, "Your reservation(s) on this seat were cancelled."

    # ---------- librarian actions (yellow chairs only) ----------
    def remove_reservation(self, seat_id, index):
        with self._transaction():
            lst = list(self._reservations.get(seat_id, []))
            if not 0 <= index < len(lst):
                return False, "That reservation no longer exists."
            lst.pop(index)
            self._set_reservations(seat_id, lst); self._save()
        return True, "Reservation removed."

    def force_release(self, seat_id):
        """Librarian removes whoever is logged into a red chair (no student number needed)."""
        with self._transaction():
            if seat_id not in self._owners:
                return False, "This seat is already available."
            student = self._owners.pop(seat_id)
            self._since.pop(seat_id, None)
            self._save()
        return True, f"Student {student} was logged out of seat {seat_id}."

    def clear_reservations(self, seat_id):
        with self._transaction():
            if not self._reservations.get(seat_id):
                return False, "There are no reservations on this seat."
            del self._reservations[seat_id]; self._save()
        return True, f"All reservations on seat {seat_id} were removed."

    def _set_reservations(self, seat_id, lst):
        if lst: self._reservations[seat_id] = lst
        else: self._reservations.pop(seat_id, None)
