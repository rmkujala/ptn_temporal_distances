from __future__ import print_function

import os
import fnmatch
import pickle

import numpy
import pandas

import seaborn as sns
import matplotlib.pyplot as plt

from compute import compute_all_to_all_profile_statistics_with_defaults
from settings import RESULTS_DIRECTORY, HELSINKI_NODES_FNAME
from util import run_in_parallel


def analyze():
    filenames = [os.path.join(RESULTS_DIRECTORY, fname)
                 for fname in os.listdir(RESULTS_DIRECTORY)
                 if fnmatch.fnmatch(fname, "*all_to_all_stats_target_*.pkl")]
    filenames = list(sorted(filenames, key=lambda fname: (len(fname), fname)))

    min_temporal_distances = []
    mean_temporal_distances = []
    max_temporal_distances = []

    for fname in filenames[0:7]:
        print(fname)
        with open(fname, 'rb') as f:
            data = pickle.load(f)
            stats = data['stats']
            for el in stats["min_temporal_distance"]:
                if not numpy.isnan(el) and not numpy.isinf(el) and el < 0:
                    print("negative values in ", fname, data['target'])
                    break


            min_temporal_distances.extend(list(stats["min_temporal_distance"]))
            mean_temporal_distances.extend(list(stats["mean_temporal_distance"]))
            max_temporal_distances.extend(list(stats["max_temporal_distance"]))


    min_temporal_distances = numpy.array(min_temporal_distances)
    mean_temporal_distances = numpy.array(mean_temporal_distances)
    max_temporal_distances = numpy.array(max_temporal_distances)
    for array in [min_temporal_distances, mean_temporal_distances, max_temporal_distances]:
        array[numpy.isnan(array)] = 180 * 60
        array[numpy.isinf(array)] = 180 * 60
        try:
            assert (array >= 0).all()
        except AssertionError as e:
            print(array[array < 0])
        array /= 60.0
    sns.jointplot(min_temporal_distances, mean_temporal_distances, kind="hex", color="#4CB391")
    sns.jointplot(mean_temporal_distances, max_temporal_distances, kind="hex", color="orange")
    sns.jointplot(min_temporal_distances, max_temporal_distances, kind="hex", color="red")
    plt.show()


def chunk_a_list(list, chunksize):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(list), chunksize):
        yield list[i:i + chunksize]


if __name__ == "__main__":
    nodes = pandas.read_csv(HELSINKI_NODES_FNAME)['stop_I'].values
    args = list(chunk_a_list(nodes, 20))
    run_in_parallel(compute_all_to_all_profile_statistics_with_defaults, args, 4)

    # compute_all_to_all_profile_statistics_with_defaults()
    # analyze()



