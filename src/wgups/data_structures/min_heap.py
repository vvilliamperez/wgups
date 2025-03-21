class MinHeap:
    def __init__(self):
        self.data = []  # List to store heap elements

    def push(self, package):
        """Adds a package to the heap and maintains heap property."""
        self.data.append(package)  # Add the package at the end
        self._heapify_up(len(self.data) - 1)  # Restore heap property

    def pop(self):
        """Removes and returns the package with the earliest deadline."""
        if not self.data:
            return False
        # Swap the root with the last element
        self._swap(0, len(self.data) - 1)
        # Remove the last element (smallest item)
        min_package = self.data.pop()
        # Restore heap property
        self._heapify_down(0)
        return min_package

    def _heapify_up(self, index):
        """Restore the heap property by moving the element at index up."""
        parent = (index - 1) // 2
        if index > 0 and self.data[index].deadline < self.data[parent].deadline:
            self._swap(index, parent)
            self._heapify_up(parent)

    def _heapify_down(self, index):
        """Restore the heap property by moving the element at index down."""
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2

        # Check if left child exists and is smaller
        if left < len(self.data) and self.data[left].deadline < self.data[smallest].deadline:
            smallest = left

        # Check if right child exists and is smaller
        if right < len(self.data) and self.data[right].deadline < self.data[smallest].deadline:
            smallest = right

        # If the smallest isn't the current index, swap and continue
        if smallest != index:
            self._swap(index, smallest)
            self._heapify_down(smallest)

    def _swap(self, i, j):
        """Helper function to swap two elements in the heap."""
        self.data[i], self.data[j] = self.data[j], self.data[i]

    def __len__(self):
        """Returns the number of elements in the heap."""
        return len(self.data)
