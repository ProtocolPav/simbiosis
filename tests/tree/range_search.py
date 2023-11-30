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

    def range_search(self, point: tuple[float, float], topleft: tuple[float, float], bottomright: tuple[float, float]):
        points_list = []
        self.queue.append(self.nodes[0])

        while len(self.queue) != 0:
            current_node: Node = self.queue.pop(0)
            depth = current_node.depth
            print(f"QUEUE {self.queue}")
            axis = depth % 2
            opposite = (depth + 1) % 2

            lb = topleft[axis] if axis == 0 else bottomright[axis]
            ub = bottomright[axis] if axis == 0 else topleft[axis]

            print(f"Currently at: {current_node.data}. Depth {depth}")

            print(lb, current_node.data[axis], ub, lb <= current_node.data[axis] <= ub)
            if lb <= current_node.data[axis] <= ub:
                if current_node.left_child is not None:
                    self.queue.append(current_node.left_child)
                if current_node.right_child is not None:
                    self.queue.append(current_node.right_child)

                lb = topleft[opposite] if opposite == 0 else bottomright[opposite]
                ub = bottomright[opposite] if opposite == 0 else topleft[opposite]

                print(lb, current_node.data[opposite], ub, lb <= current_node.data[opposite] <= ub)
                if lb <= current_node.data[opposite] <= ub:
                    print(f"POINT FOUND {current_node.data}")
                    points_list.append(current_node.data)
            else:
                if point[axis] < current_node.data[axis] and current_node.left_child is not None:
                    self.queue.append(current_node.left_child)
                    print(f"PROBABLE SUBTREE {current_node.left_child}")
                elif point[axis] > current_node.data[axis] and current_node.right_child is not None:
                    self.queue.append(current_node.right_child)
                    print(f"PROBABLE SUBTREE {current_node.right_child}")

        return points_list


def test_10(display_tree: bool = False):
    test_points = [(0, 36), (4, 84), (6, 48), (7, 65), (9, 66), (9, 75), (11, 25), (14, 16),
                   (29, 32), (33, 44), (39, 52), (43, 96), (43, 76), (48, 0), (50, 51), (55, 47),
                   (61, 88), (64, 73), (66, 66), (68, 0), (68, 94), (73, 8), (74, 0), (76, 22),
                   (91, 90), (99, 85), (100, 95), (100, 57), (100, 8), (100, 97), (19, 40),
                   (12, 60), (3, 54), (19, 70)]
    boxsize = 12

    tree = KDTree(test_points)

    print("Running Test 10")
    start = monotonic()
    all_points = tree.range_search((9, 66), (9-boxsize, 66+boxsize), (9+boxsize, 66-boxsize))
    end = monotonic()

    print(f"Time Elapsed: {end - start}")
    if display_tree:
        print(all_points)


if __name__ == "__main__":
    test_10(True)