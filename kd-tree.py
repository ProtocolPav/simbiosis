import random


class Node:
    def __init__(self, data, left_node, right_node):
        self.data = data
        self.left_child = left_node
        self.right_child = right_node

    def __repr__(self):
        try:
            left_data = self.left_child.data
        except:
            left_data = None

        try:
            right_data = self.right_child.data
        except:
            right_data = None
        return f"Left: {left_data}\tData: {self.data}\tRight: {right_data}"


class KDTree:
    def __init__(self, points: list[tuple[float, float]], depth: int = 0):
        self.nodes = []
        self.__create_tree(points, depth)

    def __create_tree(self, points: list[tuple[float, float]], depth: int = 0):
        # Get the axis to sort the points by initially. The root note will be 0, and thus give me the x-axis (0)
        axis = depth % 2
        if len(points) != 0:
            points.sort(key=lambda x: x[axis])
            middle_value = len(points) // 2
            median_point = points[middle_value]

            left = self.__create_tree(points[0:middle_value], depth+1)
            right = self.__create_tree(points[middle_value+1:], depth+1)

            node = Node(median_point, left, right)
            self.nodes.insert(0, node)
            return node

    def insert(self, point: tuple[float, float]):
        ...

    def delete(self, point: tuple[float, float]):
        ...

    def range_search(self, point: tuple[float, float]):
        ...


point_list = []
for i in range(300):
    point = (random.randint(0, 100), random.randint(0, 100))
    point_list.append(point)

tree = KDTree(point_list)
for i in tree.nodes:
    print(i)
