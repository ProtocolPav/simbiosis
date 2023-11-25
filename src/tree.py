from logs import log
from src.entity import BaseEntity

from datetime import datetime


class Node:
    def __init__(self, data: BaseEntity, depth: int, left_node, right_node):
        self.data = data
        self.left_child = left_node
        self.right_child = right_node
        self.depth = depth

    def __repr__(self):
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
        self.nodes = []
        self.queue = []
        start = datetime.now()
        self.__create_tree(points, depth)
        # log(f"Tree of size {len(self.nodes)} created in {datetime.now() - start}")

    def __create_tree(self, entities: list[BaseEntity], depth: int = 0):
        axis = depth % 2
        if len(entities) != 0:
            entities.sort(key=lambda i: (i.x if axis == 0 else i.y))
            middle_value = len(entities) // 2
            median = entities[middle_value]

            left = self.__create_tree(entities[0:middle_value], depth + 1)
            right = self.__create_tree(entities[middle_value + 1:], depth + 1)

            node = Node(median, depth, left, right)
            self.nodes.insert(0, node)
            return node

    def find(self, point: tuple[float, float]) -> bool | BaseEntity:
        """
        Performs a Binary Search through the tree until it finds a node with
        the specified coordinates or reaches a leaf node
        :param point:
        :return:
        """
        node: Node = self.nodes[0] if len(self.nodes) != 0 else None
        depth = 0
        found = False
        leaf = False
        while not (found or leaf):
            axis = depth % 2
            if node is None:
                leaf = True
                return False
            elif node.data.get_coordinates() == point:
                found = True
                print(point)
                return node.data
            elif point[axis] <= node.data.get_coordinates()[axis]:
                node = node.left_child
            elif point[axis] >= node.data.get_coordinates()[axis]:
                node = node.right_child
            # There was a bug here where i didnt have the equals and it would enter a forever loop and crash. I fixed it.
            # Bug where it does not properly find all of the points...

    def range_search(self, node: Node, radius: float):
        """
        Performs a Breadth First Search through the tree, discarding subtrees that
        have no chance of falling within the box.
        :param node:
        :param radius:
        :return:
        """
        ...
