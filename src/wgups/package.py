from enum import Enum


def convert_deadline(deadline_in_hhmmss):
    """
    Convert the deadline to seconds
    """
    if deadline_in_hhmmss == 'EOD':
        return 86400

    deadline = deadline_in_hhmmss.split(':')
    return int(deadline[0]) * 3600 + int(deadline[1]) * 60 + int(deadline[2])


class Package:

    def __init__(self, package_ID, destination, deadline_in_hhmmss, weight, notes):

        self.package_ID = package_ID
        self.destination = destination
        self.deadline = convert_deadline(deadline_in_hhmmss)
        self.weight = weight
        self.notes = notes

        """Packages start at hub"""
        self.status = PackageStatus.AT_HUB

        # ID 0 means it's not loaded
        self.truck_id = 0


class PackageStatus(Enum):
    AT_HUB = 1
    ON_TRUCK = 2
    IN_TRANSIT = 3
    NEXT_STOP = 4
    DELIVERED = 5
