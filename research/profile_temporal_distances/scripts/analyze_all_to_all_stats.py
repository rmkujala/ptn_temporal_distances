import fnmatch
import pickle
import os

import matplotlib
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from scipy.stats import binned_statistic

from util import get_data_or_compute

import settings
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs

to_vectors = NodeProfileAnalyzerTimeAndVehLegs.all_measures_and_names_as_lists()
ALL_TO_ALL_STATS_DIR = os.path.join(settings.RESULTS_DIRECTORY, "all_to_all_stats")

from matplotlib import rc
rc('text', usetex=True)

"""
Code for plotting the all-to-all statistics.
See the main block (at the end) for an entry point to this script.
"""


def _get_raw_stats_filenames():
    filenames = [os.path.join(ALL_TO_ALL_STATS_DIR, fname)
                 for fname in os.listdir(ALL_TO_ALL_STATS_DIR)
                 if fnmatch.fnmatch(fname, "*all_to_all_stats_target_*.pkl")]
    filenames = list(sorted(filenames, key=lambda fname: (len(fname), fname)))
    return filenames


def compute_observable_name_matrix(observable_name, limit=None):
    fnames = _get_raw_stats_filenames()
    values = []
    if limit:
        fnames = fnames[:limit]
    for fname in fnames:
        print(fname)
        with open(fname, 'rb') as f:
            data = pickle.load(f)
            values.append(data['stats'][observable_name])
    return numpy.array(values)


def _plot_2d_pdf(xvalues, yvalues, xbins, ybins, aspect='equal', ax=None):
    histogram, xbins, ybins = numpy.histogram2d(xvalues, yvalues, bins=[xbins, ybins], normed=True)

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    histogram[histogram == 0] = float('nan')
    cmap = matplotlib.cm.get_cmap("viridis")  # afmhot
    cmap.set_bad("white", 1.)

    extent = [xbins[0], xbins[-1], ybins[0], ybins[-1]]
    im = ax.imshow(histogram.T, interpolation='nearest', origin='low',
                   extent=extent, cmap=cmap, aspect=aspect)

    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.set_label(r"Probability density", size=8)
    cbar.formatter.set_powerlimits((0, 0))
    cbar.ax.yaxis.set_offset_position('left')
    cbar.update_ticks()

    bin_centers, _, _ = binned_statistic(xvalues, xvalues, statistic='mean', bins=xbins)
    bin_averages, _, _ = binned_statistic(xvalues, yvalues, statistic='mean', bins=xbins)
    percentile_5, _, _ = binned_statistic(xvalues, yvalues, statistic=lambda values: numpy.percentile(values, 5),
                                          bins=xbins)
    percentile_95, _, _ = binned_statistic(xvalues, yvalues, statistic=lambda values: numpy.percentile(values, 95),
                                           bins=xbins)
    bin_stdevs, _, _ = binned_statistic(xvalues, yvalues, statistic='std', bins=xbins)
    ax.plot(bin_centers, bin_averages, ls="-", lw=3.0, color="#FF3EB6", alpha=0.8, label="mean")
    ax.plot(bin_centers, percentile_5, ls="--", lw=3.0, color="#FF3EB6", alpha=0.8, label="5th and 95th percentile")
    ax.plot(bin_centers, percentile_95, ls="--", lw=3.0, color="#FF3EB6", alpha=0.8)  # , label="95th percentile")
    # bin_medians, _, _ = binned_statistic(xvalues, yvalues, statistic='median', bins=xbins)
    # ax.plot(bin_centers, bin_medians, ls="--", color="green", label="median")
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 180)
    leg = ax.legend(loc="upper right", fancybox=True, prop={'size': 10})
    leg.get_frame().set_alpha(0.9)
    return ax


def _load_data():
    observables = [
        "min_temporal_distance",
        "mean_temporal_distance",
        "max_temporal_distance",
        "n_pareto_optimal_trips",
        "mean_n_boardings_on_shortest_paths",
        "min_n_boardings",
        "max_n_boardings_on_shortest_paths"
    ]

    observable_to_matrix = {}
    numpy.random.seed(seed=10)
    rands = numpy.unique(numpy.random.randint(1, 5000, size=100))
    for observable in observables:
        matrix = get_data_or_compute(
            os.path.join(ALL_TO_ALL_STATS_DIR, observable + "_matrix.pkl"),
            compute_observable_name_matrix,
            observable,
            recompute=False,
            limit=None
        )
        # Uncomment below for faster testing of this plotting script.
        # print("Taking only a small sample for faster plot development!")
        # matrix = matrix[rands]
        observable_to_matrix[observable] = matrix

    print("data loaded")

    mins_flattened = observable_to_matrix["min_temporal_distance"].flatten() / 60.0
    print("mins flattened")

    maxs_flattened = observable_to_matrix["max_temporal_distance"].flatten() / 60.0
    print("maxs flattened")

    means_flattened = observable_to_matrix["mean_temporal_distance"].flatten() / 60.0
    print("means flattened")

    n_trips_flattened = observable_to_matrix["n_pareto_optimal_trips"].flatten()
    print("n_trips flattened")

    mean_n_boardings_flattened = observable_to_matrix["mean_n_boardings_on_shortest_paths"].flatten()
    print("mean_n_boardings flattened")

    min_n_boardings_flattened = observable_to_matrix["min_n_boardings"].flatten()
    max_n_boardings_flattened = observable_to_matrix["max_n_boardings_on_shortest_paths"].flatten()

    time_bins = numpy.linspace(-0.5, 180.5, 182)

    combined_time_valids = numpy.ones(len(mins_flattened), dtype=bool)
    for arr in [mins_flattened, means_flattened, maxs_flattened]:
        time_valids = numpy.ones(len(mins_flattened), dtype=bool)
        time_valids *= (arr >= 0)
        time_valids *= (arr < float('inf'))
        combined_time_valids *= time_valids
        time_invalids = numpy.logical_not(time_valids)
        arr[time_invalids] = 240

    print("Filtered invalid time values")

    mins_flattened_time_valids = mins_flattened[combined_time_valids]
    maxs_flattened_time_valids = maxs_flattened[combined_time_valids]
    means_flattened_time_valids = means_flattened[combined_time_valids]
    mean_n_boardings_flattened_time_valids = mean_n_boardings_flattened[combined_time_valids]
    n_pareto_optimal_trips_flattened_time_valids = n_trips_flattened[combined_time_valids]
    min_n_boardings_flattened_time_valids = min_n_boardings_flattened[combined_time_valids]
    max_n_boardings_flattened_time_valids = max_n_boardings_flattened[combined_time_valids]

    flattened_time_valids = {}
    flattened_time_valids["min_temporal_distance"] = mins_flattened_time_valids
    flattened_time_valids["mean_temporal_distance"] = means_flattened_time_valids
    flattened_time_valids["max_temporal_distance"] = maxs_flattened_time_valids
    flattened_time_valids["mean_n_boardings_on_shortest_paths"] = mean_n_boardings_flattened_time_valids
    flattened_time_valids["n_pareto_optimal_trips"] = n_pareto_optimal_trips_flattened_time_valids
    flattened_time_valids["min_n_boardings"] = min_n_boardings_flattened_time_valids
    flattened_time_valids["max_n_boardings_on_shortest_paths"] = max_n_boardings_flattened_time_valids
    return time_bins, flattened_time_valids


def plot_mean_minus_min_vs_min(ax, mins, means, time_bins):
    _plot_2d_pdf(mins,
                 means - mins,
                 time_bins,
                 time_bins,
                 aspect='auto',
                 ax=ax)
    ax.set_ylabel("$\\tau_\\mathrm{mean} - \\tau_\\mathrm{min}$")
    ax.set_xlabel("$\\tau_\\mathrm{min}$")


def plot_mean_minus_min_per_min_vs_min(ax, mins, means, time_bins):
    valids_zero = mins > 0
    mins_now = mins[valids_zero]
    means_now = means[valids_zero]
    ax = _plot_2d_pdf(mins_now, (means_now - mins_now) / mins_now, time_bins,
                      numpy.linspace(0, 3, 100), aspect='auto', ax=ax)
    ax.set_ylabel("$(\\tau_\\mathrm{mean} - \\tau_\\mathrm{min}) / \\tau_\\mathrm{min}$")
    ax.set_xlabel("$\\tau_\\mathrm{min}$")
    ax.set_xlim([0, 120])
    ax.set_ylim([0, 2])


def plot_min_vs_n_pareto_optimal_journeys(ax, mins, journey_counts, time_bins):
    x_label = "$\\tau_\\mathrm{min}$"
    y_label = "$n_\\mathrm{journeys}$"
    max_n_trips = max(journey_counts)
    n_trip_bins = numpy.linspace(-0.5, max_n_trips + 0.5, max_n_trips + 2)
    ax = _plot_2d_pdf(mins,
                      journey_counts,
                      time_bins,
                      n_trip_bins,
                      aspect='auto',
                      ax=ax)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_xlim([0, 180])
    ax.set_ylim([0, max_n_trips])


def plot_min_vs_mean_n_boardings(ax, mins, mean_n_boardings, time_bins):
    ax = _plot_2d_pdf(mins,
                      mean_n_boardings,
                      time_bins,
                      numpy.linspace(0, max(mean_n_boardings), 50),
                      aspect='auto',
                      ax=ax)
    ax.set_xlabel("$\\tau_\\mathrm{min}$")
    ax.set_ylabel("$b_\\mathrm{mean\\,f.p.}$")
    ax.set_xlim([0, 180])
    ax.set_ylim([0, max(mean_n_boardings)])


def plot_min_tdist_pdf(ax, min_times, mean_times, max_times, time_bins):
    ax.set_xlabel("Temporal distance $\\tau$ (min)")
    ax.set_ylabel("Probability density $P(\\tau)$")
    ax.set_xlim([0, 180])
    orig_colors = [[237, 248, 177], [127, 205, 187], [44, 127, 184]][::-1]
    alphas = [1.0, 0.8, 0.6]  # [1.0, 0.7, 0.4]
    colors = [(r / 256., g / 256., b / 256, alpha) for (r, g, b), alpha in zip(orig_colors, alphas)]
    # colors = ['#edf8b1', '#7fcdbb', '#2c7fb8'][::-1]
    labels = ["$\\tau_\\mathrm{%s}$" % s for s in ["min", "mean", "max"]]
    for values, color, label, lw in zip([min_times, mean_times, max_times], colors, labels, [2, 1.5, 1.]):
        ax.hist(values,
                bins=time_bins,
                facecolor=color,
                edgecolor="k",
                histtype="stepfilled",
                normed=True,
                label=label,
                lw=lw)
    xfmt = ScalarFormatter()
    xfmt.set_powerlimits((-0, 0))
    ax.yaxis.set_major_formatter(xfmt)
    leg = ax.legend(loc="best", fancybox=True)
    leg.get_frame().set_alpha(0.9)


def plot_min_n_boardings_vs_mean_n_boardings(ax, min_nboardings, mean_n_boardings_fp):
    ax = _plot_2d_pdf(min_nboardings,
                      mean_n_boardings_fp - min_nboardings,
                      numpy.linspace(-0.5, 0.5 + numpy.round(max(mean_n_boardings_fp)),
                                     numpy.round(max(mean_n_boardings_fp)) + 2),
                      numpy.linspace(0, max(mean_n_boardings_fp), 50),
                      aspect='auto',
                      ax=ax)
    ax.set_xlabel("$b_\\mathrm{min}$")
    ax.set_ylabel("$b_\\mathrm{mean\\,f.p.}$")
    ax.set_xlim([-0.5, max(mean_n_boardings_fp)])
    ax.set_ylim([0, max(mean_n_boardings_fp)])


def plot_boarding_count_distributions(ax1, min_nboardings, mean_n_nboardings_fp, max_n_boardings_fp):
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    divider = make_axes_locatable(ax1)
    ax2 = divider.new_vertical(size="100%", pad=0.03, pack_start=True)
    ax3 = divider.new_vertical(size="100%", pad=0.03, pack_start=True)
    fig = ax1.get_figure()
    fig.add_axes(ax2)
    fig.add_axes(ax3)
    labels = ["$b_\\mathrm{%s}$" % s for s in ["min", "mean,f.p.", "max,f.p"]]

    orig_colors = [[237, 248, 177], [127, 205, 187], [44, 127, 184]][::-1]
    alphas = [1.0, 0.7, 1.0]
    colors = [(r / 256., g / 256., b / 256, alpha) for (r, g, b), alpha in zip(orig_colors, alphas)]

    max_n = max(max_n_boardings_fp)

    for i, (ax, values, color, label, lw) in enumerate(zip([ax1, ax2, ax3],
                                                           [min_nboardings, mean_n_nboardings_fp, max_n_boardings_fp],
                                                           colors,
                                                           labels,
                                                           [2, 1.5, 1.])):
        bins = numpy.linspace(-0.1, max_n + 0.1, max_n * 5 + 2)
        if i == 1:
            ax.hist(values,
                    bins=bins,
                    facecolor=color,
                    edgecolor="k",
                    histtype="stepfilled",
                    normed=True,
                    label=label,
                    lw=lw
                    )
        else:
            hist, bin_edges = numpy.histogram(values, bins)
            print(bin_edges)
            hist = hist / numpy.sum(hist)
            ax.bar(bin_edges[:-1], hist, width=bin_edges[1] - bin_edges[0], edgecolor="k", label=label, lw=lw,
                   facecolor=color)

        leg = ax.legend(loc="best", fancybox=True, prop={'size': 10})
        leg.get_frame().set_alpha(0.9)

    ax3.set_xlabel("Number of boardings $b$")
    for ax in [ax1, ax2, ax3]:
        ax.set_ylabel("$P(b)$")
        plt.sca(ax)
        plt.locator_params(nbins=3, axis="y")
        list(ax.get_yticklabels())[-1].set_visible(False)

        ax.set_xlim(-0.2, max_n + 0.2)

        if ax in [ax1, ax2]:
            for tl in ax.get_xticklabels():
                tl.set_visible(False)


if __name__ == "__main__":
    time_bins, flattened_time_valid_dict = _load_data()
    fig = plt.figure(figsize=(11, 5))
    plt.subplots_adjust(wspace=0.26, hspace=0.34, left=0.05, bottom=0.10, top=0.9, right=0.98, )

    ax1 = fig.add_subplot(2, 3, 1)
    plot_min_tdist_pdf(ax1,
                       flattened_time_valid_dict["min_temporal_distance"],
                       flattened_time_valid_dict["mean_temporal_distance"],
                       flattened_time_valid_dict["max_temporal_distance"],
                       time_bins[::3])
    print("finished ax1")

    ax2 = fig.add_subplot(2, 3, 2)
    plot_mean_minus_min_vs_min(ax2,
                               flattened_time_valid_dict["min_temporal_distance"],
                               flattened_time_valid_dict["mean_temporal_distance"],
                               time_bins
                               )
    ax2.set_xlim(0, 120)
    ax2.set_ylim(0, 80)
    print("finished ax2")

    ax3 = fig.add_subplot(2, 3, 3)
    plot_mean_minus_min_per_min_vs_min(ax3,
                                       flattened_time_valid_dict["min_temporal_distance"],
                                       flattened_time_valid_dict["mean_temporal_distance"],
                                       time_bins
                                       )
    ax3.set_xlim(0, 120)
    print("finished ax3")

    ax4 = fig.add_subplot(2, 3, 4)
    plot_boarding_count_distributions(ax4,
                                      flattened_time_valid_dict["min_n_boardings"],
                                      flattened_time_valid_dict["mean_n_boardings_on_shortest_paths"],
                                      flattened_time_valid_dict["max_n_boardings_on_shortest_paths"]
                                      )
    print("finished ax4")

    ax5 = fig.add_subplot(2, 3, 5)
    plot_min_vs_mean_n_boardings(ax5,
                                 flattened_time_valid_dict["min_temporal_distance"],
                                 flattened_time_valid_dict["mean_n_boardings_on_shortest_paths"],
                                 time_bins=time_bins)
    ax5.set_xlim(0, 120)
    print("finished ax5")

    ax6 = fig.add_subplot(2, 3, 6)
    plot_min_vs_n_pareto_optimal_journeys(ax6,
                                          flattened_time_valid_dict["min_temporal_distance"],
                                          flattened_time_valid_dict["n_pareto_optimal_trips"],
                                          time_bins=time_bins)
    ax6.set_xlim(0, 120)
    print("finished ax6")

    # Annotating each axes by a letter.
    for ax, letter in zip([ax1, ax2, ax3, ax4, ax5, ax6], "ABCDEF"):
        if ax is ax4:
            y = 0.85
        else:
            y = 0.94
        ax.text(0.04, y, "\\textbf{" + letter + "}",
                horizontalalignment="left",
                verticalalignment="top",
                transform=ax.transAxes,
                fontsize=12,
                color="black",
                backgroundcolor="white")

    fig.savefig(settings.FIGS_DIRECTORY + "all_to_all_stats.pdf")
    plt.show()
