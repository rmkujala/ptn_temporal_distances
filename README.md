## General
This repository contains the scripts (written in Python 3) used for producing the results for the manuscript:
"Travel times and transfers in public transport networks:
comprehensive accessibility analysis based on Pareto-optimal journeys"

### License
All scripts (under `scripts/`) are free to use in accordance with the MIT license.

### Acknowledgment
If you use these scripts, please cite our paper or give appropriate acknowledgement otherwise.
(Details on citing the paper will be added once the paper has been published.)

## Data
The data for running the analyses are provided under `data/`
The original source data (events and stops) for our analyses consitst of GTFS-data and OpenStreetMap extracts:
- The original GTFS data has been downloaded from the Reittiopas API (http://developer.reittiopas.fi/pages/en/other-apis.php)
- The OpenStreetMap data was downloaded from http://www.geofabrik.de/data/download.html (Open Database License 1.0.)
    (used for computing walking distances)

## Dependencies
The preprocessing of the source data, and all scripts in this repository use the gtfspy Python package (https://github.com/CxAalto/gtfspy), which is also included as an explicit git-submodule dependency in this repository.
Note that, since the creation/run of the analysis scripts in these repository, the gtfspy package has most likely improved / changed, and thus this repository should not be considered as a long-term model example how to work with `gtfspy`.
For introduction on how to use `gtfspy`, see the documentation in that package.

Moreover, the code in this repository is not necessarily compatible with the most recent version of the `gtfspy` package.
The only version of `gtfspy` package that these scripts are guaranteed to work with is the one accompanied with the git-submodule dependency.

Other (more standard) dependencies include:
- `smopy`  (https://github.com/rossant/smopy)
- `pandas`
- `numpy`
- `matplotlib`
- `Cython`
- `requests`

## Scripts

### Modules used by all / most analysis scripts
- `settings.py`
    - Shared settings for the analyses
- `compute.py`
    - Shared computation and caching pipelines for the analyses.
- `util.py`
    - Miscellanous shared utility functions.

### Analyzes
- `plot_one_day_example_profile.py`
    - Compute and plot one long (6AM-9PM) temporal distance profile augmented with boarding-counts.
- `plot_temporal_distance_profiles.py`
    - Compute and plot two examples of temporal distance profiles with and without boarding-count information.
- `plot_transfers_on_map.py`
    - Compute and plot boardings counts on a map.
- `temporal_distances_map.py`
    - Compute and plot temporal distance statistics on a map.
- `multiple_targets_fig.py`
    - Compute and plot mean temporal distance and mean number of transfers on fastest-paths towards multiple locations.

### All-to-all analyses
- `all_to_all_slurm.sh`
    - A script for submitting a batch job to Triton cluster (at Aalto University) for performing all-to-all analyses (calls `compute_all_to_all_stats.py`)
- `compute_all_to_all_stats.py`
    - A short script steering the all-to-all computations in Python
- `analyze_all_to_all_stats.py`
    - Analyze the results produced by compute_all_to_all_stats.py
- `slurm_submit_command.txt`
    - A reminder how to submit the batch job to Triton

### Other analyses
- `plot_temporal_distance_profiles_simple_verification.py`
    - Plot fastest-path temporal distance profiles using a simple profiler that only tracks time.
- `plot_profiles_on_a_map.py`
    - Old legacy code that was no longer used.

### Schematic plots
- `schematic_plots.py`
    - Plot schematic examples of temporal distance profiles.
- `schematic_temporal_network_image.py`
    - Plot a crude node-time diagram of a list of events.

## Author / Point of contact:
Rainer Kujala (Rainer.Kujala@gmail.com; @rmkujala)
