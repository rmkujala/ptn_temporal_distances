import fnmatch
import pickle
import os

import matplotlib
import numpy
import seaborn as sns
import matplotlib.pyplot as plt
import time

from util import get_data_or_compute

import settings
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs

to_vectors = NodeProfileAnalyzerTimeAndVehLegs.all_measures_and_names_as_lists()
ALL_TO_ALL_STATS_DIR = os.path.join(settings.RESULTS_DIRECTORY, "all_to_all_stats")


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




observables = [
    "min_temporal_distance",
    # "mean_temporal_distance",
    "max_temporal_distance",
    # "n_pareto_optimal_trips",
    # "mean_n_boardings_on_shortest_paths"
]

observable_to_matrix = {}
for observable in observables:
    matrix = get_data_or_compute(
        os.path.join(ALL_TO_ALL_STATS_DIR, observable + "_matrix.pkl"),
        compute_observable_name_matrix,
        observable,
        recompute=True,
        limit=5
    )
    observable_to_matrix[observable] = matrix



if True:
    # mean vs. min:
    bins = numpy.linspace(-0.5, 180.5, 182)
    mins = observable_to_matrix["min_temporal_distance"].flatten() / 60.0
    print(numpy.unique(numpy.ceil(mins)))

    # maxs = observable_to_matrix["max_temporal_distance"].flatten() / 60.0
    # means = observable_to_matrix["mean_temporal_distance"].flatten() / 60.0

    print(bins)
    # for ar in [mins]:
    #     hist, edges = numpy.histogram(ar[ar < 180], bins=bins)
    #     print(hist[:20])
    #     print(numpy.nonzero(hist < 0.5))


    # plt.hist2d(mins[valids], maxs[valids], bins=181, normed=True)
    # plt.grid(False)
    # plt.show()

    #
    #
    # histogram, xbins, ybins = numpy.histogram2d(mins, maxs, bins=[bins, bins], normed=True)
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    #
    #
    # histogram[histogram == 0] = float('nan')
    # masked_histogram = numpy.ma.array(histogram, mask=numpy.isnan(histogram))
    # cmap = matplotlib.cm.get_cmap("afmhot")
    # cmap.set_bad("white", 1.)
    # im = plt.imshow(histogram.T, interpolation='nearest', origin='low',
    #                 extent=[xbins[0], xbins[-1], ybins[0], ybins[-1]], cmap=cmap)
    #
    # fig.colorbar(im, ax=ax)
    # ax.plot([0, 180], [0, 180], color="r")
    # ax.set_xlim(0, 180)
    # ax.set_ylim(0, 180)
    # plt.show()

