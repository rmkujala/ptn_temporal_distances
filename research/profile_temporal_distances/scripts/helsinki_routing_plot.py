from __future__ import print_function

import os
import pickle

import networkx
import pandas
import pytz

from gtfspy.routing.connection_scan_profile import ConnectionScanProfiler
from gtfspy.routing.models import Connection
from gtfspy.routing.plots import plot_temporal_distance_variation

fname = "../results/tmpdata.pickle"
helsinki_data_basedir = "../data/helsinki/2016-09-28/"
target_stop_I = 115
recompute = True

if not recompute and os.path.exists(fname):
    print("Loading precomputed data")
    profiles = pickle.load(open(fname, 'rb'))
    print("Loaded precomputed data")
else:
    print("Recomputing temporal distances to target")
    events = pandas.read_csv(helsinki_data_basedir + "main.day.temporal_network.csv")
    events.sort_values("dep_time_ut", ascending=False, inplace=True)
    # events = events.iloc[:100000]

    connections = [
        Connection(int(e.from_stop_I), int(e.to_stop_I), int(e.dep_time_ut), int(e.arr_time_ut), int(e.trip_I)) for e in events.itertuples()
    ]

    transfers = pandas.read_csv(helsinki_data_basedir + "main.day.transfers.csv")
    filtered_transfers = transfers[transfers["d_walk"] <= 500]
    net = networkx.Graph()
    for row in filtered_transfers.itertuples():
        net.add_edge(int(row.from_stop_I), int(row.to_stop_I), {"d_walk": row.d_walk})

    print("Data loaded")

    csp = ConnectionScanProfiler(connections, target_stop=target_stop_I, walk_network=net, walk_speed=1.5)
    csp.run()
    profiles = dict(csp.stop_profiles)
    pickle.dump(profiles, open(fname, 'wb') , -1)


from_stop_Is = [
    123,   # kamppi as well
    3356,  # dipoli
    3063,  # kilon asema
    5935   # sorvatie, sipoo
]

nodes = pandas.read_csv(helsinki_data_basedir + "main.day.nodes.csv")

target_stop_name = nodes[nodes["stop_I"] == target_stop_I]["name"].values[0]
for from_stop_I in from_stop_Is:
    from_stop_name = nodes[nodes["stop_I"] == from_stop_I]["name"].values[0]
    stop_profile = profiles[from_stop_I]
    if len(stop_profile.get_pareto_tuples()) > 0:
        fig = plot_temporal_distance_variation(stop_profile, timezone=pytz.timezone("Europe/Helsinki"))
        ax = fig.get_axes()[0]
        ax.set_title(u"From " + from_stop_name + u" to " + target_stop_name)
        fig.savefig(u"../results/" + from_stop_name + "_to_" + target_stop_name + ".pdf")


