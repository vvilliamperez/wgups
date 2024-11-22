from enum import Enum
from logging import getLogger

from wgups.package import Package, PackageStatus

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

    def __init__(self, truck_id: int):
        self.truck_id = truck_id
        self.max_capacity = MAX_CAPACITY
        self.speed_in_mph = AVG_SPEED

        self.distance_to_next_location_in_miles = 0
        self.point_a = START_LOCATION
        self.point_b = None

        # Whatever packages are in the truck, are to be delivered In Order.
        self.packages = []
        self.packages_delivered = []

        self.status = TruckStatus.AT_HUB

    @property
    def available_capacity(self):
        return self.max_capacity - len(self.packages)

    def load(self, packages):
        for package in packages:
            if len(self.packages) <= self.available_capacity:
                self.packages.append(package)
                package.status = PackageStatus.ON_TRUCK
                package.truck_id = self.truck_id
            else:
                logger.error(f"Truck {self.id} is at capacity. Cannot load package {package.ID}")
                raise Exception(f"Truck {self.id} is at capacity. Cannot load package {package.ID}")


    def deliver(self):
        pkg = self.packages.pop(0)
        self.packages_delivered.append(pkg)
        self.point_a = pkg.full_address
        pkg.status = PackageStatus.DELIVERED
        logger.info(f"Truck {self.id} delivered package {pkg.ID} at {pkg.full_address}")

        if len(self.packages) > 0:
            self.start_route()
        else:
            """Return to hub"""
            return self.return_to_hub()

    def return_to_hub(self):
        self.distance_to_next_location_in_miles = get_distance_between_locations(self.point_a, START_LOCATION)
        self.status = TruckStatus.RETURNING

    def start_route(self):
        self.distance_to_next_location_in_miles = get_distance_between_locations(self.point_a, self.packages[0].full_address)
        self.packages[0].status = PackageStatus.NEXT_STOP
        for package in self.packages[1:]:
            package.status = PackageStatus.IN_TRANSIT

    # tick rate is in seconds
    def update(self, seconds=1):
        tick_rate_in_hours = seconds / 3600  # convert seconds to hours
        if self.status == TruckStatus.EN_ROUTE:
            self.distance_to_next_location_in_miles -= self.speed_in_mph * tick_rate_in_hours
            if self.distance_to_next_location_in_miles <= 0:
                self.deliver()
        elif self.status == TruckStatus.AT_HUB:
            logger.info(f"Truck {self.id} is at hub, please load packages and start route")
            logger.info(f"Truck {self.id} is loaded with {len(self.packages)} packages")
        elif self.status == TruckStatus.RETURNING:
            self.distance_to_next_location_in_miles -= self.speed_in_mph * tick_rate_in_hours
            if self.distance_to_next_location_in_miles <= 0:
                self.point_a = START_LOCATION
                self.status = TruckStatus.AT_HUB


class TruckStatus(Enum):
    AT_HUB = 1
    EN_ROUTE = 2
    RETURNING = 3
