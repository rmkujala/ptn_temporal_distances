import matplotlib.pyplot as plt
from matplotlib import gridspec

import settings
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from gtfspy.routing.multi_objective_pseudo_connection_scan_profiler import MultiObjectivePseudoCSAProfiler
from gtfspy.routing.connection import Connection

import networkx
import matplotlib as mpl
mpl.style.use('classic')


from matplotlib import rc
# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)


OFFSET = 8*3600
events = [
    ("a", "b", 0, 12, "bus_1"),
    ("a", "b", 20, 32, "bus_1"),
    ("a", "b", 40, 52, "bus_1"),
    ("c", "d", 10, 12, "tram_1"),
    ("c", "d", 30, 32, "tram_1"),
    ("d", "e", 15, 17, "bus_2"),
    ("d", "e", 40, 42, "bus_2"),
    ("f", "g", 22, 24, "tram_2"),
    ("f", "g", 42, 44, "tram_2"),
    ("h", "i", 24, 27, "rail"),
    ("j", "k", 00,  6, "subway_1"),
    ("j", "k", 30, 36, "subway_1"),
]
events = [(e[0], e[1], e[2]* 60 + OFFSET, e[3] * 60 + OFFSET, e[4]) for e in events]
nodes = "OabcdefghijkD"
node_name_to_index = {name:i for i, name in enumerate(nodes)}
max_y = 1
min_y = 0
max_t = max((event[3] for event in events))
min_t = min((event[2] for event in events))


dummy_seq = 1
connections = [Connection(e[0], e[1], e[2], e[3], e[4], dummy_seq, is_walk=False)
               for e in events]

g = networkx.Graph()
g.add_edge("O", "a", d_walk=7)
g.add_edge("O", "c", d_walk=2)
g.add_edge("O", "h", d_walk=5)
g.add_edge("b", "D", d_walk=18)
g.add_edge("d", "i", d_walk=3)
g.add_edge("e", "f", d_walk=3)
g.add_edge("e", "D", d_walk=15)
g.add_edge("g", "D", d_walk=4)
g.add_edge("i", "j", d_walk=2)
g.add_edge("k", "D", d_walk=3)
g.add_edge("O", "D", d_walk=60)

profiler = MultiObjectivePseudoCSAProfiler(connections, "D", min_t, max_t, transfer_margin=0, walk_network=g, walk_speed=1.0/60.0)
pseudo_connections = profiler._pseudo_connections


def _t_to_x(t):
    assert(t >= min_t)
    assert(t <= max_t)
    return 0.15 + 0.75 * (t - min_t) / (max_t - min_t)

n_nodes = len(node_name_to_index)
y_offset_top = 0.05
y_offset_down = 0.1

def plot_temporal_network():
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)

    step = (max_y - min_y - y_offset_down - y_offset_top)/(n_nodes)
    node_ys = [step * (n_nodes - i  - 0.5 ) + y_offset_down for i in range(n_nodes)]
    for y, letter in zip(node_ys, nodes):
        ax.plot([0.1, 0.95], [y, y], color="black", ls="-", lw=2)
        ax.text(0.08, y, letter, va="center", ha="right")

    from gtfspy.route_types import ROUTE_TYPE_TO_COLOR, ROUTE_TYPE_TO_LOWERCASE_TAG, WALK
    trip_id_to_color = {}
    for event in events:
        trip_id = event[-1]
        for route_type, tag in ROUTE_TYPE_TO_LOWERCASE_TAG.items():
            if tag in trip_id:
                trip_id_to_color[trip_id] = ROUTE_TYPE_TO_COLOR[route_type]
    trip_id_to_color['walk'] = ROUTE_TYPE_TO_COLOR[WALK]

    for i, pseudo_connection in enumerate(pseudo_connections):
        arrival_stop = pseudo_connection.arrival_stop
        arrival_stop_next_departure_time = pseudo_connection.arrival_stop
        arr_time = pseudo_connection.arrival_time
        departure_stop = pseudo_connection.departure_stop
        dep_time = pseudo_connection.departure_time
        color = trip_id_to_color["walk"]
        xs = [_t_to_x(t) for t in [dep_time, arr_time]]
        origin_y = node_ys[node_name_to_index[departure_stop]]
        destination_y = node_ys[node_name_to_index[arrival_stop]]
        from_xy = [xs[0], origin_y]
        to_xy = [xs[1], destination_y]
        ax.annotate("",
                     xy=to_xy,
                     xytext=from_xy,
                     arrowprops=dict(arrowstyle="simple", fc="white", ec=color, lw=1.5, linestyle="-"),
                     xycoords="data",
                     textcoords="data")


    for origin, destination, dep_time, arr_time, name in events:
        color = trip_id_to_color[name]
        origin_index = node_name_to_index[origin]
        origin_y = node_ys[origin_index]
        destination_index = node_name_to_index[destination]
        destination_y = node_ys[destination_index]
        xs = [_t_to_x(t) for t in [dep_time, arr_time]]
        from_xy = [xs[0], origin_y]
        to_xy = [xs[1], destination_y]
        print(from_xy)
        print(to_xy)
        ax.annotate("",
                     xy=to_xy,
                     xytext=from_xy,
                     arrowprops=dict(arrowstyle="simple", color=color, ls="-"),
                     xycoords="data",
                     textcoords="data")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


profiler.run()
profile = profiler.stop_profiles['O']



def plot_plain_profile(profile):
    gs = gridspec.GridSpec(1, 6)
    gs.update(left=0.1, right=0.96, wspace=0.2, bottom=0.18)
    analyzer = NodeProfileAnalyzerTimeAndVehLegs(profile, 8*3600, 8.5*3600).get_time_profile_analyzer()
    fig = plt.figure(figsize=(5.5, 3.5))

    ax1 = plt.subplot(gs[:, :4])
    analyzer.plot_temporal_distance_profile(format_string="%H:%M",
                                            plot_journeys=True,
                                            journey_letters="BFH",
                                            lw=3,
                                            ax=ax1,
                                            plot_tdist_stats=True,
                                            alpha=0.15,
                                            plot_trip_stats=False,
                                            duration_divider=60)
    print("plotted")
    ax2 = plt.subplot(gs[:, 4:])

    ax2.set_xlim(0, 0.1)

    fig = analyzer.plot_temporal_distance_pdf_horizontal(use_minutes=True,
                                                         ax=ax2,
                                                         legend_font_size=9,
                                                         legend_loc="lower right")

    ax2.set_ylabel("")
    ax2.set_yticks([])
    ax2.set_yticklabels(["" for _ in ax2.get_yticks()])

    ax2.set_xticks([0.05, 0.10])
    ax2.set_yticklabels(["0.05", "0.10"])

    ax1.set_ylim(0, 67)
    ax2.set_ylim(0, 67)

    ax1.set_xlabel("Departure time $t_{\\text{dep}}$ (min)")
    ax1.set_ylabel("Temporal distance $\\tau$ (min)")

    handles, labels = ax1.get_legend_handles_labels()

    ax1.legend(handles, labels, loc="best", ncol=2, shadow=False, prop={'size': 9})
    for _ax, letter in zip([ax1, ax2], "AB"):
        _ax.text(0.04, 0.98,
                  "\\textbf{" + letter + "}",
                  horizontalalignment="left",
                  verticalalignment="top",
                  transform=_ax.transAxes,
                  fontsize=15,
                  color="black")

    fig.savefig(settings.FIGS_DIRECTORY + "schematic_temporal_distance.pdf")


def plot_transfer_profile(profile):
    gs = gridspec.GridSpec(1, 6)
    gs.update(left=0.1, right=0.96, wspace=0.15, bottom=0.18)
    analyzer = NodeProfileAnalyzerTimeAndVehLegs(profile, 8*3600, 8*3600 + 30 * 60)
    print(analyzer.mean_n_boardings_on_shortest_paths())

    fig = plt.figure(figsize=(5.5, 3.5))
    ax1 = plt.subplot(gs[:, :4])
    fig = analyzer.plot_new_transfer_temporal_distance_profile(format_string="%H:%M",
                                                               duration_divider=60,
                                                               default_lw=4,
                                                               journey_letters="BCEFH",
                                                               plot_journeys=True,
                                                               ax=ax1,
                                                               ncol_legend=2,
                                                               legend_font_size=9)

    ax1.set_xlabel("Departure time $t_{\\text{dep}}$ (min)")
    ax1.set_ylabel("Temporal distance $\\tau$ (min)")

    ax2 = plt.subplot(gs[:, 4:])
    ax2 = analyzer.plot_temporal_distance_pdf_horizontal(use_minutes=False,
                                                         duration_divider=60,
                                                         ax=ax2,
                                                         legend_font_size=9,
                                                         legend_loc="lower right")

    ax2.set_ylabel("")

    ax1.set_ylim(0, 67)
    ax2.set_ylim(0, 67)
    ax2.set_xlim(0, 0.1)
    ax2.set_yticklabels(["" for _ in ax2.get_yticks()])
    ax2.set_xlabel("Probability density $P(\\tau)$")
    ax2.set_xticks([0.05, 0.1])
    ax2.get_yaxis().set_tick_params(direction='in')

    for _ax, letter in zip([ax1, ax2], "AB"):
        _ax.text(0.04, 0.98,
                  "\\textbf{" + letter + "}",
                  horizontalalignment="left",
                  verticalalignment="top",
                  transform=_ax.transAxes,
                  fontsize=15,
                  color="black",
                  zorder=99999999)
    fig.savefig(settings.FIGS_DIRECTORY + "schematic_transfer_profile.pdf")



# plot_temporal_network()
plot_plain_profile(profile)
plot_transfer_profile(profile)
# plt.show()

plt.show()
