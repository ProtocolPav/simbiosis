import random
from datetime import datetime
from scipy.spatial import KDTree as scitree


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
        self.queue = []

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

    def range_search(self, point: tuple[float, float], topleft: tuple[float, float], bottomright: tuple[float, float]):
        points_list = []
        self.queue.append(self.nodes[0])
        depth = 0

        while len(self.queue) != 0:
            print(f"QUEUE {self.queue}")
            axis = depth % 2
            opposite = (depth + 1) % 2
            current_node: Node = self.queue.pop(0)
            while current_node is None:
                print("Popping again")
                current_node: Node = self.queue.pop(0)

            lb = topleft[axis] if axis == 0 else bottomright[axis]
            ub = bottomright[axis] if axis == 0 else topleft[axis]

            print(f"Currently at: {current_node.data}. Depth {depth}")

            print(lb, current_node.data[axis], ub, lb < current_node.data[axis] < ub)
            if lb < current_node.data[axis] < ub:
                if current_node.left_child is not None:
                    self.queue.append(current_node.left_child)
                if current_node.right_child is not None:
                    self.queue.append(current_node.right_child)

                lb = topleft[opposite] if opposite == 0 else bottomright[opposite]
                ub = bottomright[opposite] if opposite == 0 else topleft[opposite]

                print(lb, current_node.data[opposite], ub, lb < current_node.data[opposite] < ub)
                if lb < current_node.data[opposite] < ub:
                    print(f"POINT FOUND {current_node.data}")
                    points_list.append(current_node.data)
            else:
                print("appending most probable subtree")
                if point[axis] > current_node.data[axis] and current_node.left_child is not None:
                    self.queue.append(current_node.left_child)
                elif point[axis] < current_node.data[axis] and current_node.right_child is not None:
                    self.queue.append(current_node.right_child)

            depth += 1

        return points_list


# point_list = []
# for i in range(10):
#     point = (random.randint(0, 100), random.randint(0, 100))
#     point_list.append(point)
point_list = [(38, 48), (7, 68), (79, 72), (55, 31), (50, 88), (49, 32), (26, 6), (17, 79), (18, 21), (4, 100)]

print("Starting Scitree")
start = datetime.now()
tree = scitree(point_list)
print(datetime.now() - start)

print("Starting My Tree")
start = datetime.now()
tree2 = KDTree(point_list)
print(datetime.now() - start)

for i in tree2.nodes:
    print(i)

random_point = (49, 32)
topleft = random_point[0] - 12, random_point[1] + 12
bottomright = random_point[0] + 12, random_point[1] - 12
print(f"Searching for {random_point}")
list_returned = tree2.range_search(random_point, topleft, bottomright)
print("Final List")
print(list_returned)
