from __future__ import print_function

import os
import pickle

import networkx

from gtfspy.routing.node_profile_multiobjective import NodeProfileMultiObjective
from gtfspy.routing.models import Connection

from gtfspy.routing.multi_objective_pseudo_connection_scan_profiler import MultiObjectivePseudoCSAProfiler

from settings import HELSINKI_DATA_BASEDIR, RESULTS_DIRECTORY, ROUTING_START_TIME_DEP, ROUTING_END_TIME_DEP, \
    ANALYSIS_START_TIME_DEP, HELSINKI_NODES_FNAME, ANALYSIS_END_TIME_DEP

def _targets_to_str(targets):
    targets_str = "_".join([str(target) for target in targets])
    return targets_str

def get_profile_data(targets=[115], recompute=False):
    node_profiles_fname = os.path.join(RESULTS_DIRECTORY, "node_profile_" + _targets_to_str(targets) + ".pickle")
    if not recompute and os.path.exists(node_profiles_fname):
        print("Loading precomputed data")
        profiles = pickle.load(open(node_profiles_fname, 'rb'))
        print(profiles)
        print("Loaded precomputed data")
    else:
        print("Recomputing profiles")
        profiles = _compute_profile_data(targets)
        pickle.dump(profiles, open(node_profiles_fname, 'wb'), -1)
        print("Recomputing profiles")
    return profiles


def get_node_profile_statistics(targets, recompute=False, recompute_profiles=False):

    profile_statistics_fname = os.path.join(RESULTS_DIRECTORY, "node_profile_statistics_" +
                                            _targets_to_str(targets) + ".pickle")
    if recompute_profiles:
        recompute = True
    if not recompute and os.path.exists(profile_statistics_fname):
        print("Loading precomputed statistics")
        observable_name_to_data = pickle.load(open(profile_statistics_fname, 'rb'))
        print("Loaded precomputed statistics")
    else:
        print("Recomputing statistics")
        observable_name_to_data = _compute_node_profile_statistics(targets, recompute_profiles)
        pickle.dump(observable_name_to_data, open(profile_statistics_fname, 'wb'), -1)
        print("Recomputed statistics")
    return observable_name_to_data


def _read_connections_pandas():
    import pandas
    events = pandas.read_csv(HELSINKI_DATA_BASEDIR + "main.day.temporal_network.csv")
    events = events[events["dep_time_ut"] >= ROUTING_START_TIME_DEP]
    time_filtered_events = events[events["dep_time_ut"] <= ROUTING_END_TIME_DEP]
    time_filtered_events.sort_values("dep_time_ut", ascending=False, inplace=True)

    connections = [
        Connection(int(e.from_stop_I), int(e.to_stop_I), int(e.dep_time_ut), int(e.arr_time_ut), int(e.trip_I))
        for e in time_filtered_events.itertuples()
        ]
    return connections


def _read_connections_csv():
    import csv
    # header: from_stop_I, to_stop_I, dep_time_ut, arr_time_ut, route_type, route_id, trip_I, seq
    from_node_index = 0
    to_node_index = 1
    dep_time_index = 2
    arr_time_index = 3
    trip_I_index = 6
    connections = []
    with open(HELSINKI_DATA_BASEDIR + "main.day.temporal_network.csv", 'r') as csvfile:
        events_reader = csv.reader(csvfile, delimiter=',')
        for _row in events_reader:
            break
        for row in events_reader:
            dep_time = int(row[dep_time_index])
            if ROUTING_END_TIME_DEP >= dep_time >= ROUTING_START_TIME_DEP:
                connections.append(Connection(int(row[from_node_index]), int(row[to_node_index]), int(row[dep_time_index]),
                                              int(row[arr_time_index]), int(row[trip_I_index])))
    connections = sorted(connections, key=lambda conn: -conn.departure_time)
    return connections


def _read_transfers_pandas(max_walk_distance=500):
    import pandas
    transfers = pandas.read_csv(HELSINKI_DATA_BASEDIR + "main.day.transfers.csv")
    filtered_transfers = transfers[transfers["d_walk"] <= max_walk_distance]
    net = networkx.Graph()
    for row in filtered_transfers.itertuples():
        net.add_edge(int(row.from_stop_I), int(row.to_stop_I), {"d_walk": row.d_walk})
    return net


def _read_transfers_csv(max_walk_distance=500):
    import csv
    # "from_stop_I,to_stop_I,d,d_walk"
    from_node_index = 0
    to_node_index = 1
    d_walk_index = 3
    net = networkx.Graph()
    with open(HELSINKI_DATA_BASEDIR + "main.day.transfers.csv", 'r') as csvfile:
        transfers_reader = csv.reader(csvfile, delimiter=',')
        for _row in transfers_reader:
            break
        for row in transfers_reader:
            d_walk = int(row[d_walk_index])
            if d_walk <= max_walk_distance:
                net.add_edge(int(row[from_node_index]), int(row[to_node_index]), {"d_walk": int(row[d_walk_index])})
    return net


def _compute_profile_data(targests=[115]):
    max_walk_distance = 500
    walking_speed = 1.5
    connections = _read_connections_csv()
    net = _read_transfers_csv(max_walk_distance)

    # csp = PseudoConnectionScanProfiler(connections, target_stop=target_stop_I, walk_network=net, walk_speed=walking_speed)
    csp = MultiObjectivePseudoCSAProfiler(connections, targets=targests,
                                          walk_network=net, walk_speed=walking_speed,
                                          track_vehicle_legs=True, track_time=True, verbose=True)

    # csp = ConnectionScanProfiler(connections, target_stop=target_stop_I, walk_network=net, walk_speed=walking_speed)
    print("CSA Profiler running...")
    print(len(csp._all_connections))
    csp.run()
    print("CSA profiler finished")

    parameters = {
        "target_stop_I": targests,
        "walk_distance": max_walk_distance,
        "walking_speed": walking_speed
    }

    profiles = {"params": parameters,
                "profiles": dict(csp.stop_profiles)
    }
    return profiles


def _compute_node_profile_statistics(targets, recompute_profiles=False):
    from routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
    import pandas
    profile_summary_methods, profile_observable_names = NodeProfileAnalyzerTimeAndVehLegs.all_measures_and_names_as_lists()

    profile_data = get_profile_data(targets, recompute=recompute_profiles)['profiles']
    profile_summary_data = [[] for _ in range(len(profile_observable_names))]

    observable_name_to_method = dict(zip(profile_observable_names, profile_summary_methods))
    observable_name_to_data = dict(zip(profile_observable_names, profile_summary_data))

    nodes = pandas.read_csv(HELSINKI_NODES_FNAME)
    for stop_I in nodes['stop_I'].values:
        try:
            profile = profile_data[stop_I]
        except KeyError:
            profile = NodeProfileMultiObjective()
            profile.finalize()
        profile_analyzer = NodeProfileAnalyzerTimeAndVehLegs(profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
        for observable_name in profile_observable_names:
            method = observable_name_to_method[observable_name]
            observable_value = method(profile_analyzer)
            if observable_value is None:
                print(observable_name, stop_I)

            observable_name_to_data[observable_name].append(observable_value)

    return observable_name_to_data

if __name__ == "__main__":
    # performance testing:
    orig_routing_end_time_dep = ROUTING_END_TIME_DEP
    for i in range(1, 5):  # , 5):
        ROUTING_END_TIME_DEP = ROUTING_START_TIME_DEP + i * 3600
        print("Total routing time: (hours)", (ROUTING_END_TIME_DEP - ROUTING_START_TIME_DEP) / 3600.)
        _compute_profile_data()
