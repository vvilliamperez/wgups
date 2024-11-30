from copy import copy
from logging import getLogger
from typing import List, Dict

from wgups.data_structures.avl_tree import AVLTree
from wgups.core.constants import TRUCK_FLEET_SIZE, DRIVER_CREW_SIZE, START_TIME, SPECIAL_UPDATE_TIME, FLIGHT_ARRIVAL_TIME, \
    EOD_IN_SECONDS
from wgups.core.delivery_truck import DeliveryTruck, TruckStatus
from wgups.core.package import PackageStatus, Package
from wgups.core.special_route import SpecialRoute
from wgups.core.utils import get_distance
from wgups.data_structures.min_heap import MinHeap

logger = getLogger(__name__)

class DeliveryManager:

    def __init__(self, package_data: List[Dict], distance_data: List[Dict], location_data: List[Dict]):

        self.package_data = package_data
        self.distance_data = distance_data
        self.location_data = location_data

        self.packages = []
        self.trucks = []

        # Create a fleet of trucks, based on the TRUCK_FLEET_SIZE and DRIVER_CREW_SIZE
        for i in range(min(TRUCK_FLEET_SIZE, DRIVER_CREW_SIZE)):
            self.trucks.append(DeliveryTruck(truck_id=i+1, distance_data=self.distance_data))

        self.total_packages = 0
        self.initialize_packages()
        self.default_tick_speed = None

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
    def packages_at_hub_sorted(self):
        packages_unsorted = [package for package in self.packages if package.status == PackageStatus.AT_HUB]
        packages = sorted(packages_unsorted, key=lambda pkg: pkg.deadline)
        return packages

    @property
    def packages_unavailable(self):
        return [package for package in self.packages if package.status == PackageStatus.UNAVAILABLE]

    @property
    def packages_on_trucks(self):
        packages = []
        for truck in self.trucks:
            packages.extend(truck.packages_on_truck)
        return packages

    @property
    def packages_delivered(self):
        packages = []
        for truck in self.trucks:
            packages.extend(truck.packages_delivered)
        return packages


    def lookup_packages(self, id=None, destination=None, weight=None, status=None):
        """
        Lookup function for packages
        :param id:
        :param destination:
        :param weight:
        :param status:
        :return:
        """
        results = []
        for package in self.packages:
            if id is not None and package.package_ID == int(id):
                results.append(package)
            if destination is not None and package.destination == str(destination):
                results.append(package)
            if weight is not None and package.weight == float(weight):
                results.append(package)
            if status is not None and package.status == PackageStatus[str(status).upper()]:
                results.append(package)
        return results

    def get_status_for_package_id(self, package_id):
        """
        Get the status of a package by its ID
        Lookup function
        :param package_id:
        :return:
        """
        for package in self.packages:
            if package.package_ID == package_id:
                return package
        logger.warning(f"Package {package_id} not found")
        return None

    def all_packages_delivered(self):
        return [package for package in self.packages if package.status != PackageStatus.DELIVERED] == []

    def tick(self, seconds=1):
        """
        Update the simulation by a number of seconds

        If any trucks are at the hub, run the route algorithm to assign packages to trucks at the hub.
        Algorithm is dependent on the remaining packages and the available drivers.

        :param seconds:
        :return:
        """
        if self.default_tick_speed is not None:
            seconds = self.default_tick_speed
        self.time += seconds

        if self.time == SPECIAL_UPDATE_TIME:
             # Update package 9 with revised address
            revised_address = "410 S State St, Salt Lake City, UT 84111"
            logger.info("\n\n")
            logger.warning(f"Special update!! Updating package 9 with revised address: {revised_address}")

            package_9 = [package for package in self.packages if package.package_ID == "9"][0]

            match package_9.status:
                # if package 9 is delivered, go get it and redeliver
                case PackageStatus.DELIVERED:
                    # find truck nearest to package 9
                    logger.warning("\n\nPackage 9 has already been delivered. Will need to pick up and redeliver.")
                    logger.info("Finding nearest truck to package 9")

                    nearest_truck = None
                    nearest_distance = float('inf')
                    for truck in self.trucks:
                        distance = get_distance(self.distance_data, truck.point_b, package_9.destination)
                        if distance < nearest_distance:
                            nearest_truck = truck
                            nearest_distance = distance
                    # add special route to nearest truck
                    # finishes current delivery, heads to and picks up package 9,
                    route_to_package_9 = SpecialRoute(package_9.destination, reason="Pick up package 9")
                    route_to_package_9.truck_id = nearest_truck.truck_id
                    nearest_truck.packages_on_truck.insert(1,route_to_package_9)
                    # delivers package 9, continues route
                    package_9_copy = copy(package_9)
                    package_9_copy.destination = self.lookup_location(revised_address)
                    package_9_copy.note_on_delivery = "Delivered after correction!"
                    nearest_truck.packages_on_truck.insert(2, package_9_copy)
                    logger.info(f"Truck {nearest_truck.truck_id} is making a special pickup and delivery for package 9")
                # if package 9 is on truck, update the destination
                case PackageStatus.ON_TRUCK:
                    logger.info(f"Package 9 is on truck {package_9.truck_id}.")
                    logger.warning("Revising routing, but may cause delay")
                    package_9.destination = self.lookup_location(revised_address)
                    logger.info(f"Package 9 destination updated to {revised_address}")
                case PackageStatus.AT_HUB:
                    logger.info(f"Package 9 is at hub. Updating destination.")
                    package_9.destination = self.lookup_location(revised_address)
                    logger.info(f"Package 9 destination updated to {revised_address}")
                case PackageStatus.IN_TRANSIT:
                    logger.info(f"Package 9 is in transit on truck {package_9.truck_id}.")
                    logger.info("Revising routing, but may cause delay.")
                    package_9.destination = self.lookup_location(revised_address)
                    logger.info(f"Package 9 destination updated to {revised_address}")
                case PackageStatus.NEXT_STOP:
                    logger.info(f"Package 9 is next stop")
                    package_9.note_on_delivery = "Went to wrong address! Did not deliver."
                    # Continue to "deliver" package 9, but add a duplicate to the manifest
                    # so that the truck will deliver the revised package 9
                    package_9_copy = Package(package_9.package_ID, package_9.destination, package_9.deadline_in_hhmmss, package_9.weight, package_9.notes)
                    package_9_copy.destination = self.lookup_location(revised_address)
                    package_9_copy.note_on_delivery = "Delivered after correction!"
                    self.trucks[package_9.truck_id - 1].load([package_9_copy])
                case PackageStatus.UNAVAILABLE:
                    logger.info(f"Package 9 is unavailable.")
                    logger.info("Revising route..")
                    package_9.destination = self.lookup_location(revised_address)
            logger.info(f"Package 9 updated... resuming route! \n\n")


        if self.time == FLIGHT_ARRIVAL_TIME:
            logger.info("\n\n")
            logger.info("Flight has arrived")
            # Flight has arrived, mark packages available
            for package in self.packages_unavailable:
                package.status = PackageStatus.AT_HUB
                logger.info(f"Package {package.package_ID} is now available")
            logger.info("All packages are now available\n\n")


        if any(truck.status == TruckStatus.AT_HUB for truck in self.trucks):
            self.run_route_algorithm(self.trucks_at_hub)

        for truck in self.trucks:
            truck.update(self.time, seconds=seconds)

        if self.time == EOD_IN_SECONDS:
            raise Exception("Reached midnight! Stopping simulation.")

    def lookup_location(self, search_text)-> str:
        for row in self.location_data:
            if search_text in row['PackageText']:
                return row['Location']
        raise(Exception(f"Location {search_text} not found"))

    def run_route_algorithm(self, trucks_to_assign_routes):
        """
        Assign packages to trucks, based on the remaining packages and the available drivers
        Based on all available information, assigns packages to be delivered in order to trucks

        :param trucks_to_assign_routes:
        :return:
        """
        # print(trucks_to_assign_routes)
        # Assign packages to trucks, based on the remaining packages and the available drivers
        # Based on all available information, assigns packages to be delivered in order to trucks

        # Sort packages by deadline to prioritize urgent deliveries,
        #
        #
        # this uses the avl tree
        #packages_avl = AVLTree()
        #for package in self.packages_at_hub:
        #    packages_avl.insert_package(package)
        #sorted_packages = packages_avl.in_order_traversal()

        # this uses the min heap
        packages_heap = MinHeap()
        for package in self.packages_at_hub:
            packages_heap.push(package)
        sorted_packages = []
        while pack := packages_heap.pop():
            sorted_packages.append(pack)


        # Assign packages to trucks using a greedy nearest neighbor algorithm
        # The distance is calculated using the distance data

        for truck in trucks_to_assign_routes:
            current_location = truck.point_a
            manifest = []

            while len(manifest) < truck.available_capacity:
                # Find the nearest package
                nearest_package = None
                nearest_distance = float('inf')

                for package in sorted_packages:
                    if package not in manifest:
                        distance = get_distance(self.distance_data, current_location, package.destination)
                        if distance < nearest_distance:
                            nearest_package = package
                            nearest_distance = distance
                if nearest_package is not None:
                    manifest.append(nearest_package)
                    # Update the current location
                    current_location = nearest_package.destination
                else:
                    break
            truck.load(manifest)
            truck.start_route()

        #print(self.packages)



    def start(self):
        while True:
            if self.all_packages_delivered():
                break
            self.tick()

        # convert time to hh:mm:ss
        hours = self.time // 3600
        minutes = (self.time % 3600) // 60
        seconds = self.time % 60
        logger.info(f"Simulation complete. Time: {hours}:{minutes}:{seconds}")
        logger.info(f"All {len(self.packages_delivered)} routes ran. ({len(self.packages_delivered)-self.total_packages} extra routes made for special deliveries)")

    def pause(self):
        pass

    def initialize_packages(self)-> None:
        # Extract data from each dictionary and convert to a Package object
        for data in self.package_data:

            destination = self.lookup_location(data['full_address'])
            package = Package(package_ID=data['Package ID'], destination=destination, deadline_in_hhmmss=data['Delivery Deadline'], weight=data['Mass'], notes=data['Special Notes'])
            self.packages.append(package)

            #logger.info(f"Added package {package.package_ID}")

        logger.info(f"Added {len(self.packages)} packages to global system\n\n")
        self.total_packages = len(self.packages)
        logger.info("Handling special delivery notes:")

        # Handle special notes
        packages_with_notes = [package for package in self.packages if package.notes != '']
        for package in packages_with_notes:
            match package.notes:
                case 'Can only be on truck 2':
                    self.trucks[1].load([package])
                    logger.info(f"Loaded package {package.package_ID} onto Truck 2")
                case 'Delayed on flight---will not arrive to depot until 9:05 am':
                    package.status = PackageStatus.UNAVAILABLE
                    logger.info(f"Package {package.package_ID} is delayed on a flight and unavailable until 9:05 am")
                    # Check later if package is available
        logger.info("All finished with special notes.\n\n")


