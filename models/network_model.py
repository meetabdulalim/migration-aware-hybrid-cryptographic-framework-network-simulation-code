import random
import networkx as nx
from config import CONFIG

# The topology for each network size is generated once and cached, so all runs
# of an experiment share it (run-to-run variation does not include topology).
_TOPOLOGY_CACHE = {}


def build_topology(num_endpoints):
    key = (num_endpoints, CONFIG['avg_degree'], CONFIG['rewire_prob'])
    if key in _TOPOLOGY_CACHE:
        return _TOPOLOGY_CACHE[key]

    k = min(CONFIG['avg_degree'], max(2, num_endpoints - 1))
    if k % 2 == 1:
        k += 1
    k = min(k, num_endpoints - 1 if (num_endpoints - 1) % 2 == 0 else num_endpoints - 2)
    if k < 2:
        k = 2

    g = nx.connected_watts_strogatz_graph(num_endpoints, k, CONFIG['rewire_prob'], tries=200)
    _TOPOLOGY_CACHE[key] = g
    return g


def sample_route_hops(num_endpoints):
    g = build_topology(num_endpoints)
    src, dst = random.sample(list(g.nodes), 2)
    path = nx.shortest_path(g, src, dst)
    return max(1, len(path) - 1)


def hop_propagation_delay_ms(hops):
    lo, hi = CONFIG['per_hop_delay_ms']
    return sum(random.uniform(lo, hi) for _ in range(max(1, hops)))


def qkd_path_available(hops):
    coverage = CONFIG['qkd_link_coverage']
    return random.random() < (coverage ** max(1, hops))
