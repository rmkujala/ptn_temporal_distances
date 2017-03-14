import os

from matplotlib import pyplot as plt

from matplotlib import rc
rc("text", usetex=True)

fig = plt.figure(figsize=(8, 4))
subplot_grid = (1, 6)

ax1 = plt.subplot2grid(subplot_grid, (0, 0), colspan=2, rowspan=1)

ax2 = plt.subplot2grid(subplot_grid, (0, 2), colspan=4, rowspan=1)

w = 0.5
events = [
    ("a", "b", 0, 1, "green"),
    ("b", "c", 2-w, 3, "green"),
    ("c", "b", 4, 5+w, "green"),
    ("b", "a", 6, 7, "green"),
    ("a", "b", 8 + 0, 8 + 1, "green"),
    ("b", "c", 8 + 2 -w, 8 + 3, "green"),
    ("c", "b", 8 + 4, 8 + 5 + w, "green"),
    ("b", "a", 8 + 6, 8 + 7, "green"),
    ("d", "e", 4 - 4, 5 - 4, "red"),
    ("e", "d", 2, 3, "red"),
    ("d", "e", 4, 5, "red"),
    ("e", "d", 2 + 4, 3 + 4, "red"),
    ("d", "e", 4 + 4, 5 + 4, "red"),
    ("e", "d", 2 + 8, 3 + 8, "red"),
    ("d", "e", 4 + 8, 5 + 8, "red"),
    ("e", "d", 2 + 12, 3 + 12, "red")
]

# events = [event for event in events if event[3] < 15]

node_name_to_index = {name:i for i, name in enumerate("abcde")}
max_y = 1
min_y = 0
max_t = max((event[3] for event in events))
min_t = min((event[2] for event in events))


def _t_to_x(t):
    assert(t >= min_t)
    assert(t <= max_t)
    return 0.15 + 0.75 * (t - min_t) / (max_t - min_t)

n_nodes = len(node_name_to_index)
y_offset_top = 0.05
y_offset_down = 0.1


step = (max_y - min_y - y_offset_down - y_offset_top)/(n_nodes)
node_ys = [step * (n_nodes - i  - 0.5 ) + y_offset_down for i in range(n_nodes)]
for y, letter in zip(node_ys, "abcde"):
    ax2.plot([0.1, 0.95], [y, y], color="black", ls="-", lw=2)
    ax2.text(0.08, y, letter, va="center", ha="right")

name_to_color = {
    "green": "#66c2a5",
    "red": "#fc8d62",
    "walk": "black"
}


from gtfspy.routing.multi_objective_pseudo_connection_scan_profiler import MultiObjectivePseudoCSAProfiler
from gtfspy.routing.models import Connection

connections = [Connection(departure_stop=e[0], arrival_stop=e[1], departure_time=e[2], arrival_time=e[3], trip_id=e[4], is_walk=False, waiting_time=0)
               for e in events]

import networkx
g = networkx.Graph()
g.add_edge("c", "d", d_walk=0.5)
profiler = MultiObjectivePseudoCSAProfiler(connections, "a", min_t, max_t, transfer_margin=0, walk_network=g, walk_speed=1.0)
pseudo_connections = profiler._pseudo_connections

for i, pseudo_connection in enumerate(pseudo_connections):
    print(i)
    arrival_stop = pseudo_connection.arrival_stop
    arrival_stop_next_departure_time = pseudo_connection.arrival_stop
    arr_time = pseudo_connection.arrival_time
    departure_stop = pseudo_connection.departure_stop
    dep_time = pseudo_connection.departure_time
    color = name_to_color["walk"]
    xs = [_t_to_x(t) for t in [dep_time, arr_time]]
    origin_y = node_ys[node_name_to_index[departure_stop]]
    destination_y = node_ys[node_name_to_index[arrival_stop]]
    from_xy = [xs[0], origin_y]
    to_xy = [xs[1], destination_y]
    ax2.annotate("",
                 xy=to_xy,
                 xytext=from_xy,
                 arrowprops=dict(arrowstyle="simple", fc="white", ec=color, lw=1.5, linestyle="-"),
                 xycoords="data",
                 textcoords="data")



for origin, destination, dep_time, arr_time, name in events:
    color = name_to_color[name]
    origin_index = node_name_to_index[origin]
    origin_y = node_ys[origin_index]
    destination_index = node_name_to_index[destination]
    destination_y = node_ys[destination_index]
    xs = [_t_to_x(t) for t in [dep_time, arr_time]]
    from_xy = [xs[0], origin_y]
    to_xy = [xs[1], destination_y]
    print(from_xy)
    print(to_xy)
    ax2.annotate("",
                 xy=to_xy,
                 xytext=from_xy,
                 arrowprops=dict(arrowstyle="simple", color=color, ls="-"),
                 xycoords="data",
                 textcoords="data")

ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)


for _ax, letter in zip([ax1, ax2], "AB"):
    pass
    _ax.set_xticks([])
    _ax.set_yticks([])
    _ax.text(0.02, 0.98, "\\textbf{" + letter + "}", ha="left", va="top")

handles = []
for name in ["green", "red"]:
    color = name_to_color[name]

from settings import FIGS_DIRECTORY
fig.savefig(os.path.join(FIGS_DIRECTORY, "temporal_network_base.svg"), format="svg")
plt.show()