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

    def range_search(self, point: tuple[float, float], radius: float):
        ...


class KdTree2:
    def __init__(self, P, d=0):
        n = len(P)
        m = n // 2
        P.sort(key = lambda x: x[d])
        self.point = P[m]
        self.d = d
        d = (d + 1) % len(P[0])-1 # -1 because then the last element will not be a dimension (wanted since last ele is info obj)
        self.left = self.right = None
        if m > 0 :
            self.left = KdTree2(P[:m], d)
        if n - (m+1) > 0:
            self.right = KdTree2(P[m+1:], d)


point_list = []
for i in range(30000):
    point = (random.randint(0, 100), random.randint(0, 100))
    point_list.append(point)

print("Starting Scitree")
start = datetime.now()
tree = scitree(point_list)
print(datetime.now() - start)

print("Starting My Tree")
start = datetime.now()
tree2 = KDTree(point_list)
print(datetime.now() - start)

print("Starting Other Tree")
start = datetime.now()
tree3 = KdTree2(point_list)
print(datetime.now() - start)

query_point = point_list[random.randint(0, 300)]
query = tree.query_ball_point(query_point, 10)
