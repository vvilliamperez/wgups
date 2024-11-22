from enum import Enum


class Package:

    def __init__(self, package_ID, full_address, deadline, weight, notes):

        self.package_ID = package_ID
        self.full_address = full_address
        self.deadline = deadline
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
