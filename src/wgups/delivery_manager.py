from logging import getLogger
from typing import List, Dict

from wgups.delivery_truck import DeliveryTruck, TruckStatus
from wgups.package import PackageStatus, Package

TRUCK_FLEET_SIZE = 3
DRIVER_CREW_SIZE = 2

START_TIME = 32755 # 8:00:00 AM in seconds

SPECIAL_UPDATE_TIME = 37200 # 10:20:00 AM in seconds

logger = getLogger(__name__)

class DeliveryManager:

    def __init__(self, package_data: List[Dict], distance_data: List[Dict]):

        self.package_data = package_data
        self.distance_data = distance_data

        self.packages = []
        self.initialize_packages()




        self.trucks = []
        # Create a fleet of trucks, based on the TRUCK_FLEET_SIZE and DRIVER_CREW_SIZE
        for i in range(min(TRUCK_FLEET_SIZE, DRIVER_CREW_SIZE)):
            self.trucks.append(DeliveryTruck(truck_id=i+1))

        self.time = START_TIME

    @property
    def trucks_at_hub(self):
        return [truck for truck in self.trucks if truck.status == TruckStatus.AT_HUB]

    @property
    def trucks_in_transit(self):
        return [truck for truck in self.trucks if truck.status == TruckStatus.EN_ROUTE]

    @property
    def trucks_returning(self):
        return [truck for truck in self.trucks if truck.status == TruckStatus.RETURNING]

    @property
    def packages_at_hub(self):
        return [package for package in self.packages if package.status == PackageStatus.AT_HUB]

    @property
    def packages_on_trucks(self):
        packages = []
        for truck in self.trucks:
            packages.extend(truck.packages)
        return packages

    @property
    def packages_delivered(self):
        packages = []
        for truck in self.trucks:
            packages.extend(truck.packages_delivered)
        return packages

    def tick(self, seconds=1):
        """
        Update the simulation by a number of seconds

        If any trucks are at the hub, run the route algorithm to assign packages to trucks at the hub.
        Algorithm is dependent on the remaining packages and the available drivers.

        :param seconds:
        :return:
        """
        self.time += seconds

        if self.time == SPECIAL_UPDATE_TIME:
             # Update package 9 - Correct address: 410 S State St., Salt Lake City, UT 84111
            pass

        if any(truck.status == TruckStatus.AT_HUB for truck in self.trucks):
            self.run_route_algorithm(self.trucks_at_hub)

        for truck in self.trucks:
            truck.update(seconds)

        if self.time == 86400:
            raise Exception("Reached midnight! Stopping simulation.")

    def run_route_algorithm(self, trucks_to_assign_routes):
        print(trucks_to_assign_routes)
        pass


    def start(self):
        while True:
            self.tick()

    def pause(self):
        pass

    def initialize_packages(self)-> None:
        # Extract data from each dictionary and convert to a Package object
        for data in self.package_data:
            package = Package(package_ID=data['Package ID'], full_address=data['full_address'], deadline=data['Delivery Deadline'], weight=data['Mass'], notes=data['Special Notes'])
            self.packages.append(package)
            logger.info(f"Added package {package.package_ID}")
        logger.info(f"Added {len(self.packages)} packages")


