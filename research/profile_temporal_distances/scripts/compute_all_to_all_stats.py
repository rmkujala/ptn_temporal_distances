from __future__ import print_function

import sys

import pandas

from compute import compute_all_to_all_profile_statistics_with_defaults
from settings import HELSINKI_NODES_FNAME
from util import split_into_equal_length_parts



if __name__ == "__main__":
    _, slurm_array_i, slurm_array_length = sys.argv
    slurm_array_i = int(slurm_array_i)
    slurm_array_length = int(slurm_array_length)

    assert(slurm_array_i < slurm_array_length)
    nodes = pandas.read_csv(HELSINKI_NODES_FNAME)['stop_I'].values
    parts = split_into_equal_length_parts(nodes, slurm_array_length)
    targets = parts[slurm_array_i]

    compute_all_to_all_profile_statistics_with_defaults(targets)





