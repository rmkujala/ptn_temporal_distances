from __future__ import print_function

import os
import pickle

import networkx
import numpy
import pandas

from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from gtfspy.routing.node_profile_multiobjective import NodeProfileMultiObjective
from gtfspy.routing.models import Connection

from gtfspy.routing.multi_objective_pseudo_connection_scan_profiler import MultiObjectivePseudoCSAProfiler

from settings import HELSINKI_DATA_BASEDIR, RESULTS_DIRECTORY, ROUTING_START_TIME_DEP, ROUTING_END_TIME_DEP, \
    ANALYSIS_START_TIME_DEP, HELSINKI_NODES_FNAME, ANALYSIS_END_TIME_DEP, HELSINKI_TRANSIT_CONNECTIONS_FNAME


def target_list_to_str(targets):
    targets_str = "_".join([str(target) for target in targets])
    return targets_str


def get_profile_data(targets=None, recompute=False, **kwargs):
    if targets is None:
        targets = [115]
    node_profiles_fname = os.path.join(RESULTS_DIRECTORY, "node_profile_" + target_list_to_str(targets) + ".pickle")
    if not recompute and os.path.exists(node_profiles_fname):
        print("Loading precomputed data")
        profiles = pickle.load(open(node_profiles_fname, 'rb'))
        print(profiles)
        print("Loaded precomputed data")
    else:
        print("Recomputing profiles")
        profiles = _compute_profile_data(targets, return_profiler=False, **kwargs)
        pickle.dump(profiles, open(node_profiles_fname, 'wb'), -1)
        print("Recomputing profiles")
    return profiles


def get_node_profile_statistics(targets, recompute=False, recompute_profiles=False):

    profile_statistics_fname = os.path.join(RESULTS_DIRECTORY, "node_profile_statistics_" +
                                            target_list_to_str(targets) + ".pickle")
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
    events = pandas.read_csv(HELSINKI_TRANSIT_CONNECTIONS_FNAME)
    events = events[events["dep_time_ut"] >= ROUTING_START_TIME_DEP]
    time_filtered_events = events[events["dep_time_ut"] <= ROUTING_END_TIME_DEP]
    time_filtered_events.sort_values("dep_time_ut", ascending=False, inplace=True)

    connections = [
        Connection(int(e.from_stop_I), int(e.to_stop_I), int(e.dep_time_ut), int(e.arr_time_ut), int(e.trip_I))
        for e in time_filtered_events.itertuples()
        ]
    return connections


def _read_connections_csv(routing_start_time, routing_end_time):
    import csv
    # header: from_stop_I, to_stop_I, dep_time_ut, arr_time_ut, route_type, route_id, trip_I, seq
    from_node_index = 0
    to_node_index = 1
    dep_time_index = 2
    arr_time_index = 3
    trip_I_index = 6
    connections = []
    with open(HELSINKI_TRANSIT_CONNECTIONS_FNAME, 'r') as csvfile:
        events_reader = csv.reader(csvfile, delimiter=',')
        for _row in events_reader:
            break
        for row in events_reader:
            dep_time = int(row[dep_time_index])
            if routing_start_time <= dep_time <= routing_end_time:
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


def _get_new_csp(targets=None, params=None, verbose=True):
    if "routing_start_time_dep" not in params or params["routing_start_time_dep"] is None:
        params["routing_start_time_dep"] = ROUTING_START_TIME_DEP
    if "routing_end_time_dep" not in params or params["routing_end_time_dep"] is None:
        params['routing_end_time_dep'] = ROUTING_END_TIME_DEP

    connections = _read_connections_csv(
        params["routing_start_time_dep"],
        params["routing_end_time_dep"]
    )
    if targets is None:
        targets = [connections[0].departure_stop]

    if "max_walk_distance" not in params:
        print("resetting max walk distance to default (1000m)")
        params["max_walk_distance"] = 1000
    net = _read_transfers_csv(params["max_walk_distance"])
    if "track_time" not in params:
        print("setting time tracking on")
        params["track_time"] = True
    if "track_vehicle_legs" not in params:
        print("setting vehicle boarding counting on")
        params["track_vehicle_legs"] = True
    if "transfer_margin" not in params:
        print("resetting transfer margin to 180 seconds")
        params["transfer_margin"] = 180
    if "walking_speed" not in params:
        print("resetting walking speed to default value of 70m/60s:")
        params["walking_speed"] = 70 / 60.0

    print(params)
    csp = MultiObjectivePseudoCSAProfiler(
        connections,
        targets,
        walk_network=net,
        walk_speed=params["walking_speed"],
        track_vehicle_legs=params["track_vehicle_legs"],
        track_time=params["track_time"],
        verbose=verbose,
        transfer_margin=params["transfer_margin"]
    )


    return csp, params


def _compute_profile_data(targets=[115], track_vehicle_legs=True, track_time=True,
                          routing_start_time_dep=None, routing_end_time_dep=None,
                          csp=None, verbose=True, return_profiler=False):
    """
    Compute profile data

    Parameters
    ----------
    targets
    track_vehicle_legs
    track_time
    routing_start_time_dep
    routing_end_time_dep
    csp: connection scan profiler instance
        targets are used to reset it

    Returns
    -------
    profiles: dict
    csp: MultiObjectivePseudoCSAProfiler
    """
    max_walk_distance = 1000
    walking_speed = 70 / 60.0
    transfer_margin = 180
    params = {
        "track_vehicle_legs": track_vehicle_legs,
        "track_time": track_time,
        "walking_speed": walking_speed,
        "transfer_margin": transfer_margin,
        "routing_start_time_dep": routing_start_time_dep,
        "routing_end_time_dep": routing_end_time_dep,
        "max_walk_distance": max_walk_distance,
        "targets": targets
    }
    if csp is None:
        csp, params = _get_new_csp(targets=targets, params=params, verbose=verbose)
    else:
        csp.reset(targets)

    print("CSA Profiler running...")
    csp.run()
    print("CSA profiler finished")


    profiles = {"params": params,
                "profiles": dict(csp.stop_profiles)
    }
    if return_profiler:
        return profiles, csp
    return profiles


def _compute_node_profile_statistics(targets, recompute_profiles=False):
    profile_data = get_profile_data(targets, recompute=recompute_profiles)['profiles']
    return __compute_profile_stats_from_profiles(profile_data)




def __compute_profile_stats_from_profiles(profile_data):
    """

    Parameters
    ----------
    profiles: dict
        mapping from stop_I -> MultiObjectiveNodeProfile

    Returns
    -------
    observable_name_to_data: dict
    """
    profile_summary_methods, profile_observable_names = NodeProfileAnalyzerTimeAndVehLegs.all_measures_and_names_as_lists()
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
            _assert_results_are_positive_if_not_infs_or_nans(observable_value)
            observable_name_to_data[observable_name].append(observable_value)
    return observable_name_to_data

def _assert_results_are_positive_if_not_infs_or_nans(value):
    is_nan = numpy.isnan(value)
    is_inf = numpy.isinf(value)
    is_not_negative = value >= 0
    assert (is_nan or is_inf or is_not_negative)


def compute_all_to_all_profile_statistics_with_defaults(target_Is=None, verbose=False):
    nodes = pandas.read_csv(HELSINKI_NODES_FNAME)
    csp = None
    if target_Is is None:
        target_Is = nodes['stop_I']
    for i, target_I in enumerate(target_Is):
        print(target_I, i, "/", len(target_Is))

        try:
            data, csp = _compute_profile_data([target_I], csp=csp, verbose=verbose, return_profiler=True)
        except AssertionError as e:
            continue

        obs_name_to_data = __compute_profile_stats_from_profiles(data["profiles"])
        fname = os.path.join(RESULTS_DIRECTORY, "all_to_all_stats", "all_to_all_stats_target_{target}.pkl".format(target=str(target_I)))
        to_store = {
            "target": target_I,
            "params": data["params"],
            "stats": obs_name_to_data
        }
        with open(fname, "wb") as f:
            pickle.dump(to_store, f, -1)


if __name__ == "__main__":
    # ROUTING_START_TIME_DEP = 1475528220
    ROUTING_END_TIME_DEP = ROUTING_START_TIME_DEP + 3600  # 1475530980
    targets = [115]
    _profile_data, csp = _compute_profile_data(
        targets=targets, track_vehicle_legs=True, track_time=True,
        routing_start_time_dep=ROUTING_START_TIME_DEP,
        routing_end_time_dep=ROUTING_END_TIME_DEP,
        csp=None, return_profiler=True
    )

    profiles = _profile_data['profiles']

    min_tdists = [NodeProfileAnalyzerTimeAndVehLegs(profile,
                                                    start_time_dep=ANALYSIS_START_TIME_DEP,
                                                    end_time_dep=ANALYSIS_END_TIME_DEP).min_temporal_distance()
                  for profile in _profile_data['profiles'].values()]

    uniques = numpy.unique(numpy.ceil(numpy.array(min_tdists) / 60.0))

    # performance testing:
    # orig_routing_end_time_dep = ROUTING_END_TIME_DEP
    # for i in range(1, 5):  # , 5):
    #     ROUTING_END_TIME_DEP = ROUTING_START_TIME_DEP + i * 3600
    #     print("Total routing time: (hours)", (ROUTING_END_TIME_DEP - ROUTING_START_TIME_DEP) / 3600.)
    #     _compute_profile_data()
