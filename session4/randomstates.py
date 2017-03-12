import networkx as nx
import pysal as ps
import random # python built in random library
import math

# return index of maximum value in list L
def get_max_idx(L):
    max_i = 0
    for i in range(len(L)):
        if L[i] >= L[max_i]:
            max_i = i
    return max_i

# remove item at index i from list L
def remove_i(L, i):
    return L[:i] + L[i+1:]

# insert item x at index i in list L
def insert_i(L, i, x):
    return L[:i] + [x] + L[i:]


## Election-related
# Apportionment given
# pops = list of county populations
# states = list of the state IDs (actual or 'newstate')
# other parameters are fixed for the US case
def apportion(pops, states, seats_to_assign=435, initial=1, extras=2, exclude='DC'):
    pops = list(pops)
    states = list(states)
    assigned = [initial] * len(pops)
    ex = states.index(exclude)
    assigned = remove_i(assigned, ex)
    pops = remove_i(pops, ex)
    remaining = seats_to_assign - sum(assigned)
    while remaining > 0:
        priorities = [p / math.sqrt(a * (a + 1)) for p, a in zip(pops, assigned)]
        max_priority = get_max_idx(priorities)
        assigned[max_priority] += 1
        remaining -= 1
    assigned = insert_i(assigned, ex, 1)
    assigned = [__ + 2 for __ in assigned]
    return assigned

# Determine election outcome
def run_election(df, statevar='state', pop='population', ev='ev'):
    # states = make_states(df, statevar)
    df[ev] = apportion(df[pop], df[statevar])
    return {'gop': sum(df.ev[df.win == 'R']), 
            'dem': sum(df.ev[df.win == 'D'])}
    

# returns a list of random county ids
def get_seeds(e, graph, method='default'):
    state_ids = list(set(e.state))
    random.shuffle(state_ids)
    seeds = []
    for s in state_ids:
        this_state = [n[0] for n in graph.nodes(data=True) if n[1]['state'] == s]
        seeds.append(random.choice(this_state))
    return seeds, state_ids
    

# We are going to store the neighborhood relations
# in a graph data structure provided by networkx
def random_states(e_map, reqd=''):
    G = nx.Graph()

    # neighborhoods determined by pysal operation
    neighbors = ps.weights.Contiguity.Rook.from_dataframe(e_map)

    # now make the graph, add nodes first
    G.add_nodes_from(range(len(e_map.state)))
    # now read the pysal neighbors structure
    # and add edges to the graph accordingly
    for i, Ni in neighbors: 
        edges = [(i, j) for j in Ni]
        G.add_edges_from(edges)

    # and now add the state affiliation of each as a node attribute
    for i in G.nodes():
        G.node[i]['state'] = e_map.loc[i].state
    
    if reqd == 'graph': return G
    
    seed_counties, state_ids = get_seeds(e_map, G)

    # now make a dictionary recording for each node
    # shortest path, the source seed, and state ID
    # initialize these to very long (1000), -1 (non-existent) and 'XX'
    node_shortest_paths = {n: (1000, -1, "XX") for n in G.nodes()}
    for x in neighbors.islands:
        node_shortest_paths[x] = (0, 0, e_map.loc[x].state)
    
    # Determine shortest paths to all nodes from the seed counties
    distances_from_seeds = [nx.single_source_shortest_path_length(G, n) for n in seed_counties]
    # Now iterate
    for (seed, distances, state_id) in zip(seed_counties, distances_from_seeds, state_ids):
        for target, d in distances.items():
            if d < node_shortest_paths[target][0]:
                node_shortest_paths[target] = (d, seed, state_id)
    # now find shortest paths and use those to assign
    nearest_states = [node_shortest_paths[i][2] for i in node_shortest_paths]
    return nearest_states


def draw_graph(e_map, G):
    import geopandas as gpd
    import shapely
    import matplotlib.pyplot as plt
    import quickplot as qp
    
    centroids = e_map.geometry.centroid
    n_links = gpd.GeoSeries([shapely.geometry.linestring.LineString(
                [centroids.geometry[e[0]], 
                centroids.geometry[e[1]]]) for e in G.edges()])
    fig = plt.figure(figsize=(16,12))
    qp.quickplot(e_map, facecolor='w', edgecolor='k', linewidth=0.2)
    qp.quickplot(n_links, edgecolor='#ff0000', linewidth=0.35)
    qp.quickplot(centroids, markersize=1, color='r')
    
