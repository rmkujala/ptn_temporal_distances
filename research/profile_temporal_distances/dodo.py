import os

import itertools
from doit.tools import run_once

# Get original data
# Transform data into connections + walk_network
# Run profiling code under code/
# Results can be found under results/
# Writings can be found under writings/

DATA_DIRECTORY = "data/"

CITIES = ["helsinki"]
DATES = ["2016-09-28"]


def task_copy_extracts():
    for city, date in itertools.product(CITIES, DATES):
        base_targets = ["main.day.transfers.csv", "main.day.nodes.csv", "main.day.temporal_network.csv"]
        city_date_data_directory = os.path.join(DATA_DIRECTORY, city, date)
        targets = [os.path.join(city_date_data_directory, target) for target in base_targets]
        yield {
            "name": city + "/" + date,
            "actions": ["mkdir -p " + os.path.join(DATA_DIRECTORY, city, date),
                        "scp "
                        "cswork:/m/cs/scratch/networks/rmkujala/transit/proc_test/" + city + "/" + date + "/*.csv" +
                        city_date_data_directory],
            "targets": targets,
            'uptodate': [run_once]
        }
