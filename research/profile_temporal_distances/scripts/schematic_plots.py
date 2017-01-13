import settings
from gtfspy.routing.label import LabelTimeSimple, LabelTimeWithBoardingsCount
from gtfspy.routing.node_profile_analyzer_time import NodeProfileAnalyzerTime
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from gtfspy.routing.node_profile_multiobjective import NodeProfileMultiObjective
from gtfspy.routing.node_profile_simple import NodeProfileSimple
import matplotlib.pyplot as plt


def plot_plain_profile():
    # rc('text', usetex=True)
    labels_raw = [
        (12, 16),
        (14, 20),
        (17, 25),
        (22, 26)
    ]
    profile = NodeProfileSimple(walk_to_target_duration=10 * 60)
    for label in labels_raw:
        profile.update_pareto_optimal_tuples(
            LabelTimeSimple(departure_time=label[0] * 60, arrival_time_target=label[1] * 60)
        )

    analyzer = NodeProfileAnalyzerTime(profile, 10 * 60, 20 * 60)
    fig = plt.figure(figsize=(8, 4))
    subplot_grid = (1, 6)
    ax1 = plt.subplot2grid(subplot_grid, (0, 0), colspan=4, rowspan=1)
    fig = analyzer.plot_temporal_distance_profile(format_string="%M",
                                                  plot_journeys=True,
                                                  lw=3,
                                                  ax=ax1,
                                                  plot_tdist_stats=True,
                                                  alpha=0.15,
                                                  plot_trip_stats=False,
                                                  duration_divider=60.0)

    ax2 = plt.subplot2grid(subplot_grid, (0, 4), colspan=2, rowspan=1)
    fig = analyzer.plot_temporal_distance_pdf_horizontal(use_minutes=True,
                                                         ax=ax2)

    ax2.set_ylabel("")
    ax2.set_yticks([])

    ax1.set_ylim(0, 11)
    ax2.set_ylim(0, 11)

    ax1.set_xlabel("Departure time $t_{\\text{dep}}$ (min)")
    ax1.set_ylabel("Temporal distance $\\tau$ (min)")

    handles, labels = ax1.get_legend_handles_labels()
    # legend_order = [4, 3, 0, 1, 2]
    # handles = [handles[order] for order in legend_order]
    # labels = [labels[order] for order in legend_order]
    ax1.legend(handles, labels, loc="lower center",
              fancybox=False, ncol=2, shadow=False, prop={'size': 10})
    fig.tight_layout()
    plt.subplots_adjust(wspace=0.34)
    fig.savefig(settings.RESULTS_DIRECTORY + "schematic_temporal_distance.pdf")
    plt.show()


def plot_transfer_profile():
    labels_raw = [
        (4, 14, 1),
        (4, 8, 2),
        (8, 8, 2),
        (10, 17, 1),
        (15, 27, 1),
        (15, 15, 2),
        (22, 14, 1),
        (22, 12, 2)
    ]
    for label in labels_raw:
        print(str(label[0]) + " & " + str(label[0] + label[1]) +
              " & " + str(label[1]) + " & " + str(label[2]) + " \\\\")

    labels = [
        LabelTimeWithBoardingsCount(departure_time=label[0],
                                    arrival_time_target=label[0] + label[1],
                                    n_boardings=label[2],
                                    first_leg_is_walk=False)
        for label in labels_raw
    ]

    dep_times = list(set(map(lambda el: el.departure_time, labels)))
    p = NodeProfileMultiObjective(dep_times=dep_times,
                                  walk_to_target_duration=30,
                                  label_class=LabelTimeWithBoardingsCount)

    for label in labels[::-1]:
        p.update([label])

    p.finalize()
    analyzer = NodeProfileAnalyzerTimeAndVehLegs(p, 0, 20)
    print(analyzer.mean_n_boardings_on_shortest_paths())

    fig = analyzer.plot_new_transfer_temporal_distance_profile(format_string="%S",
                                                               duration_divider=1,
                                                               default_lw=4)

    ax = fig.get_axes()[0]
    ax.set_xlabel("Departure time $t_{\text{dep}}$ (min)")
    ax.set_ylabel("Temporal distance $\tau$ (min)")
    fig.savefig(settings.RESULTS_DIRECTORY + "schematic_transfer_profile.pdf")
    plt.show()


if __name__ == "__main__":
    plot_plain_profile()
    # plot_transfer_profile()
