import math
import numpy as np
import tsplib95
import os
import sys
import random
import matplotlib.pyplot as plt
import time
import itertools
import tqdm
import scipy.stats

def create_distance_matrix(nodes):
    distance_matrix = [[0 for _ in range(len(nodes))] for _ in range(len(nodes))]
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            x = nodes[i][0] - nodes[j][0]
            y = nodes[i][1] - nodes[j][1]
            distance_matrix[i][j] = round(math.sqrt(x * x + y * y))
    return distance_matrix

#generuj deltę (zmianę) funkcji celu (odległości) dla ruchów wewnątrztrasowych i dwóch sąsiedztw
def generateDeltGoal(ai,bi,dist,current):
    a = current[ai]
    b = current[bi]
    if ai - bi == 1 or ai - bi == 1 - len(current):
        ai, bi = bi, ai
        a, b = b, a
    sum = dist[current[ai-1]][b] - dist[current[ai-1]][a]
    sum += dist[current[(bi+1)%len(current)]][a] - dist[current[(bi+1)%len(current)]][b]
    return sum

#generuj deltę funckcji celu dla ruchów zmieniających zbiór wierzchołków   
def generateDeltOffRoute(ai,b,dist,current):
    a = current[ai]
    sum = dist[current[ai-1]][b] + dist[current[(ai+1)%len(current)]][b] - (dist[current[ai-1]][a] + dist[current[(ai+1)%len(current)]][a])
    return sum

#algorytm zachłanny przeszukiwania lokalnego
def greedy(current, offRoute, dist):
    deltGoal = 0
    bestDelt = 0
    end1=False
    end2=False
    while(1):
        bestDelt = 0
        draw = bool(random.getrandbits(1)) #wylosuj rodzaj ruchu
        if (draw or end2): #wewnątrztrasowy
            combIndexes = list(itertools.combinations(range(len(current)),2))
            random.shuffle(combIndexes)
            for ai, bi in combIndexes:
                deltGoal = generateDeltGoal(ai,bi,dist,current)
                if deltGoal < 0:
                    bestDelt = deltGoal
                    if (ai == len(current)-1 and bi == 0) or (ai == 0 and bi == len(current)-1):
                        current[ai], current[bi] = current[bi], current[ai]
                    else:
                        temp = current[ai:bi+1]
                        temp.reverse()
                        current[ai:bi+1] = temp
                    break
                
            if bestDelt == 0:
                end1 = True

        else: #pozatrasowy
            shufled = list(range(len(current)))
            random.shuffle(shufled)
            for ai in shufled:
                for bi in range(len(offRoute)):
                    b = offRoute[bi]
                    deltGoal = generateDeltOffRoute(ai,b,dist,current)
                    if deltGoal < 0:
                        a = current[ai]
                        bestDelt = deltGoal
                        current[ai], offRoute[bi] = b, a
                        break
                else:
                    continue
                break
            if bestDelt == 0:
                end2 = True

        if end1 and end2:
            break

    return current

#generuj losową trasę obejmującą 50% węzłów
def randomRoute(distance_matrix):
    order = [0]
    to_pick = list(range(1, len(distance_matrix)))
    while len(to_pick) > len(distance_matrix)/2:
        rand = random.choice(to_pick)
        order.append(rand)
        to_pick.remove(rand)
    return order, to_pick

def correlationCorners(order1, order2):
    sum = 0
    for i in range(len(order1)):
        a1 = order1[i]
        b1 = order1[i - 1]
        for j in range(len(order2)):
            a2 = order2[j]
            b2 = order2[j - 1]
            if (a1 == a2 and b1 == b2) or (a1 == b2 and a2 == b1):
                sum += 1
                break
    return sum / len(order1)

filenames = ['kroA200.tsp', 'kroB200.tsp']
for filename in filenames:
    print(filename)
    problem = tsplib95.load(os.path.join(sys.path[0], filename))
    nodes = list(problem.node_coords.values())
    distance_matrix = create_distance_matrix(nodes)
    solutions = []
    for _ in tqdm.tqdm(range(1000)):
        order, offRoute = randomRoute(distance_matrix)
        order = greedy(order,offRoute,distance_matrix)
        length = sum(distance_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
        solutions.append((order, length))
    
    best_order, best_length = min(solutions, key=lambda s: s[1])

    x = [node[0] for node in nodes]
    y = [node[1] for node in nodes]
    line_x = [nodes[i][0] for i in best_order + [best_order[0]]]
    line_y = [nodes[i][1] for i in best_order + [best_order[0]]]

    lengths = [l for _, l in solutions]
    avg_len = np.average(lengths)
    min_len = min(lengths)
    max_len = max(lengths)
    print(f"Długość trasy: avg: {avg_len}, min: {min_len}, max: {max_len}")
    plt.title(f"{filename} - najlepsza trasa")
    plt.scatter(x, y)
    plt.plot(line_x, line_y)
    plt.show()

    lengths.remove(best_length)
    best_set = set(best_order)
    similarities_by_nodes = [len(best_set.intersection(o)) / len(o) for o, _ in solutions]
    similarities_by_nodes.remove(1.0)
    print(f"Współczynnik korelacji (wierzchołki): {scipy.stats.pearsonr(lengths, similarities_by_nodes)[0]}")
    plt.title(f"{filename} - zależność podobieństwa (wierzchołki) do długości trasy")
    plt.scatter(lengths, similarities_by_nodes)
    plt.show()
    print(f"Średnie podobieństwo (wierzchołki): {np.average(similarities_by_nodes)}")

    similarities_by_corners = [correlationCorners(best_order, o) for o, _ in solutions]
    similarities_by_corners.remove(1.0)
    print(f"Współczynnik korelacji (krawędzie): {scipy.stats.pearsonr(lengths, similarities_by_corners)[0]}")
    plt.title(f"{filename} - zależność podobieństwa (krawędzie) do długości trasy")
    plt.scatter(lengths, similarities_by_corners)
    plt.show()
    print(f"Średnie podobieństwo (krawędzie): {np.average(similarities_by_corners)}")

    similarities = [(similarities_by_nodes[i] + similarities_by_corners[i]) / 2 for i in range(len(similarities_by_nodes))]
    plt.title(f"{filename} - zależność podobieństwa (średnie) do długości trasy")
    plt.scatter(lengths, similarities)
    plt.show()
