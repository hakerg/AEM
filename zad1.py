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
    order = [0]
    to_pick = list(range(1, len(distance_matrix)))
    while len(to_pick) > 0:
        distance_list = distance_matrix[order[-1]]
        shortest = min(to_pick, key=lambda index: distance_list[index])
        order.append(shortest)
        to_pick.remove(shortest)
    return order

def greedy_expand(distance_matrix):
    min_i = 0
    min_j = 1
    for i in range(len(distance_matrix)):
        for j in range(len(distance_matrix)):
            if i != j and distance_matrix[i][j] < distance_matrix[min_i][min_j]:
                min_i = i
                min_j = j
    order = [min_i, min_j]
    to_pick = list(range(len(distance_matrix)))
    to_pick.remove(min_i)
    to_pick.remove(min_j)
    while len(to_pick) > 0:
        distance_list_1 = distance_matrix[order[-1]]
        distance_list_2 = distance_matrix[order[-2]]
        new_index = min(to_pick, key=lambda index: distance_list_1[index] + distance_list_2[index])
        order.append(new_index)
        to_pick.remove(new_index)
    return order

def regret_heuristics(distance_matrix):
    min_i = 0
    min_j = 1
    for i in range(len(distance_matrix)):
        for j in range(len(distance_matrix)):
            if i != j and distance_matrix[i][j] < distance_matrix[min_i][min_j]:
                min_i = i
                min_j = j
    order = [min_i, min_j]
    to_pick = list(range(len(distance_matrix)))
    to_pick.remove(min_i)
    to_pick.remove(min_j)
    while len(to_pick) > 1:
        profit_table = []
        best_profits = [-math.inf, -math.inf]
        for index in to_pick:
            profit_list = [-distance_matrix[order[-1]][index] - distance_matrix[order[-2]][index]]
            profit_list.append(max(-distance_matrix[i][index] - distance_matrix[i][order[-1]] for i in to_pick if i != index))
            profit_table.append(profit_list)
            for i in range(2):
                if profit_list[i] > best_profits[i]:
                    best_profits[i] = profit_list[i]
        min_regret = math.inf
        new_index = None
        for i in range(len(to_pick)):
            regret = max(best_profits[0] - profit_table[i][0], best_profits[1] - profit_table[i][1])
            if regret < min_regret:
                min_regret = regret
                new_index = to_pick[i]
        order.append(new_index)
        to_pick.remove(new_index)
    order.append(to_pick[0])
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

    for method in methods:
        lengths = []
        best_length = math.inf
        best_nodes = None
        best_order = None
        for _ in range(50):
            half_nodes = random.sample(nodes, math.ceil(len(nodes) / 2))
            distance_matrix = create_distance_matrix(half_nodes)
            order = method(distance_matrix)
            order.append(order[0])
            length = sum(distance_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
            lengths.append(length)
            if length < best_length:
                best_length = length
                best_nodes = half_nodes
                best_order = order

        x = [node[0] for node in best_nodes]
        y = [node[1] for node in best_nodes]
        line_x = [best_nodes[i][0] for i in best_order]
        line_y = [best_nodes[i][1] for i in best_order]

        plt.title('{0}, {1}\navg: {2}, min: {3}, max: {4}'.format(filename, names[method], np.average(lengths), min(lengths), max(lengths)))
        plt.scatter(x, y)
        plt.plot(line_x, line_y)
        plt.show()