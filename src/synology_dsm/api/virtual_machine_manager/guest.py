"""DSM Storage data."""
from synology_dsm.helpers import SynoFormatHelper


class SynoVirtualMachineManager:
    """Class containing Storage data."""

    API_KEY = "SYNO.Virtualization.API.Guest"
    ACTION_API_KEY = "SYNO.Virtualization.API.Guest.Action"

    def __init__(self, dsm):
        """Constructor method."""
        self._dsm = dsm
        self._data = {}

    def update(self):
        """Updates storage data."""
        raw_data = self._dsm.get(self.API_KEY, "list")
        if raw_data:
            self._data = raw_data["data"]
          #  print(raw_data)

    # Root
    @property
    def guests(self):
        """Gets all Virtual Machines."""
        return self._data.get("guests", [])

    @property
    def guest_ids(self):
        """Gets a Virtual Machines name."""
        guests = []
        for guest in self.guests:
            guests.append(guest["guest_id"])
        return guests

    def get_guest(self, guest_id):
        """Returns a specific guest."""
        for guest in self.guests:
            if guest["guest_id"] == guest_id:
                return guest
        return {}

    def guest_name(self, guest_id):
        """Return the name of this guest."""
        return self.get_guest(guest_id).get("guest_name")

    def guest_status(self, guest_id):
        """Gets storage env."""
        return self.get_guest(guest_id).get("status")

    def guest_network_name(self, guest_id):
        """Gets storage env."""
        return self.get_guest(guest_id).get("network_name")

    def poweron(self, guest_id, guest_name):
        res = self._dsm.post(
            self.ACTION_API_KEY,
            "poweron",
            {
                "guest_id": guest_id,
                "guest_name": guest_name,
            },
        )
        self.update()

    def shutdown(self, guest_id, guest_name):
        res = self._dsm.post(
            self.ACTION_API_KEY,
            "shutdown",
            {
                "guest_id": guest_id,
                "guest_name": guest_name,
            },
        )
        self.update()
    
    def poweroff(self, guest_id, guest_name):
        res = self._dsm.post(
            self.ACTION_API_KEY,
            "poweroff",
            {
                "guest_id": guest_id,
                "guest_name": guest_name,
            },
        )
        self.update()
        return res
