from enum import Enum
from logging import getLogger

from wgups.core.utils import convert_deadline, convert_seconds_to_hhmmss

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


    def __str__(self):


        return (f"Package ID: {self.package_ID}\n"
                f"Destination: {self.destination}\n"
                f"Deadline: {convert_seconds_to_hhmmss(self.deadline)}\n"
                f"Delivered at: {convert_seconds_to_hhmmss(self.delivered_at_time)}\n"
                f"Weight: {self.weight}\n"
                f"Notes: {self.notes}\n"
                f"Status: {self.status}\n"
                f"Truck ID: {self.truck_id}\n"
                f"Note on Delivery: {self.note_on_delivery}\n")


    # create function for when package status is delivered
    def delivered(self, delivery_time):
        self.status = PackageStatus.DELIVERED
        self.delivered_at_time = delivery_time
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
