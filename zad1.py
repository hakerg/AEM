import math
import numpy as np
import tsplib95
import os
import sys
import random
import matplotlib.pyplot as plt

def create_distance_matrix(nodes):
    distance_matrix = [[0 for _ in range(len(nodes))] for _ in range(len(nodes))]
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            x = nodes[i][0] - nodes[j][0]
            y = nodes[i][1] - nodes[j][1]
            distance_matrix[i][j] = round(math.sqrt(x * x + y * y))
    return distance_matrix

def nearest_neighbor(distance_matrix):
    count = math.ceil(len(distance_matrix) / 2)
    order = [random.randrange(0, len(distance_matrix))]
    to_pick = [i for i in range(len(distance_matrix)) if i not in order]
    to_pick.sort(key=lambda index: distance_matrix[order[0]][index])
    to_pick = to_pick[:count - 1]

    while len(to_pick) > 0:
        distance_list = distance_matrix[order[-1]]
        shortest = min(to_pick, key=lambda index: distance_list[index])
        order.append(shortest)
        to_pick.remove(shortest)
    
    order.append(order[0])
    return order

def greedy_expand(distance_matrix):
    count = math.ceil(len(distance_matrix) / 2)
    order = [random.randrange(0, len(distance_matrix))]
    to_pick = [i for i in range(len(distance_matrix)) if i not in order]
    to_pick.sort(key=lambda index: distance_matrix[order[0]][index])
    to_pick = to_pick[:count - 1]
    order.append(order[0])

    while len(to_pick) > 0:
        min_cost = math.inf
        min_index = None
        min_place = None
        for index in to_pick:
            for place in range(1, len(order)):
                index_before = order[place - 1]
                index_after = order[place]
                cost = distance_matrix[index_before][index] + distance_matrix[index][index_after] - distance_matrix[index_before][index_after]
                if cost < min_cost:
                    min_cost = cost
                    min_index = index
                    min_place = place
        
        order.insert(min_place, min_index)
        to_pick.remove(min_index)
    return order

def regret_heuristics(distance_matrix):
    count = math.ceil(len(distance_matrix) / 2)
    order = [random.randrange(0, len(distance_matrix))]
    to_pick = [i for i in range(len(distance_matrix)) if i not in order]
    to_pick.sort(key=lambda index: distance_matrix[order[0]][index])
    to_pick = to_pick[:count - 1]
    
    order.append(to_pick[0])
    to_pick.remove(to_pick[0])
    order.append(order[0])

    while len(to_pick) > 0:
        max_regret = -math.inf
        max_index = None
        max_place = None
        for index in to_pick:
            places = []
            for place in range(1, len(order)):
                index_before = order[place - 1]
                index_after = order[place]
                cost = distance_matrix[index_before][index] + distance_matrix[index][index_after] - distance_matrix[index_before][index_after]
                places.append((place, cost))
            places.sort(key=lambda item: item[1])
            regret = places[1][1] - places[0][1]
            if regret > max_regret:
                max_regret = regret
                max_index = index
                max_place = places[0][0]
        
        order.insert(max_place, max_index)
        to_pick.remove(max_index)
    return order

filenames = ['kroA100.tsp', 'kroB100.tsp']
methods = [nearest_neighbor, greedy_expand, regret_heuristics]
names = {
    nearest_neighbor: "Najbliższego sąsiada",
    greedy_expand: "Greedy cycle",
    regret_heuristics: "Regret heuristics"
}
for filename in filenames:
    problem = tsplib95.load(os.path.join(sys.path[0], filename))
    nodes = list(problem.node_coords.values())
    distance_matrix = create_distance_matrix(nodes)

    for method in methods:
        lengths = []
        best_length = math.inf
        best_order = None
        for _ in range(50):
            order = method(distance_matrix)
            length = sum(distance_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
            lengths.append(length)
            if length < best_length:
                best_length = length
                best_order = order

        x = [node[0] for node in nodes]
        y = [node[1] for node in nodes]
        line_x = [nodes[i][0] for i in best_order]
        line_y = [nodes[i][1] for i in best_order]

        print("{0}, {1}: avg: {2}, min: {3}, max: {4}".format(filename, names[method], np.average(lengths), min(lengths), max(lengths)))
        plt.title("{0}, {1}".format(filename, names[method]))
        plt.scatter(x, y)
        plt.plot(line_x, line_y)
        plt.show()