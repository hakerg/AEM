import math
import numpy as np
import tsplib95
import os
import sys
import random
import matplotlib.pyplot as plt
import time
import heapq

def create_distance_matrix(nodes):
    distance_matrix = [[0 for _ in range(len(nodes))] for _ in range(len(nodes))]
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            x = nodes[i][0] - nodes[j][0]
            y = nodes[i][1] - nodes[j][1]
            distance_matrix[i][j] = round(math.sqrt(x * x + y * y))
    return distance_matrix

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

def steepest_edge_switch(distance_matrix):
    count = math.ceil(len(distance_matrix) / 2)
    start_point = random.randrange(0, len(distance_matrix))
    order = sorted(range(len(distance_matrix)), key=lambda i: distance_matrix[start_point][i])[:count]
    random.shuffle(order)
    outside = [i for i in range(len(distance_matrix)) if i not in order]
    while True:
        min_delta = 0
        for a_index in range(count):
            a = order[a_index]
            an = order[(a_index + 1) % count]
            ap = order[(a_index - 1) % count]
            # wymiana krawędzi
            for b_index in range(a_index + 1, count):
                b = order[b_index]
                bn = order[(b_index + 1) % count]
                delta = distance_matrix[a][b] + distance_matrix[an][bn] - distance_matrix[a][an] - distance_matrix[b][bn]
                if delta < min_delta:
                    min_delta = delta
                    min_a_index = a_index
                    min_b_index = b_index
                    switch_points = False
            # wymiana wierzchołków spoza trasy
            for b_index in range(len(outside)):
                b = outside[b_index]
                delta = distance_matrix[ap][b] + distance_matrix[b][an] - distance_matrix[ap][a] - distance_matrix[a][an]
                if delta < min_delta:
                    min_delta = delta
                    min_a_index = a_index
                    min_b_index = b_index
                    switch_points = True
        if min_delta < 0:
            if switch_points:
                # zamień wierzchołki
                order[min_a_index], outside[min_b_index] = outside[min_b_index], order[min_a_index]
            else:
                # zamień krawędzie
                start = (min_a_index + 1) % count
                end = min_b_index
                while True:
                    order[start], order[end] = order[end], order[start]
                    start = (start + 1) % count
                    if (start == end):
                        break
                    end = (end - 1) % count
                    if (start == end):
                        break
        else:
            break
    order.append(order[0])
    return order

def steepest_edge_switch_candidates(distance_matrix):
    candidates = []
    for distances in distance_matrix:
        candidates.append(sorted(range(len(distances)), key=lambda i: distances[i])[1:6])

    count = math.ceil(len(distance_matrix) / 2)
    start_point = random.randrange(0, len(distance_matrix))
    order = sorted(range(len(distance_matrix)), key=lambda i: distance_matrix[start_point][i])[:count]
    random.shuffle(order)
    outside = [i for i in range(len(distance_matrix)) if i not in order]
    while True:
        min_delta = 0
        for a_index in range(count):
            a = order[a_index]
            an = order[(a_index + 1) % count]
            ap = order[(a_index - 1) % count]
            for b in candidates[a]:
                # wymiana krawędzi
                try:
                    b_index = order.index(b)
                    bn = order[(b_index + 1) % count]
                    delta = distance_matrix[a][b] + distance_matrix[an][bn] - distance_matrix[a][an] - distance_matrix[b][bn]
                    if delta < min_delta:
                        min_delta = delta
                        min_a_index = a_index
                        min_b_index = b_index
                        switch_points = False
                # wymiana wierzchołków spoza trasy
                except:
                    b_index = outside.index(b)
                    delta = distance_matrix[ap][b] + distance_matrix[b][an] - distance_matrix[ap][a] - distance_matrix[a][an]
                    if delta < min_delta:
                        min_delta = delta
                        min_a_index = a_index
                        min_b_index = b_index
                        switch_points = True
        if min_delta < 0:
            if switch_points:
                # zamień wierzchołki
                order[min_a_index], outside[min_b_index] = outside[min_b_index], order[min_a_index]
            else:
                # zamień krawędzie
                start = (min_a_index + 1) % count
                end = min_b_index
                while True:
                    order[start], order[end] = order[end], order[start]
                    start = (start + 1) % count
                    if (start == end):
                        break
                    end = (end - 1) % count
                    if (start == end):
                        break
        else:
            break
    order.append(order[0])
    return order

class Move:
    def __init__(self, ap, a, an, b, bn, switch_points, delta):
        self.ap = ap
        self.a = a
        self.an = an
        self.b = b
        self.bn = bn
        self.switch_points = switch_points
        self.delta = delta
    
    def __lt__(self, other):
        return self.delta < other.delta

def steepest_edge_switch_move_list(distance_matrix):
    count = math.ceil(len(distance_matrix) / 2)
    start_point = random.randrange(0, len(distance_matrix))
    order = sorted(range(len(distance_matrix)), key=lambda i: distance_matrix[start_point][i])[:count]
    random.shuffle(order)
    outside = [i for i in range(len(distance_matrix)) if i not in order]
    moves_heap = []
    moves_matrix = [[[False, False] for _ in range(len(distance_matrix))] for _ in range(len(distance_matrix))]
    indexes_to_check = list(range(count))
    while True:
        for a_index in indexes_to_check:
            a = order[a_index]
            an = order[(a_index + 1) % count]
            ap = order[(a_index - 1) % count]
            # wymiana krawędzi
            for b_index in range(count):
                b = order[b_index]
                if a == b or moves_matrix[a][b][False] or moves_matrix[b][a][False]:
                    continue
                bn = order[(b_index + 1) % count]
                delta = distance_matrix[a][b] + distance_matrix[an][bn] - distance_matrix[a][an] - distance_matrix[b][bn]
                if delta < 0:
                    heapq.heappush(moves_heap, Move(None, a, an, b, bn, False, delta))
                    moves_matrix[a][b][False] = True
                    moves_matrix[b][a][False] = True
            # wymiana wierzchołków spoza trasy
            for b_index in range(len(outside)):
                b = outside[b_index]
                if moves_matrix[a][b][True] or moves_matrix[b][a][True]:
                    continue
                delta = distance_matrix[ap][b] + distance_matrix[b][an] - distance_matrix[ap][a] - distance_matrix[a][an]
                if delta < 0:
                    heapq.heappush(moves_heap, Move(ap, a, an, b, None, True, delta))
                    moves_matrix[a][b][True] = True
                    moves_matrix[b][a][True] = True

        if len(moves_heap) == 0:
            break

        move = heapq.heappop(moves_heap)
        indexes_to_check = []
        try:
            a_index = order.index(move.a)
            if move.switch_points:
                # zamień wierzchołki
                b_index = outside.index(move.b)
                ap_index = (a_index - 1) % count
                an_index = (a_index + 1) % count
                if move.ap == order[ap_index] and move.an == order[an_index]:
                    order[a_index], outside[b_index] = outside[b_index], order[a_index]
                indexes_to_check = [a_index]
            else:
                # zamień krawędzie
                b_index = order.index(move.b)
                an_index = (a_index + 1) % count
                bn_index = (b_index + 1) % count
                if move.an == order[an_index] and move.bn == order[bn_index]:
                    start = an_index
                    end = b_index
                    while True:
                        order[start], order[end] = order[end], order[start]
                        start = (start + 1) % count
                        if (start == end):
                            break
                        end = (end - 1) % count
                        if (start == end):
                            break
                indexes_to_check = [a_index, b_index]
        except:
            pass
        moves_matrix[move.a][move.b][move.switch_points] = False
        moves_matrix[move.b][move.a][move.switch_points] = False
    order.append(order[0])
    return order

def steepest_both(distance_matrix):
    candidates = []
    for distances in distance_matrix:
        candidates.append(sorted(range(len(distances)), key=lambda i: distances[i])[1:6])
        
    count = math.ceil(len(distance_matrix) / 2)
    start_point = random.randrange(0, len(distance_matrix))
    order = sorted(range(len(distance_matrix)), key=lambda i: distance_matrix[start_point][i])[:count]
    random.shuffle(order)
    outside = [i for i in range(len(distance_matrix)) if i not in order]
    moves_heap = []
    moves_matrix = [[[False, False] for _ in range(len(distance_matrix))] for _ in range(len(distance_matrix))]
    indexes_to_check = list(range(count))
    while True:
        for a_index in indexes_to_check:
            a = order[a_index]
            an = order[(a_index + 1) % count]
            ap = order[(a_index - 1) % count]
            for b in candidates[a]:
                # wymiana krawędzi
                try:
                    b_index = order.index(b)
                    if a == b or moves_matrix[a][b][False] or moves_matrix[b][a][False]:
                        continue
                    bn = order[(b_index + 1) % count]
                    delta = distance_matrix[a][b] + distance_matrix[an][bn] - distance_matrix[a][an] - distance_matrix[b][bn]
                    if delta < 0:
                        heapq.heappush(moves_heap, Move(None, a, an, b, bn, False, delta))
                        moves_matrix[a][b][False] = True
                        moves_matrix[b][a][False] = True
                # wymiana wierzchołków spoza trasy
                except:
                    if moves_matrix[a][b][True] or moves_matrix[b][a][True]:
                        continue
                    b_index = outside.index(b)
                    delta = distance_matrix[ap][b] + distance_matrix[b][an] - distance_matrix[ap][a] - distance_matrix[a][an]
                    if delta < 0:
                        heapq.heappush(moves_heap, Move(ap, a, an, b, None, True, delta))
                        moves_matrix[a][b][True] = True
                        moves_matrix[b][a][True] = True

        if len(moves_heap) == 0:
            break

        move = heapq.heappop(moves_heap)
        indexes_to_check = []
        try:
            a_index = order.index(move.a)
            if move.switch_points:
                # zamień wierzchołki
                b_index = outside.index(move.b)
                ap_index = (a_index - 1) % count
                an_index = (a_index + 1) % count
                if move.ap == order[ap_index] and move.an == order[an_index]:
                    order[a_index], outside[b_index] = outside[b_index], order[a_index]
                indexes_to_check = [a_index]
            else:
                # zamień krawędzie
                b_index = order.index(move.b)
                an_index = (a_index + 1) % count
                bn_index = (b_index + 1) % count
                if move.an == order[an_index] and move.bn == order[bn_index]:
                    start = an_index
                    end = b_index
                    while True:
                        order[start], order[end] = order[end], order[start]
                        start = (start + 1) % count
                        if (start == end):
                            break
                        end = (end - 1) % count
                        if (start == end):
                            break
                indexes_to_check = [a_index, b_index]
        except:
            pass
        moves_matrix[move.a][move.b][move.switch_points] = False
        moves_matrix[move.b][move.a][move.switch_points] = False
    order.append(order[0])
    return order

filenames = ['kroA200.tsp', 'kroB200.tsp']
methods = [steepest_edge_switch_move_list, steepest_edge_switch_candidates, steepest_both, steepest_edge_switch, regret_heuristics]
names = {
    steepest_edge_switch_move_list: "Steepest + lista ruchów",
    steepest_edge_switch_candidates: "Steepest + ruchy kandydackie",
    steepest_both: "Steepest + lista ruchów + ruchy kandydackie",
    steepest_edge_switch: "Steepest z wymianą krawędzi",
    regret_heuristics: "Heurystyka konstrukcyjna z żalem"
}
for filename in filenames:
    print(filename)
    problem = tsplib95.load(os.path.join(sys.path[0], filename))
    nodes = list(problem.node_coords.values())
    distance_matrix = create_distance_matrix(nodes)

    for method in methods:
        print(names[method])
        lengths = []
        times = []
        best_length = math.inf
        best_order = None
        for _ in range(100):
            t = time.time()
            order = method(distance_matrix)
            times.append(round((time.time() - t) * 1000))
            length = sum(distance_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
            lengths.append(length)
            if length < best_length:
                best_length = length
                best_order = order

        x = [node[0] for node in nodes]
        y = [node[1] for node in nodes]
        line_x = [nodes[i][0] for i in best_order]
        line_y = [nodes[i][1] for i in best_order]

        print("Długość trasy: avg: {0}, min: {1}, max: {2}".format(np.average(lengths), min(lengths), max(lengths)))
        print("Czas: avg: {0} ms, min: {1} ms, max: {2} ms\n".format(np.average(times), min(times), max(times)))
        plt.title("{0}, {1}".format(filename, names[method]))
        plt.scatter(x, y)
        plt.plot(line_x, line_y)
        plt.show()