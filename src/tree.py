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
        self.points = []
        self.nodes = []
        self.queue = []
        start = datetime.now()
        self.__create_tree(points, depth)
        log(f"Tree of size {len(self.nodes)} created in {datetime.now() - start}")

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

            lb = topleft[axis] if axis == 0 else bottomright[axis]
            ub = bottomright[axis] if axis == 0 else topleft[axis]

            if lb <= current_node.data.get_coordinates()[axis] <= ub:
                if current_node.left_child is not None:
                    self.queue.append(current_node.left_child)
                if current_node.right_child is not None:
                    self.queue.append(current_node.right_child)

                lb = topleft[opposite] if opposite == 0 else bottomright[opposite]
                ub = bottomright[opposite] if opposite == 0 else topleft[opposite]

                if lb <= current_node.data.get_coordinates()[opposite] <= ub and current_node.data.get_coordinates() != point:
                    points_list.append(current_node.data)
            else:
                if point[axis] < current_node.data.get_coordinates()[axis] and current_node.left_child is not None:
                    self.queue.append(current_node.left_child)
                elif point[axis] > current_node.data.get_coordinates()[axis] and current_node.right_child is not None:
                    self.queue.append(current_node.right_child)

        return points_list
