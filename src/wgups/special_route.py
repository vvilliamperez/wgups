from logging import getLogger

from wgups.package import Package, PackageStatus

logger = getLogger(__name__)

"""
Special Route

A special route package is a an "empty" package object used for directing the truck to a specific location.
It is not a package that is to be delivered, but rather a placeholder for the truck to go to a specific location.
"""
class SpecialRoute(Package):


    def __init__(self, destination=None, notes=None, reason=None):
        package_ID = 999
        deadline_in_hhmmss = "EOD"
        weight = 0
        super().__init__(package_ID, destination, deadline_in_hhmmss, weight, notes)
        self.reason = reason
        logger.warning(f"Special Route  created for {self.destination}")

    def delivered(self):
        logger.warning(f"Truck {self.truck_id} arrived at special location {self.destination}")
        logger.warning(f"Reason: {self.reason}")
        self.status = PackageStatus.DELIVERED
        return self.status


