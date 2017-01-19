from __future__ import unicode_literals

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
from matplotlib import gridspec

from util import make_filename_nice, make_string_latex_friendly

from matplotlib import rc
rc("text", usetex=True)

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

fig1 = plt.figure(figsize=(11, 3.5))


fig1_fname = u"../results/" + target_stop_name + "_from_"


gs1 = gridspec.GridSpec(1, 6)
gs1.update(left=0.05, right=0.48, wspace=0.15, bottom=0.22)
gs2 = gridspec.GridSpec(1, 6)
gs2.update(left=0.55, right=0.98, wspace=0.15, bottom=0.2)




for i, (gs, from_stop_I) in enumerate(zip([gs1, gs2], from_stop_Is)):
    from_stop_name = nodes[nodes["stop_I"] == from_stop_I]["name"].values[0]


    stop_profile = profiles[from_stop_I]
    if isinstance(stop_profile, NodeProfileMultiObjective) and stop_profile.label_class == LabelTimeWithBoardingsCount:
        analyzer = NodeProfileAnalyzerTimeAndVehLegs(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
        print(analyzer.max_n_boardings_on_shortest_paths())
    else:
        analyzer = NodeProfileAnalyzerTime(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)

    plot_tdist_stats = True

    plt.figure(fig1.number)
    ax1 = plt.subplot(gs[:, :4])

    fig1 = analyzer.plot_fastest_temporal_distance_profile(timezone=TIMEZONE,
                                                           plot_tdist_stats=plot_tdist_stats,
                                                           format_string="%H:%M",
                                                           ax=ax1,
                                                           lw=3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=40, ha="right")

    ax2 = plt.subplot(gs[:, 4:])
    ax2_xticks = [0, 0.05, 0.10]
    ax2.set_xticks(ax2_xticks)
    ax2.set_xticklabels(["0", "0.05", "0.10"])

    ta = analyzer.get_time_profile_analyzer(analyzer.max_trip_n_boardings())
    ta.plot_temporal_distance_pdf_horizontal(ax=ax2)

    ax1.set_ylim(0, 60)
    ax2.set_ylim(0, 60)
    ax2.set_ylabel("")
    ax2.set_yticklabels([""] * len(ax2.get_yticks()))

    ax1.legend(loc="best", prop={'size': 12})

    title = u"From " + from_stop_name + u" to " + target_stop_name

    ax1.set_title(make_string_latex_friendly(title))
    fig1_fname += from_stop_name + "_"

    if i == len(from_stop_Is) - 1:
        fig1_fname += "_fastest"
        fig1_fname += u"_trip_stats"
        fig1_fname += u".pdf"
        fig1_fname = make_filename_nice(fig1_fname)
        fig1.savefig(fig1_fname)

    fname = u"../results/" + from_stop_name + "_to_" + target_stop_name + ".pdf"
    fname = make_filename_nice(fname)

    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    analyzer.plot_new_transfer_temporal_distance_profile(
        timezone=TIMEZONE,
        format_string="%H:%M",
        ax=ax,
        plot_journeys=False,
        default_lw=3,
        fastest_path_lw=3
    )

    # ax.set_title(u"From " + from_stop_name + u" to " + target_stop_name)
    fig.savefig(fname)


plt.show()
