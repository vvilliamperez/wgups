# WGUPS Route Optimization Project


# Part A - Self Adjusting Algorithm

I'm using a greedy nearest neighbor algorithm with a priority score to assign packages to trucks. 
It starts with a sorted list of the packages available at the hub using a min-heap.
Then the algorithm assigns packages to trucks based on the priority score,
which is calculated based on the deadline and distance to the next package.

The algorithm repeats this for each package, and each truck, 
until all the trucks are full or there are no more packages left to assign.

This algorithm runs anytime there is a truck at the hub, and packages available to be delivered.

# Part B - Program Overview

## 1. Algorithm Overview in Pseudocode

BEGIN run_route_algorithm
    // Step 1: Sort packages by deadline using min heap
    CREATE min_heap
    COLLECT packages from hub
    
    // Add packages to min heap
    BEGIN package sorting
        GET next package
        ASSIGN package to min_heap using deadline
        CONTINUE until no more packages
    END package sorting
    
    CREATE sorted_packages list
    BEGIN heap extraction
        GET package from min_heap
        ASSIGN package to sorted_packages
        CONTINUE until min_heap empty
    END heap extraction

    // Step 2: Assign packages to each available truck
    COLLECT trucks at hub
    BEGIN truck assignment
        GET next truck
        ASSIGN starting point to current_location
        CREATE manifest list
        
        BEGIN package assignment
            CHECK manifest size < truck capacity
            CHECK sorted_packages not empty
            
            ASSIGN infinity to best_score
            
            BEGIN find best package
                GET next package from sorted_packages
                CHECK package not in manifest
                    COLLECT deadline information
                    COLLECT distance information
                    COLLECT priority score
                    
                    CHECK priority score < best_score
                        UPDATE best_score
                        UPDATE best_package
                    END CHECK
                END CHECK
            END find best package
            
            CHECK best_package exists
                ASSIGN best_package to manifest
                UPDATE sorted_packages
                UPDATE current_location
            END CHECK
            
            CONTINUE until manifest full or no packages
        END package assignment
        
        ASSIGN manifest to truck
        INITIATE truck route
        
        CONTINUE until all trucks checked
    END truck assignment
END run_route_algorithm

## 2. Programming Environment

This project is implemented using Python 3.13. The code is written with compatibility for Python 3.8 or later. Below are some details about the programming environment and resources used:

- Python Standard Library: The code relies solely on the standard library to ensure portability and ease of use.

- tkinter: A simple GUI is built using tkinter. Note that tkinter is not installed by default in some Python distributions, so users may need to ensure that it is available in their Python environment.

The IDE used was PyCharm 2024.2.4 (Professional Edition)
Build #PY-242.23726.102, built on October 22, 2024
Licensed to William Perez
Subscription is active until May 4, 2025.
For educational use only.



### Preprocessed Data
A `/res` folder contains preprocessed data files used by the algorithm. The following files are included:
- distance_data.csv: Contains the distances between all locations.
- location_lookup.csv: Maps written addresses (as seen on the packages) to actual addresses used in the system.
- package_file.csv: Contains all package data.

These files were preprocessed manually using the provided Excel files before being converted into CSV format.

## 3. Time Space Complexity Analysis
For the purposes of algorithm analysis, I have separated these variables as they are distinct and not directly related to each other:
- $n$: Number of packages to be delivered.
- $t$: Number of trucks at the hub.
- $k$: Number of times the route algorithm is called.

### Big O Notation Analysis

- Route Algorithm `run_route_algorithm()::delivery_manager.py` (Greedy Nearest Neighbor with Priority Score Approach):
  - Time Complexity: $O(t * n^2)$ where n is the number of packages to be delivered and t is the number of trucks at the hub. 
    - Treating all data as constant, the time complexity is $O(n^2)$.
This complexity arises from the greedy nearest neighbor approach used to optimize the routes. 
The algorithm iterates over each truck and calculates each package's priority score based on the deadline and distance to the next package.
    - Even though the sorting step shown below is $O(n * log(n))$, the dominant time complexity is the route assignment step.
  - Space Complexity: $O(n)$ due to the linear storage of the data for the priority score calculation for each package. 
- Sorting Step `MinHeap::min_heap.py` (Min-Heap Sort):
  - Time Complexity: $O(n *log(n))$ due to the use of a min-heap to sort the packages by deadline (not distance).
    - Building the min-heap: $O(n)$
    - Extracting the minimum element: $O(log(n))$
    - Total time complexity: $O(n * log(n))$
  - Space Complexity: $O(n)$ due to the storage of the sorted packages and the manifest for each truck.
- Preprocessing Step:
  - Time Complexity: $O(n)$ due to the processing of the package data and distance data of fixed size n.
  - Space Complexity: $O(n)$ due to the storage of the package data and distance data of fixed size n.
- Overall Complexity:
  - Time Complexity: $O(k * t * n^2)$ due to the dominant time complexity of the route algorithm, where k is the number of times the route algorithm is called.
    - Treating all data as constant, the time complexity is $O(n^2)$. 
  - Space Complexity: $O(k*t*n)$ due to the storage of the sorted packages and the manifest for each truck.
    - Treating all data as constant, the space complexity is $O(n)$.

## 4. Scalability and Adaptability 

The algorithm is designed to be scalable and adaptable to handle a large number of packages and trucks.
- Scalability:
  - The algorithm can handle a large number of packages and trucks efficiently due to its time complexity of O(n^2) for the route assignment step.
  - The use of a greedy nearest neighbor approach allows for optimization of routes even with a large number of packages.
- Adaptability:
  - The algorithm can adapt to changes in the number of packages, trucks, and delivery locations.
  - The route algorithm is ran each time there is a truck at the hub, and uses the most up to date information to assign packages to trucks.
  - In addition to the routing algorithm, the system updates the packages across the network if the address was changed or the package was delayed.
    - If the package is on a truck or at the hub and the address was changed, the system will update the truck's manifest and reroute the truck to the new address.
    - If the package was delivered incorrectly, we send a special route to pick up the package and deliver it to the correct address.

## 5. Efficiency and Maintainability

The program is written using object orientated principles to ensure modularity and maintainability. 

The main program logic is in `main.py`.
- The program is able to be called with the `--cli` command line argument to run the full simulation with no GUI.
- Default behaviour will set up the Tkinter GUI and allow the user to interact with the program. TKinter should be installed with most standard Python distributions.

Small helper functions are in `utils.py`

Constants are stored in `constants.py`

The core object classes live in `/core` and consist of:
- `DeliveryManager`: Manages the delivery process and assigns packages to trucks.
- `DeliverTruck`: Represents a delivery truck with a capacity, current location, manifest, and speed and status.
- `Package`: Represents a package with a destination, deadline, and status.
- `SpecialRoute`: Represents a route that is not a package. Used for rerouting trucks to pick up or deliver incorrectly delivered packages. 
This inherites from `Package` and has a special delivery note.

Data structures are stores in `/data_structures`
- `MinHeap`: A min-heap data structure used to sort packages by deadline.
- `AVLTree (UNUSED)`: An AVL tree data structure used to store the package data for quick lookup by package ID. (Unused)

The data structures can easily be swapped in and out for the main route claogirhm in `DeliveryManager.py` 
to test different data structures for performance.


## 6.  Strengths and weaknesses of the MinHeap data structure

### Strengths
- The MinHeap data structure is efficient for maintaining a sorted order of elements, allowing for quick access to the minimum element.
- Space-efficient: The MinHeap data structure uses an array-based representation, which is space-efficient compared to other data structures like AVL trees.
- Easy to implement: I implemented the MinHeap data structure using a list in Python, and other standard library functions, making it easy to understand and maintain.
### Weaknesses
- My implementation of the MinHeap only sorts by package deadline. It would be more efficient to sort by deadline and distance to the next package.
- Packages might have the same deadline, so the MinHeap does not guarantee a perfect ordering of packages.

# Part D - Self Adjusting Data Structure

I'm using a min-heap data structure to sort the packages by deadline.
This is implemented in the `MinHeap` class in `min_heap.py` using a list and helper functions to maintain the heap property.

The relationships between data points in the min-heap are as follows:

1. Temporal Relationships:
   - Packages are primarily ordered by their delivery deadlines
   - Early morning deadlines (e.g., 9:00 AM) take precedence over later deadlines (e.g., EOD)
   - Packages with the same deadline maintain their relative order based on insertion
   - Delayed packages (e.g., those arriving at 9:05 AM) are not included until they become available

2. Dependency Relationships:
   - Some packages must be delivered together (e.g., packages 13, 15, and 19)
   - Certain packages can only be assigned to specific trucks (e.g., "Can only be on truck 2")
   - Address updates (like package 9) affect the delivery sequence but not the heap structure
   - Package status (AT_HUB, IN_TRANSIT, DELIVERED) determines whether a package remains in the heap

3. Priority Relationships:
   - Deadline is the primary sorting factor in the heap
   - When the route algorithm runs, it combines this deadline priority with:
     - Distance to the delivery location
     - Current truck location
     - Special delivery requirements
   - This creates a dynamic priority system where the heap's order influences but doesn't solely determine delivery order

The self-adjusting nature of the min-heap helps maintain these relationships by:
- Automatically promoting urgent packages to the root
- Allowing efficient removal of the highest priority package when trucks are loaded
- Supporting dynamic updates when package statuses change (e.g., when delayed packages arrive)

This structure ensures that when the delivery manager needs to assign packages to trucks, it can efficiently access packages in deadline order while maintaining all dependency and special delivery requirements.

# Part E - Hash Table for Packages

I've implemented a hash table in `delivery_manager.py` as a dictionary for the packages. 
I'm using the package ID as the key, and the package object as the value. 
The package object contains all the extra data including:
- package ID number
- delivery address
- delivery deadline
- delivery city
- delivery zip code
- package weight
- delivery status 

# Part F - Lookup Function

I've implemented a lookup function `lookup_package_data_for_package_id()` in `delivery_manager.py` that takes a package ID as the input and returns the package object that matches. 
If the package ID is not found, the function raises an exception. This should not occur in normal opperation.


# Part G - Screenshots of the system at work
It is difficult to show the system at work in a single screenshot, 
but I have included logs that contain the output of the package statuses at the reuqested times.
There simulation completes at 10:57pm, so I have included logs for 9:00am, 10:00am, and 10:57pm. 
This last log would be the same as 12pm.

To accomplish the same log, a user can run the program, and use the `Tick Number of Seconds` button
to advance the simulation to the desired time. To get to 9:00am, input `3600` seconds. Then press `Check All Packages Status`.
To get to 10:00am, input another `3600` seconds. Then press `Check All Packages Status`.
To get to 10:57pm, input another `3600` seconds. Then press `Check All Packages Status`.
The simulation completes all deliveries by 10:57am.

- [9:00am](/0900log.txt)
- [10:00am](/1000log.txt)
- [10:57am](/1057log.txt)

# Part H - Screenshot of Successful Completion and Total Miles

Completion Screenshot:
![Completion Screenshot](/CompletionScreenshot.png)

# Part I - Justification of the algorithm

The greedy nearest neighbor algorithm with priority score approach is a good choice for this problem due to the following reasons:
- **Efficiency**: The algorithm has a time complexity of O(n^2) for the route assignment step, which is sufficient for handling a large number of packages and trucks.
- **Adaptability**: The algorithm can adapt to changes in the number of packages, trucks, and delivery locations.
- **Priority Score**: The priority score calculation based on the deadline and distance allows for optimization of routes based on urgency and distance. This allows for tweaking the weight of the deadline and distance to optimize the routes.

Two other algorithms that could be considered are:
- **Greedy Algorithm**: A simple greedy algorithm that assigns packages to trucks based on the closest package at each step.
  - This algorithm may not consider the urgency of the delivery. It may also not self adjust well as new information is available. 
- **Nearest Neighbor Algorithm**: A nearest neighbor algorithm that assigns packages to trucks based on the closest package. 
  - Similar to the greedy algorithm, this may not consider the urgency of the delivery. It may also not self adjust well as new information is available.


# Part J - Reflection

If I were to do this project again, I would adjust the algorithm to consider the current location of all trucks when assigning packages.
Currently, the algorithm only runs when one or more trucks are at the hub, and assigns packages based on that information. (Trucks and packages at hub).
In a more optimal system, the algorithm could run at each step of the way taking into account the location of all trucks. 
This could allow for:
- **truck to truck transfers**
- **considering trucks that may be incoming to the hub**
- **rerouting trucks to return packages to the hub for another truck to pick up**
- **returning to the hub to pick up new packages that have arrived**

# Part K - Data Structure Justification

The min-heap data structure is a good choice for sorting packages by deadline due to the following reasons:
- **Efficiency**: The min-heap has a time complexity of $O(n * log(n))$ for sorting the packages by deadline, which is sufficient for a large number of packages.
- **Space Efficiency**: The min-heap uses an array-based representation, which is essentially a list.