"""
Plot temporal distances based on pre-computed node-profiles
"""
import pandas
import pytz

from gtfspy.routing.node_profile_analyzer_time import NodeProfileAnalyzerTime
from gtfspy.routing.label import LabelTimeWithBoardingsCount
from gtfspy.routing.node_profile_multiobjective import NodeProfileMultiObjective
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from settings import HELSINKI_NODES_FNAME, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP, TIMEZONE
from settings import OTANIEMI_STOP_ID, ITAKESKUS_STOP_ID, MUNKKIVUORI_STOP_ID
from compute import get_profile_data
from matplotlib import pyplot as plt

from util import make_filename_nice

target_stop_I = OTANIEMI_STOP_ID
# Some old ones:
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
    # 2843      # Vallikatu (Pohjois-Leppavaara)
    ITAKESKUS_STOP_ID,
    MUNKKIVUORI_STOP_ID
]


target_stop_name = nodes[nodes["stop_I"] == target_stop_I]["name"].values[0]

if target_stop_name == "Alvar Aallon puisto":
    target_stop_name = "Alvar Aalto's park"

fig1 = plt.figure(figsize=(11, 4))

fig1_fname = u"../results/" + target_stop_name + "_from_"

for i, from_stop_I in enumerate(from_stop_Is):
    from_stop_name = nodes[nodes["stop_I"] == from_stop_I]["name"].values[0]

    stop_profile = profiles[from_stop_I]
    if isinstance(stop_profile, NodeProfileMultiObjective) and stop_profile.label_class == LabelTimeWithBoardingsCount:
        analyzer = NodeProfileAnalyzerTimeAndVehLegs(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
        print(analyzer.max_n_boardings_on_shortest_paths())
    else:
        analyzer = NodeProfileAnalyzerTime(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)

    plot_tdist_stats = True

    ax1 = fig1.add_subplot(1, 2, i + 1)
    fig1 = analyzer.plot_fastest_temporal_distance_profile(timezone=TIMEZONE,
                                                           plot_tdist_stats=plot_tdist_stats,
                                                           format_string="%H:%M",
                                                           ax=ax1,
                                                           lw=3)
    ax1.set_ylim(0, 60)
    ax1.legend(loc="best", prop={'size': 12})

    ax1.set_title(u"From " + from_stop_name + u" to " + target_stop_name)
    fig1_fname += from_stop_name + "_"

    if i == len(from_stop_Is) - 1:
        fig1_fname += "_fastest"
        fig1_fname += u"_trip_stats"
        fig1_fname += u".pdf"
        fig1_fname = make_filename_nice(fig1_fname)
        print(fig1_fname)
        fig1.tight_layout()
        fig1.savefig(fig1_fname)

    fname = u"../results/" + from_stop_name + "_to_" + target_stop_name + ".pdf"
    fname = make_filename_nice(fname)
    print(fname)

    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    analyzer.plot_new_transfer_temporal_distance_profile(timezone=TIMEZONE,
                                                         format_string="%H:%M",
                                                         ax=ax,
                                                         plot_journeys=False,
                                                         default_lw=3,
                                                         fastest_path_lw=3)
    fig1.tight_layout()
    ax.set_title(u"From " + from_stop_name + u" to " + target_stop_name)
    fig.savefig(fname)


plt.show()
