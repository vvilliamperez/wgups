class AVLNode:
    def __init__(self, package):
        self.package = package  # Store the Package object
        self.left = None
        self.right = None
        self.height = 1  # Height of the node


class AVLTree:
    def __init__(self):
        self.root = None

    # Utility to get the height of a node
    def get_height(self, node):
        return node.height if node else 0

    # Utility to calculate the balance factor of a node
    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    # Right rotate subtree rooted with node y
    def right_rotate(self, y):
        if not y or not y.left:
            return y  # Return the node itself if rotation is not possible

        x = y.left
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))

        return x

    # Left rotate subtree rooted with node x
    def left_rotate(self, x):
        if not x or not x.right:
            return x  # Return the node itself if rotation is not possible

        y = x.right
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    # Insert a package into the AVL tree
    def insert(self, node, package):
        """Recursive helper function for insertion."""
        if not node:
            return AVLNode(package)

        # Use deadlinefor ordering
        if package.deadline > node.package.deadline:
            node.left = self.insert(node.left, package)
        elif package.deadline < node.package.deadline:
            node.right = self.insert(node.right, package)
        else:
            # Same deadline, check for duplicate ID (enforce unique packages)
            if package.package_ID == node.package.package_ID:
                raise ValueError(f"Duplicate package ID {package.package_ID} is not allowed.")
            else:
                # Insert packages with the same deadline into the right subtree
                node.right = self.insert(node.right, package)

        # Update the height of the ancestor node
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

        # Balance the node
        balance = self.get_balance(node)

        # Left Left Case
        if balance > 1 and package.deadline > node.left.package.deadline:
            return self.right_rotate(node)

        # Right Right Case
        if balance < -1 and package.deadline < node.right.package.deadline:
            return self.left_rotate(node)

        # Left Right Case
        if balance > 1 and package.deadline > node.left.package.deadline:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)

        # Right Left Case
        if balance < -1 and package.deadline < node.right.package.deadline:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)

        return node

    # Public method to insert a package
    def insert_package(self, package):
        """Inserts a package into the AVL tree."""
        self.root = self.insert(self.root, package)

    # In-order traversal to get sorted list of packages by deadlines
    def in_order_traversal(self, node="Initial", result=None):
        """Traverse the AVL tree in order and return sorted packages."""
        if result is None:
            result = []
        if node is "Initial":
            node = self.root
        if node is None:
            return result


        if node is not None:
            # Traverse the left subtree
            self.in_order_traversal(node.left, result)
            # Visit the current node
            result.append(node.package)
            # Traverse the right subtree
            self.in_order_traversal(node.right, result)

        return result

