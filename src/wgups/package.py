from enum import Enum
from logging import getLogger

from wgups.utils import convert_deadline

logger = getLogger(__name__)


class Package:

    def __init__(self, package_ID, destination, deadline_in_hhmmss, weight, notes):

        self.package_ID = package_ID
        self.destination = destination
        self.deadline = convert_deadline(deadline_in_hhmmss)
        self.weight = weight
        self.notes = notes

        self.delivered_at_time = None

        """Packages start at hub"""
        self.status = PackageStatus.AT_HUB

        # ID 0 means it's not loaded
        self.truck_id = 0

        self.note_on_delivery = None

    # create function for when package status is delivered
    def delivered(self):
        self.status = PackageStatus.DELIVERED
        logger.info(f"Truck {self.truck_id} delivered package {self.package_ID} at {self.destination}")
        if self.note_on_delivery:
            logger.warning(f"Package {self.package_ID} delivered with note: {self.note_on_delivery}")
        return self.status

    # create function for when package status is in transit
    def in_transit(self):
        self.status = PackageStatus.IN_TRANSIT
        return self.status

    # create function for when package status is on truck
    def on_truck(self):
        self.status = PackageStatus.ON_TRUCK
        return self.status

    # create function for when package status is at hub
    def at_hub(self):
        self.status = PackageStatus.AT_HUB
        return self.status

    # create function for when package status is next stop
    def next_stop(self):
        self.status = PackageStatus.NEXT_STOP
        return self.status

    # create function for when package status is unavailable
    def unavailable(self):
        self.status = PackageStatus.UNAVAILABLE
        return self.status




class PackageStatus(Enum):
    AT_HUB = 1
    ON_TRUCK = 2
    IN_TRANSIT = 3
    NEXT_STOP = 4
    DELIVERED = 5
    UNAVAILABLE = 6
