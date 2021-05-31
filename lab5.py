import math
import numpy as np
import tsplib95
import os
import sys
import random
import matplotlib.pyplot as plt
import time

# REMEMBER: last element of order is the copy of the first one

def create_distance_matrix(nodes):
    distance_matrix = [[0 for _ in range(len(nodes))] for _ in range(len(nodes))]
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            x = nodes[i][0] - nodes[j][0]
            y = nodes[i][1] - nodes[j][1]
            distance_matrix[i][j] = round(math.sqrt(x * x + y * y))
    return distance_matrix

def greedy_expand(distance_matrix, order=None):
    count = math.ceil(len(distance_matrix) / 2)
    if order == None:
        order = [random.randrange(0, len(distance_matrix))]
        order.append(order[0])
    to_pick = [i for i in range(len(distance_matrix)) if i not in order]

    while len(order) < count + 1:
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

def steepest_edge_switch_candidates(distance_matrix,order=None):
    candidates = []
    for distances in distance_matrix:
        candidates.append(sorted(range(len(distances)), key=lambda i: distances[i])[1:6])
    count = math.ceil(len(distance_matrix) / 2)
    if order == None:
        start_point = random.randrange(0, len(distance_matrix))
        order = sorted(range(len(distance_matrix)), key=lambda i: distance_matrix[start_point][i])[:count]
        random.shuffle(order)
    else:
        order.pop()
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

def MSLS(distance_matrix):
    best_length = math.inf
    best_order = None
    for _ in range(100):
        order = steepest_edge_switch_candidates(distance_matrix)
        length = sum(distance_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
        if length < best_length:
            best_length = length
            best_order = order
    return best_order

def ILS1(distance_matrix,end_time):
    if end_time == 0:
        end_time = 7
    def perturbation(order):
        count = math.ceil(len(distance_matrix) / 2)
        for _ in range(2):
            a_index = random.randrange(1,count-2)
            b_index = random.randrange(a_index+2,count)
            start = (a_index + 1) % count
            end = b_index
            while True:
                order[start], order[end] = order[end], order[start]
                start = (start + 1) % count
                if (start == end):
                    break
                end = (end - 1) % count
                if (start == end):
                    break
            order.pop()
            order.append(order[0])
        return order
    count_LS = 0
    t = time.time()
    best_order = steepest_edge_switch_candidates(distance_matrix)
    best_length = sum(distance_matrix[best_order[i]][best_order[i + 1]] for i in range(len(best_order) - 1))
    while True:
        perturbed_order = perturbation(best_order)
        order = steepest_edge_switch_candidates(distance_matrix, perturbed_order)
        count_LS += 1
        length = sum(distance_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
        if length < best_length:
            best_length = length
            best_order = order
        if time.time() - t >= end_time:
            break
    return best_order, count_LS

def ILS2(distance_matrix,end_time):
    if end_time == 0:
        end_time = 7
    def perturbation(order):
        left = random.randrange(0,80)
        right = left + 20
        order.pop()
        del order[left:right]
        order.append(order[0])
        order = greedy_expand(distance_matrix, order)
        return order
    count_LS = 0
    t = time.time()
    best_order = steepest_edge_switch_candidates(distance_matrix)
    best_length = sum(distance_matrix[best_order[i]][best_order[i + 1]] for i in range(len(best_order) - 1))
    while True:
        perturbed_order = perturbation(best_order)
        order = steepest_edge_switch_candidates(distance_matrix, perturbed_order)
        count_LS += 1
        length = sum(distance_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
        if length < best_length:
            best_length = length
            best_order = order
        if time.time() - t >= end_time:
            break
    return best_order, count_LS

def ILS2a(distance_matrix,end_time):
    def perturbation(order):
        left = random.randrange(0,80)
        right = left + 20
        order.pop()
        del order[left:right]
        order.append(order[0])
        order = greedy_expand(distance_matrix, order)
        return order
    count_LS = 0
    t = time.time()
    best_order = steepest_edge_switch_candidates(distance_matrix)
    best_length = sum(distance_matrix[best_order[i]][best_order[i + 1]] for i in range(len(best_order) - 1))
    while True:
        order = perturbation(best_order)
        length = sum(distance_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
        if length < best_length:
            best_length = length
            best_order = order
        if time.time() - t >= end_time:
            break
    return best_order, count_LS

def compare_solutions(order1, order2):
    count = len(order1) - 1
    o1 = order1[:count]
    o2 = order2[:count]
    try:
        index1 = o1.index(o2[0])
        for index2 in range(1, count):
            if o1[(index1 + index2) % count] != o2[index2]:
                return False
        return True
    except:
        return False

def find_common_paths(order1, order2):
    count = len(order1) - 1
    o1 = order1[:count]
    o2 = order2[:count]
    paths = []
    path = []
    last_index2 = None
    for node1 in o1:
        try:
            index2 = o2.index(node1)
            if len(path) > 0 and (last_index2 + 1) % count != index2:
                paths.append(path)
                path = []
            last_index2 = index2
            path.append(node1)
        except:
            if len(path) > 0:
                paths.append(path)
                path = []
    return paths

def exists_in_paths(paths, element):
    for path in paths:
        if element in path:
            return True
    return False

def join_paths(paths, uncommon_nodes: list, count):
    random.shuffle(paths)
    total = 0
    for path in paths:
        total += len(path)
    while total != count:
        if (total > count):
            total -= len(paths[-1])
            uncommon_nodes += paths[-1]
            paths.pop()
        else:
            index = random.randrange(0, len(uncommon_nodes))
            total += 1
            paths.insert(random.randrange(0, len(paths)), [uncommon_nodes[index]])
            uncommon_nodes.pop(index)
    order = []
    for path in paths:
        order += path
    order.append(order[0])
    return order

def evolution(distance_matrix, end_time):
    population = []
    while len(population) < 20:
        order = greedy_expand(distance_matrix)
        length = sum(distance_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
        insert = True
        for p_order, p_length in population:
            if length == p_length and compare_solutions(order, p_order):
                insert = False
                break
        if insert:
            population.append((order, length))
    t = time.time()
    count_LS = 0
    while True:
        parents = random.sample(population, 2)
        common_paths = find_common_paths(parents[0][0], parents[1][0])
        uncommon_nodes = []
        for parent in parents:
            for node in parent[0]:
                if node not in uncommon_nodes and not exists_in_paths(common_paths, node):
                    uncommon_nodes.append(node)
        order = join_paths(common_paths, uncommon_nodes, len(parents[0][0]) - 1)
        order = steepest_edge_switch_candidates(distance_matrix, order)
        count_LS += 1
        length = sum(distance_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
        max_index = max(range(len(population)), key=lambda i: population[i][1])
        if length < population[max_index][1]:
            population[max_index] = order, length
        if time.time() - t >= end_time:
            break
    return min(population, key=lambda p: p[1])[0], count_LS
    

filenames = ['kroA200.tsp', 'kroB200.tsp']
#methods = [MSLS, ILS1, ILS2, ILS2a, evolution]
methods = [evolution]
names = {
    MSLS: "Multiple start local search",
    ILS1: "Iteracyjne przeszukiwanie lokalne z niewielką perturbacją",
    ILS2: "Iteracyjne przeszukiwanie lokalne z perturbacją typu Destroy-Repair",
    ILS2a: "ILS2 w wersji bez wykorzystania lokalnego przeszukiwania",
    evolution: "Hybrydowy algorytm ewolucyjny"
}
for filename in filenames:
    print(filename)
    problem = tsplib95.load(os.path.join(sys.path[0], filename))
    nodes = list(problem.node_coords.values())
    distance_matrix = create_distance_matrix(nodes)
    avg_time_MSLS = 9.4
    for method in methods:
        print(names[method])
        lengths = []
        times = []
        times_LS = []
        best_length = math.inf
        best_order = None
        for _ in range(10):
            t = time.time()
            if method == MSLS:
                order = method(distance_matrix)
                times.append(round(time.time() - t))
            else:
                order, count_LS = method(distance_matrix,avg_time_MSLS)
                times_LS.append(count_LS)
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
        if method == MSLS:
            avg_time_MSLS = np.average(times)
            print("Avg Czas: ",avg_time_MSLS)
        else:
            print("Liczba urochomień LS: avg: {0}, min: {1}, max: {2}\n".format(np.average(times_LS), min(times_LS), max(times_LS)))
        plt.title("{0}, {1}".format(filename, names[method]))
        plt.scatter(x, y)
        plt.plot(line_x, line_y)
        plt.show()