from enum import Enum
from logging import getLogger
from typing import List, Dict

from wgups.package import Package, PackageStatus
from wgups.utils import get_distance

MAX_CAPACITY = 16  # packages
AVG_SPEED = 18  # MPH
START_LOCATION = "Western Governors University 4001 South 700 East, Salt Lake City, UT 84107"

logger = getLogger(__name__)


class DeliveryTruck:

    """"

    A delivery truck that can carry packages and deliver them to their destination.
    Truck will receive a manifest of packages and deliver them in order.
    Truck will return to hub after all packages are delivered.

    Routing algorithm is done by the DeliveryManager, which creates the manifest for each truck.
    """

    def __init__(self, truck_id: int, distance_data: List[Dict]):
        self.truck_id = truck_id
        self.distance_data = distance_data
        self.max_capacity = MAX_CAPACITY
        self.speed_in_mph = AVG_SPEED

        self.distance_to_next_location_in_miles = 0.0
        self.point_a = START_LOCATION
        self.point_b = None

        # Whatever packages are in the truck, are to be delivered In Order.
        self.packages_on_truck = []
        self.packages_delivered = []

        self.status = TruckStatus.AT_HUB

    @property
    def available_capacity(self):
        return self.max_capacity - len(self.packages_on_truck)

    def load(self, packages):
        for package in packages:
            if self.available_capacity > 0 :
                self.packages_on_truck.append(package)
                package.status = PackageStatus.ON_TRUCK
                package.truck_id = self.truck_id
            else:
                logger.error(f"Truck {self.truck_id} is at capacity. Cannot load package {package.package_ID}")
                raise Exception(f"Truck {self.truck_id} is at capacity. Cannot load package {package.package_ID}")


    def deliver(self):
        pkg = self.packages_on_truck.pop(0)
        self.packages_delivered.append(pkg)

        pkg.status = PackageStatus.DELIVERED
        logger.info(f"Truck {self.truck_id} delivered package {pkg.package_ID} at {pkg.destination}")

        self.point_a = pkg.destination
        self.point_b = None
        if len(self.packages_on_truck) > 0:
            """Continue route"""
            self.start_route()
        else:
            """Return to hub"""
            return self.return_to_hub()

    def dock(self):
        self.point_a = START_LOCATION
        self.point_b = None
        self.status = TruckStatus.AT_HUB


    def return_to_hub(self):
        logger.info(f"Truck {self.truck_id} is returning to hub")
        self.point_b = START_LOCATION
        self.distance_to_next_location_in_miles = get_distance(self.distance_data, self.point_a, self.point_b)
        self.status = TruckStatus.RETURNING


    def start_route(self):

        if self.packages_on_truck is None or len(self.packages_on_truck) == 0:
            logger.warning(f"Truck {self.truck_id} has no packages to deliver")
        logger.info(f"Truck {self.truck_id} is starting route to {self.packages_on_truck[0].destination}")
        self.status = TruckStatus.EN_ROUTE
        self.point_b = self.packages_on_truck[0].destination
        self.distance_to_next_location_in_miles = get_distance(self.distance_data, self.point_a, self.point_b)
        self.packages_on_truck[0].status = PackageStatus.NEXT_STOP
        for package in self.packages_on_truck[1:]:
            package.status = PackageStatus.IN_TRANSIT

    # tick rate is in seconds
    def update(self, seconds=1):
        tick_rate_in_hours = seconds / 3600  # convert seconds to hours
        if self.status == TruckStatus.EN_ROUTE:
            self.distance_to_next_location_in_miles -= float(float(self.speed_in_mph) * tick_rate_in_hours)
            if self.distance_to_next_location_in_miles <= 0.0:
                self.deliver()
        elif self.status == TruckStatus.AT_HUB:
            #logger.info(f"Truck {self.truck_id} is at hub, please load packages and start route")
            #logger.info(f"Truck {self.truck_id} is loaded with {len(self.packages_on_truck)} packages")
            return
        elif self.status == TruckStatus.RETURNING:
            self.distance_to_next_location_in_miles -= float(float(self.speed_in_mph) * tick_rate_in_hours)
            if self.distance_to_next_location_in_miles <= 0.0:
                self.dock()


class TruckStatus(Enum):
    AT_HUB = 1
    EN_ROUTE = 2
    RETURNING = 3
