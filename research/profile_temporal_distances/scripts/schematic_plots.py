from copy import copy

import settings
from gtfspy.routing.label import LabelTimeSimple, LabelTimeWithBoardingsCount
from gtfspy.routing.node_profile_analyzer_time import NodeProfileAnalyzerTime
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from gtfspy.routing.node_profile_multiobjective import NodeProfileMultiObjective
from gtfspy.routing.node_profile_simple import NodeProfileSimple
import matplotlib.pyplot as plt
from matplotlib import gridspec


from matplotlib import rc
rc('text', usetex=True)

labels_t_dep_dur_b = [
    (8, 4, 2, "A"),   # A
    (11, 4, 1, "B"),  # B
    (15, 5, 2, "C"),  # C
    (18, 4, 1, "D"),  # D
    (21, 5, 1, "E"),  # E
    (8, 6, 1, "F"),   # F (not on fastest path
    (14, 7, 1, "G")  # G (not on fastest path)
]
labels_t_dep_dur_b = list(reversed(sorted(labels_t_dep_dur_b)))

walk_to_target_duration = 10

gs = gridspec.GridSpec(1, 6)
gs.update(left=0.1, right=0.98, wspace=0.15, bottom=0.18)

def plot_plain_profile():
    profile = NodeProfileSimple(walk_to_target_duration=10 * 60)
    for label in labels_t_dep_dur_b:
        profile.update_pareto_optimal_tuples(
            LabelTimeSimple(departure_time=label[0] * 60, arrival_time_target=(label[0] + label[1]) * 60)
        )

    analyzer = NodeProfileAnalyzerTime(profile, 0 * 60, 20 * 60)
    fig = plt.figure(figsize=(5.5, 3.5))


    ax1 = plt.subplot(gs[:, :4])
    analyzer.plot_temporal_distance_profile(format_string="%M",
                                              plot_journeys=True,
                                              lw=3,
                                              ax=ax1,
                                              plot_tdist_stats=True,
                                              alpha=0.15,
                                              plot_trip_stats=False,
                                              duration_divider=60.0)

    ax2 = plt.subplot(gs[:, 4:])
    # ax2 = plt.subplot2grid(subplot_grid, (0, 4), colspan=2, rowspan=1)
    fig = analyzer.plot_temporal_distance_pdf_horizontal(use_minutes=True,
                                                         ax=ax2,
                                                         legend_font_size=9)

    ax2.set_ylabel("")
    ax2.set_yticks([])

    ax1.set_ylim(0, 11.5)
    ax2.set_ylim(0, 11.5)
    ax2.set_xlim(0, 0.3)
    ax2.set_yticklabels(["" for _ in ax2.get_yticks()])
    ax2.set_xticks([0.1, 0.2, 0.3])

    ax1.set_xlabel("Departure time $t_{\\text{dep}}$ (min)")
    ax1.set_ylabel("Temporal distance $\\tau$ (min)")

    handles, labels = ax1.get_legend_handles_labels()
    # legend_order = [4, 3, 0, 1, 2]
    # handles = [handles[order] for order in legend_order]
    # labels = [labels[order] for order in legend_order]

    ax1.legend(handles, labels, loc="best",
               fancybox=True, ncol=2, shadow=False, prop={'size': 9})
    for _ax, letter in zip([ax1, ax2], "AB"):
        _ax.text(0.04, 0.98,
                  "\\textbf{" + letter + "}",
                  horizontalalignment="left",
                  verticalalignment="top",
                  transform=_ax.transAxes,
                  fontsize=15,
                  color="black")
    # fig.tight_layout()
    # plt.subplots_adjust(wspace=0.34)
    fig.savefig(settings.FIGS_DIRECTORY + "schematic_temporal_distance.pdf")


def plot_transfer_profile():
    alphabetical_labels = list(labels_t_dep_dur_b)
    alphabetical_labels.sort(key=lambda el: el[-1])
    for label in alphabetical_labels:
        print(label[-1] + " & " + str(label[0]) + " & " + str(label[0] + label[1]) +
              " & " + str(label[1]) + " & " + str(label[2]) + " \\\\")

    labels = [
        LabelTimeWithBoardingsCount(departure_time=label[0],
                                    arrival_time_target=label[0] + label[1],
                                    n_boardings=label[2],
                                    first_leg_is_walk=False)
        for label in labels_t_dep_dur_b
        ]

    dep_times = list(set(map(lambda el: el.departure_time, labels)))
    p = NodeProfileMultiObjective(dep_times=dep_times,
                                  walk_to_target_duration=10,
                                  label_class=LabelTimeWithBoardingsCount)

    for label in labels:
        p.update([label])

    p.finalize()
    analyzer = NodeProfileAnalyzerTimeAndVehLegs(p, 0, 20)
    print(analyzer.mean_n_boardings_on_shortest_paths())

    journey_letters = [label[-1] for label in labels_t_dep_dur_b[::-1]]

    fig = plt.figure(figsize=(5.5, 3.5))
    subplot_grid = (1, 6)

    ax1 = plt.subplot(gs[:, :4])
    fig = analyzer.plot_new_transfer_temporal_distance_profile(format_string="%S",
                                                               duration_divider=1,
                                                               default_lw=4,
                                                               journey_letters=journey_letters,
                                                               ax=ax1,
                                                               ncol_legend=2,
                                                               legend_font_size=9)

    ax1.set_xlabel("Departure time $t_{\\text{dep}}$ (min)")
    ax1.set_ylabel("Temporal distance $\\tau$ (min)")

    ax2 = plt.subplot(gs[:, 4:])
    ax2 = analyzer.plot_temporal_distance_pdf_horizontal(use_minutes=True,
                                                         duration_divider=1,
                                                         ax=ax2,
                                                         legend_font_size=9)

    ax2.set_ylabel("")

    ax1.set_ylim(0, 11.5)
    ax2.set_ylim(0, 11.5)
    ax2.set_xlim(0, 0.3)
    ax2.set_yticklabels(["" for _ in ax2.get_yticks()])
    ax2.set_xlabel("Probability density $P(\\tau)$")
    ax2.set_xticks([0.1, 0.2, 0.3])

    for _ax, letter in zip([ax1, ax2], "AB"):
        _ax.text(0.04, 0.98,
                  "\\textbf{" + letter + "}",
                  horizontalalignment="left",
                  verticalalignment="top",
                  transform=_ax.transAxes,
                  fontsize=15,
                  color="black")
    fig.savefig(settings.FIGS_DIRECTORY + "schematic_transfer_profile.pdf")
    plt.show()


if __name__ == "__main__":
    plot_plain_profile()
    plot_transfer_profile()
