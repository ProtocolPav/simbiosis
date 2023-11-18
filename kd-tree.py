import random
from datetime import datetime
from scipy.spatial import KDTree as scitree
import matplotlib.pyplot as plt


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

            node = Node(median_point, left, right, depth)
            self.nodes.insert(0, node)
            return node

    def range_search(self, point_node: Node, topleft: tuple[float, float], bottomright: tuple[float, float]):
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
                if point_node.data[axis] < current_node.data[axis] and current_node.left_child is not None:
                    self.queue.append(current_node.left_child)
                    print(f"PROBABLE SUBTREE {current_node.left_child}")
                elif point_node.data[axis] > current_node.data[axis] and current_node.right_child is not None:
                    self.queue.append(current_node.right_child)
                    print(f"PROBABLE SUBTREE {current_node.right_child}")

            # depth += 1

        return points_list


point_list = []
for i in range(300):
    point = (random.randint(0, 100), random.randint(0, 100))
    point_list.append(point)
# point_list = [(38, 48), (7, 68), (79, 72), (55, 31), (50, 88), (49, 32), (26, 6), (17, 79), (18, 21), (4, 100)]
# point_list = [(64, 53), (47, 24), (15, 17), (13, 3), (44, 77), (4, 53), (81, 26), (72, 21), (82, 48), (70, 15)]
# point_list = [(0, 36), (4, 84), (6, 48), (7, 65), (9, 66), (9, 75), (11, 25), (14, 16), (29, 32), (33, 44), (39, 52), (43, 96), (43, 76), (48, 0), (50, 51), (55, 47), (61, 88), (64, 73), (66, 66), (68, 0), (68, 94), (73, 8), (74, 0), (76, 22), (91, 90), (99, 85), (100, 95), (100, 57), (100, 8), (100, 97)]

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
    # if i.data == (49, 32):
    #     random_point = i
    # if i.data == (81, 26):
    #     random_point = i
    # if i.data == (7, 65):
    #     random_point = i

random_point = random.choice(tree2.nodes)
# random_point = (49, 32)
# random_point = (81, 26) # (70, 15)
box_radius = 0
topleft = random_point.data[0] - box_radius, random_point.data[1] + box_radius
bottomright = random_point.data[0] + box_radius, random_point.data[1] - box_radius
print(point_list)
print(f"Searching for {random_point}")
start = datetime.now()
list_returned = tree2.range_search(random_point, topleft, bottomright)
print(datetime.now() - start)

print("Final List")
print(list_returned)

start = datetime.now()
print(tree.query_ball_point(random_point.data, box_radius))
print(datetime.now() - start)

x = []
y = []
for i in point_list:
    x.append(i[0])
    y.append(i[1])

plt.scatter(x, y)
plt.grid()
plt.show()
