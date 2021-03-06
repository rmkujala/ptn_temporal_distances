import os

import numpy
import pandas
from matplotlib import gridspec
from matplotlib import pyplot as plt
from matplotlib import rc

from compute import _compute_profile_data
from gtfspy.routing.label import LabelTimeWithBoardingsCount
from gtfspy.routing.node_profile_analyzer_time import NodeProfileAnalyzerTime
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from gtfspy.routing.node_profile_multiobjective import NodeProfileMultiObjective
import settings
from settings import FIGS_DIRECTORY, RESULTS_DIRECTORY
from settings import HELSINKI_NODES_FNAME, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP, TIMEZONE
from util import make_filename_nice, make_string_latex_friendly, get_data_or_compute

"""
Code for plotting the real-world temporal distance profile examples shown in the paper.
This script is somewhat unnecessarily complicated, and is probably not a good intro how to work with gtfspy.
"""

rc("text", usetex=True)

target_stop_I = settings.get_stop_I_by_stop_id(settings.AALTO_UNIVERSITY_ID)

params = {
    "targets": [target_stop_I],
    "routing_start_time_dep": settings.ROUTING_START_TIME_DEP,
    "routing_end_time_dep": settings.ROUTING_END_TIME_DEP
}

fname = os.path.join(RESULTS_DIRECTORY, "example_profiles.pickle")
profile_data = get_data_or_compute(fname, _compute_profile_data, recompute=False, **params)

# profile_data = get_profile_data([target_stop_I], recompute=True, track_vehicle_legs=True)
print(profile_data["params"])

nodes = pandas.read_csv(HELSINKI_NODES_FNAME, sep=";")

profiles = profile_data["profiles"]

from_stop_Is = [
    # 123,    # Kamppi (as well)
    # 401,    # Kansanelakelaitos
    # 3356,   # Dipoli
    # 3063,   # Kilon asema
    # 5935,   # Sorvatie
    # 3101,   # lahderannanristi
    # 3373,   # Innopoli
    # 2843    # Vallikatu (Pohjois-Leppavaara)
    settings.get_stop_I_by_stop_id(settings.ITAKESKUS_ID),
    settings.get_stop_I_by_stop_id(settings.MUNKKIVUORI_ID)
]

target_stop_name = "Aalto University"
# nodes[nodes["stop_I"] == target_stop_I]["name"].values[0]


fig1 = plt.figure(figsize=(11, 3.5))
fig2 = plt.figure(figsize=(11, 3.5))

fig1_fname = FIGS_DIRECTORY + "/profile_" + target_stop_name + "_from_"
fig2_fname = FIGS_DIRECTORY + "/profile_w_transfers_" + target_stop_name + "_from_"

gs1 = gridspec.GridSpec(1, 6)
gs1.update(left=0.05, right=0.48, wspace=0.15, bottom=0.22)
gs2 = gridspec.GridSpec(1, 6)
gs2.update(left=0.55, right=0.98, wspace=0.15, bottom=0.22)

# Loop over from_stop_Is
from_stop_names = ["It\\\"akeskus", "Munkkivuori"]
for i, (gs, from_stop_I, from_stop_name) in enumerate(zip([gs1, gs2], from_stop_Is, from_stop_names)):
    fig1_fname += from_stop_name.replace('\"', "").replace("\\", "") + "_"
    fig2_fname += from_stop_name.replace('\"', "").replace("\\", "") + "_"
    print(fig1_fname, fig1_fname)

    stop_profile = profiles[from_stop_I]
    if isinstance(stop_profile, NodeProfileMultiObjective) and stop_profile.label_class == LabelTimeWithBoardingsCount:
        analyzer = NodeProfileAnalyzerTimeAndVehLegs(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
        print(analyzer.max_n_boardings_on_shortest_paths())
    else:
        analyzer = NodeProfileAnalyzerTime(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)

    title = u"From " + from_stop_name + u" to " + target_stop_name

    plt.figure(fig1.number)
    ax1 = plt.subplot(gs[:, :4])
    dep_times = numpy.array(analyzer.get_time_profile_analyzer().trip_departure_times) / 60 % 60

    ax = analyzer.plot_fastest_temporal_distance_profile(timezone=TIMEZONE,
                                                           plot_tdist_stats=True,
                                                           format_string="%H:%M",
                                                           ax=ax1,
                                                           lw=3)
    fig1 = ax.figure
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=40, ha="center")
    ax2 = plt.subplot(gs[:, 4:])
    ta = analyzer.get_time_profile_analyzer(analyzer.max_trip_n_boardings())
    ta.plot_temporal_distance_pdf_horizontal(ax=ax2, legend_loc="bottom")
    ax1.legend(loc="best", prop={'size': 12})
    fig1.text(0.25 + 0.5 * i, 0.94, make_string_latex_friendly(title), ha="center", va="center", size=14)

    plt.figure(fig2.number)
    ax_1 = plt.subplot(gs[:, :4])

    # Print fastest-path temporal distance statistics:
    print("mean_temporal_distance: ", analyzer.mean_temporal_distance() / 60.0)
    print("mean_temporal_distance_with_min_n_boardings: ",
          analyzer.mean_temporal_distance_with_min_n_boardings() / 60.0)
    time_diff = analyzer.mean_temporal_distance_with_min_n_boardings() / 60.0 - analyzer.mean_temporal_distance() / 60.0
    print("difference in mean t: ", time_diff)
    print("mean_n_boardings: ", analyzer.mean_n_boardings_on_shortest_paths())
    boarding_diff = analyzer.mean_n_boardings_on_shortest_paths() - analyzer.min_n_boardings()
    print("difference in boardings: ", boarding_diff)

    analyzer.plot_new_transfer_temporal_distance_profile(
        timezone=TIMEZONE,
        format_string="%H:%M",
        ax=ax_1,
        plot_journeys=False,
        default_lw=3,
        fastest_path_lw=3
    )

    ax_2 = plt.subplot(gs[:, 4:])

    legend_loc = "lower left"

    analyzer.plot_temporal_distance_pdf_horizontal(ax=ax_2, legend_font_size=9, legend_loc=legend_loc)
    fig2.text(0.25 + 0.5 * i, 0.94, make_string_latex_friendly(title), ha="center", va="center", size=14)

    # Annotate axes using letters, and adjust plots
    for ii, (_ax1, _ax2) in enumerate(zip([ax1, ax_1], [ax2, ax_2])):
        _ax1.set_ylim(0, 80)
        _ax2.set_ylim(0, 80)
        _ax2.set_yticklabels(["" for _ in ax2.get_yticks()])
        _ax2.set_xticks([0.05, 0.10])
        _ax2.set_xlabel("$P(\\tau)")
        _ax2.set_ylabel("")

        letter = "AC"[i]
        _ax1.text(0.04, 0.98,
                  "\\textbf{" + letter + "}",
                  horizontalalignment="left",
                  verticalalignment="top",
                  transform=_ax1.transAxes,
                  fontsize=15,
                  color="black")

        letter = "BD"[i]
        _ax2.text(0.04, 0.98,
                  "\\textbf{" + letter + "}",
                  horizontalalignment="left",
                  verticalalignment="top",
                  transform=_ax2.transAxes,
                  fontsize=15,
                  color="black")

        if i == 0:
            _ax2_xticks = [0.10, 0.20, 0.3]
        else:
            _ax2_xticks = [0.05, 0.10, 0.15]
        _ax2.set_xticks(_ax2_xticks)
        plt.setp(_ax1.xaxis.get_majorticklabels(), rotation=40, ha="center")

# show the figures
plt.show()

# Save figures
fig1_fname = make_filename_nice(fig1_fname + "_fastest_trip_stats.pdf")
fig2_fname = make_filename_nice(fig2_fname + ".pdf")
print(fig1_fname, fig2_fname)
fig1.savefig(fig1_fname)
fig2.savefig(fig2_fname)
