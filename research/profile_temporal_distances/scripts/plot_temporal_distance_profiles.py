"""
Plot temporal distances based on pre-computed node-profiles
"""
import pandas
import pytz

from gtfspy.routing.node_profile_analyzer_time import NodeProfileAnalyzerTime
from gtfspy.routing.label import LabelTimeWithBoardingsCount
from gtfspy.routing.node_profile_multiobjective import NodeProfileMultiObjective
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from settings import HELSINKI_NODES_FNAME, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP
from compute import get_profile_data
from matplotlib import pyplot as plt

target_stop_I = 3373
# 3373 Innopoli | Pasila 532 | Kamppi 115 | Piispanaukio 3491
profile_data = get_profile_data([target_stop_I], recompute=False, track_vehicle_legs=True)

nodes = pandas.read_csv(HELSINKI_NODES_FNAME)

profiles = profile_data["profiles"]

from_stop_Is = [
    # 123,    # Kamppi (as well)
    # 401,    # Kansanelakelaitos
    # 3356,   # Dipoli
    # 3063,   # Kilon asema
    # 5935,   # Sorvatie
    # 3101,   # lahderannanristi
    # 3373,     # Innopoli
    2843      # Vallikatu (Pohjois-Leppavaara)
]

timezone = pytz.timezone("Europe/Helsinki")

target_stop_name = nodes[nodes["stop_I"] == target_stop_I]["name"].values[0]
for from_stop_I in from_stop_Is:
    from_stop_name = nodes[nodes["stop_I"] == from_stop_I]["name"].values[0]
    stop_profile = profiles[from_stop_I]
    if isinstance(stop_profile, NodeProfileMultiObjective) and stop_profile.label_class == LabelTimeWithBoardingsCount:
        analyzer = NodeProfileAnalyzerTimeAndVehLegs(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
        print(analyzer.max_n_boardings_along_shortest_paths())
    else:
        analyzer = NodeProfileAnalyzerTime(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)

    for show_stats in ["trip", "tdist", None]:
        plot_tdist_stats = False
        plot_trip_stats = False

        fname = u"../results/" + from_stop_name + "_to_" + target_stop_name + "_fastest"
        if show_stats == "trip":
            plot_trip_stats = True
            fname += u"_trip_stats"
        elif show_stats == "tdist":
            plot_tdist_stats = True
            fname += u"_tdist_stats"
        fname += u".pdf"

        fig = analyzer.plot_fastest_temporal_distance_profile(timezone=timezone,
                                                              plot_tdist_stats=plot_tdist_stats,
                                                              plot_trip_stats=plot_trip_stats)
        ax = fig.get_axes()[0]
        ax.set_title(u"From " + from_stop_name + u" to " + target_stop_name)
        fig.savefig(fname)

    fname = u"../results/" + from_stop_name + "_to_" + target_stop_name + ".pdf"
    fig = analyzer.plot_temporal_distance_variation(timezone=timezone)
    ax = fig.get_axes()[0]
    ax.set_title(u"From " + from_stop_name + u" to " + target_stop_name)
    fig.savefig(fname)

    plt.show()
