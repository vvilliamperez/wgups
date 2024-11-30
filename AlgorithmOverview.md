# Algorithm Overview in Pseudocode

```python
def run_route_algorithm(trucks_to_assign_routes):
    """
    Assign packages to trucks, based on the remaining packages and the available drivers.
    Prioritize deliveries by deadlines and optimize routes using a greedy nearest neighbor approach.
    """

    # Step 1: Sort packages by deadline to prioritize urgent deliveries
    packages.sort(key=lambda package: package.deadline)

    # Step 2: Assign packages to each truck
    for truck in trucks_to_assign_routes:
        packages_at_hub = get_packages_at_hub()
        current_location = truck.starting_location
        manifest = []

        # Step 3: Fill truck with packages using a greedy nearest neighbor algorithm
        while len(manifest) < truck.capacity:
            nearest_package = None
            nearest_distance = float('inf')

            # Find the nearest package that is not already in the manifest
            for package in packages_at_hub:
                if package not in manifest:
                    distance = calculate_distance(current_location, package.destination)
                    if distance < nearest_distance:
                        nearest_package = package
                        nearest_distance = distance

            # Step 4: Add nearest package to the manifest
            if nearest_package:
                manifest.append(nearest_package)
                current_location = nearest_package.destination
            else:
                break

        # Step 5: Load truck with manifest and start the delivery route
        truck.load(manifest)
        truck.start_route()
```

# Programming Environment

This project is implemented using Python 3.13. The code is written with compatibility for Python 3.8 or later. Below are some details about the programming environment and resources used:

- Python Standard Library: The code relies solely on the standard library to ensure portability and ease of use.

- tkinter: A simple GUI is built using tkinter. Note that tkinter is not installed by default in some Python distributions, so users may need to ensure that it is available in their Python environment.

   ### Preprocessed Data: A /res folder contains preprocessed data files used by the algorithm. The following files are included:
    distance_data.csv: Contains the distances between all locations.
    location_lookup.csv: Maps written addresses (as seen on the packages) to actual addresses used in the system.
    package_file.csv: Contains all package data.

These files were preprocessed manually using the provided Excel files before being converted into CSV format.