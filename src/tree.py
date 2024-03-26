from logs import log
from src.entity import BaseEntity

from datetime import datetime


class Node:
    """
    Class for the nodes in the KD Tree.
    Each node has the value of itself, its depth in the tree,
    and the two children
    """
    def __init__(self, data: BaseEntity, depth: int, left_node, right_node):
        self.data = data
        self.left_child = left_node
        self.right_child = right_node
        self.depth = depth

    def __repr__(self):
        """
        Returns a string representation of the node for debugging

        :return:
        """
        try:
            left_data = self.left_child.data
        except AttributeError:
            left_data = None

        try:
            right_data = self.right_child.data
        except AttributeError:
            right_data = None

        return f"DEPTH {self.depth}   Left: {left_data} Data: {self.data} Right: {right_data}"


class KDTree:
    def __init__(self, points: list, depth: int = 0):
        # The list of all points in the KD Tree. Used for presence checking
        self.points = []
        # The list of all nodes in the KD Tree. Used for range searches
        self.nodes = []
        self.queue = []
        start = datetime.now()
        self.__create_tree(points, depth)
        log(f"Tree of size {len(self.nodes)} created in {datetime.now() - start}")

    def __create_tree(self, entities: list[BaseEntity], depth: int = 0):
        """
        Recursive method to create the KD Tree

        :param entities:
        :param depth:
        :return:
        """
        # Get the current axis. 0 is x and 1 is y
        axis = depth % 2
        if len(entities) != 0:
            entities.sort(key=lambda i: (i.x if axis == 0 else i.y))
            middle_value = len(entities) // 2
            median = entities[middle_value]

            # Generate the left and right subtrees of the node
            left = self.__create_tree(entities[0:middle_value], depth + 1)
            right = self.__create_tree(entities[middle_value + 1:], depth + 1)

            # Create the node with the right and left subtrees
            node = Node(median, depth, left, right)

            # Insert the node into the nodes list at the index 0
            # The nodes at the bottom of the tree are at the beginning of the list
            self.nodes.insert(0, node)
            self.points.append(median.get_coordinates())
            return node

    def find(self, point: tuple[float, float]) -> bool | BaseEntity:
        """
        Checks through the points list to see if the point exists in the tree

        :param point:
        :return:
        """
        return point in self.points

    def range_search(self, point: tuple[float, float], topleft: tuple[float, float],
                     bottomright: tuple[float, float]):
        """
        Performs a Breadth First Search and discards any subtrees that the point can't fall into.
        topleft and bottomright are the coordinates of the search box.

        :param point:
        :param topleft:
        :param bottomright:
        :return:
        """
        points_list = []
        self.queue.append(self.nodes[0])

        while len(self.queue) != 0:
            current_node: Node = self.queue.pop(0)
            depth = current_node.depth
            axis = depth % 2
            opposite = (depth + 1) % 2

            # Get the lower and upper bounds based on the axis
            # If the axis is the x-axis, lb is the leftmost point
            # And ub is the rightmost point
            # However for the y-axis this must be flipped, since in pygame
            # Higher y values are lower down on the screen
            lb = topleft[axis] if axis == 0 else bottomright[axis]
            ub = bottomright[axis] if axis == 0 else topleft[axis]

            # If the point axis falls within the boundaries,
            # check if the other axis also falls within it
            if lb <= current_node.data.get_coordinates()[axis] <= ub:
                # Append any children to the queue
                if current_node.left_child is not None:
                    self.queue.append(current_node.left_child)
                if current_node.right_child is not None:
                    self.queue.append(current_node.right_child)

                # Get the lb and ub of the opposite axis.
                # If the axis is the x-axis, then the opposite is the y-axis
                lb = topleft[opposite] if opposite == 0 else bottomright[opposite]
                ub = bottomright[opposite] if opposite == 0 else topleft[opposite]

                # Check if the opposite axis also falls within the
                # boundaries. This way we check that both the x and y falls within
                # The box.
                if lb <= current_node.data.get_coordinates()[opposite] <= ub and current_node.data.get_coordinates() != point:
                    points_list.append(current_node.data)
            else:
                # Only append children to the queue if
                # there is a possibility of that subtree
                # Falling within the box.
                # Since all left children should be less than the current node
                # If it is greater, there is no chance that the point falls within the box
                if point[axis] < current_node.data.get_coordinates()[axis] and current_node.left_child is not None:
                    self.queue.append(current_node.left_child)
                elif point[axis] > current_node.data.get_coordinates()[axis] and current_node.right_child is not None:
                    self.queue.append(current_node.right_child)

        # Sort the point list based on vector distance
        points_list.sort(key=lambda pt: (pt.x - point[0])**2 + (pt.y - point[1])**2)
        return points_list
