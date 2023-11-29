from time import monotonic


class Node:
    def __init__(self, data, left_node, right_node, depth):
        self.data = data
        self.left_child = left_node
        self.right_child = right_node
        self.depth = depth

    def __repr__(self):
        try:
            left_data = self.left_child.data
        except:
            left_data = None

        try:
            right_data = self.right_child.data
        except:
            right_data = None
        return f"Left: {left_data}\tData: {self.data}\tRight: {right_data}\tDepth: {self.depth}"


class KDTree:
    def __init__(self, points: list[tuple[float, float]], depth: int = 0):
        self.queue = []
        self.nodes = []

        self.__create_tree(points, depth)

    def __repr__(self):
        string = ""
        for i in self.nodes:
            string = f"{string}\n{i}"

        return string

    def __create_tree(self, points: list[tuple[float, float]], depth: int = 0):
        # Get the axis to sort the points by initially. The root note will be 0, and thus give me the x-axis (0)
        axis = depth % 2
        if len(points) != 0:
            points.sort(key=lambda x: x[axis])
            middle_value = len(points) // 2
            median_point = points[middle_value]

            left = self.__create_tree(points[0:middle_value], depth + 1)
            right = self.__create_tree(points[middle_value + 1:], depth + 1)

            node = Node(median_point, left, right, depth)
            self.nodes.insert(0, node)
            return node

    def search(self, point):
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
            elif node.data == point:
                found = True
                return node.data
            elif point[axis] <= node.data[axis]:
                node = node.left_child
            elif point[axis] >= node.data[axis]:
                node = node.right_child


def test_4(display: bool = False):
    test_points = [(0, 36), (4, 84), (6, 48), (7, 65), (9, 66), (9, 75), (11, 25), (14, 16),
                   (29, 32), (33, 44), (39, 52), (43, 96), (43, 76), (48, 0), (50, 51), (55, 47),
                   (61, 88), (64, 73), (66, 66), (68, 0), (68, 94), (73, 8), (74, 0), (76, 22),
                   (91, 90), (99, 85), (100, 95), (100, 57), (100, 8), (100, 97), (19, 40),
                   (12, 60), (3, 54), (19, 70)]

    tree = KDTree(test_points)

    print("Running Test 4")
    start = monotonic()
    point = tree.search((43, 76))
    end = monotonic()

    print(f"Time Elapsed: {end - start}")
    if display:
        print(point)


def test_5(display: bool = False):
    test_points = [(0, 36), (4, 84), (6, 48), (7, 65), (9, 66), (9, 75), (11, 25), (14, 16),
                   (29, 32), (33, 44), (39, 52), (43, 96), (43, 76), (48, 0), (50, 51), (55, 47),
                   (61, 88), (64, 73), (66, 66), (68, 0), (68, 94), (73, 8), (74, 0), (76, 22),
                   (91, 90), (99, 85), (100, 95), (100, 57), (100, 8), (100, 97), (19, 40),
                   (12, 60), (3, 54), (19, 70)]

    tree = KDTree(test_points)

    print("Running Test 4")
    start = monotonic()
    point = tree.search((63, 76))
    end = monotonic()

    print(f"Time Elapsed: {end - start}")
    if display:
        print(point)


if __name__ == "__main__":
    test_4(True)
    test_5(True)
