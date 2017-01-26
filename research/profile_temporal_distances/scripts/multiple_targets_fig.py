import matplotlib
import numpy
import requests
import os

from matplotlib import gridspec
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from matplotlib.axes import Axes
import pandas

from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from plot_profiles_on_a_map import _plot_smopy
from settings import RESULTS_DIRECTORY, FIGS_DIRECTORY

from gtfspy.util import wgs84_distance
from util import get_data_or_compute, _get_smopy_map

from settings import HELSINKI_NODES_FNAME

from matplotlib import rc
rc("text", usetex=True)

recompute_all = False


def get_swimming_halls():
    url = "http://www.hel.fi/palvelukarttaws/rest/v2/unit/?service=33462"
    print("fetching data from " + url)
    r = requests.get(url)
    data = r.json()
    return data


def plot_smopy(lats, lons, observable_values_in_minutes,
               observable_name, scalar_mappable,
               basename, node_names,
               ax=None):

    if ax is None:
        fig = plt.figure()  # figsize=(12, 8), dpi=300)
        ax = fig.add_subplot(111)

    smopy_map = _get_smopy_map(numpy.percentile(lats, 100 - 98),
                               numpy.percentile(lats, 100 - 6),
                               numpy.percentile(lons, 5),
                               numpy.percentile(lons, 95),
                               z=10)
    ax = smopy_map.show_mpl(figsize=(12, 8), ax=ax, alpha=0.8)
    xs, ys = smopy_map.to_pixels(lats, lons)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_xlim(numpy.percentile(xs, 5), numpy.percentile(xs, 95))
    ax.set_ylim(numpy.percentile(ys, 98), numpy.percentile(ys, 6))

    colors = scalar_mappable.to_rgba(observable_values_in_minutes)

    assert (isinstance(ax, matplotlib.axes.Axes))
    valids = observable_values_in_minutes < float('inf')
    ax.scatter(xs[valids], ys[valids], c=colors[valids], edgecolors=colors[valids], s=12)
    ax.set_title(observable_name)
    return ax

use_swimming_halls = False

if use_swimming_halls:
    fname = os.path.join(RESULTS_DIRECTORY, "swimming_halls_json.pickle")
    target_locations = get_data_or_compute(fname, get_swimming_halls)
    fname_postfix = "swimming_halls"
else:
    helsinki_railway_station = {"latitude": 60.171861, "longitude": 24.941415}
    pasila_railway_station = {"latitude": 60.198889, "longitude": 24.933358}
    tikkurila_railway_station = {"latitude": 60.292471, "longitude": 25.044091}
    target_locations = [helsinki_railway_station, pasila_railway_station, tikkurila_railway_station]
    fname_postfix = "train_stations"

closest_stops_fname = os.path.join(RESULTS_DIRECTORY, "multiple_targets_closest_nodes_" + fname_postfix + ".pickle")

# with open("/Users/rmkujala/Desktop/uimahallit.csv", 'w') as f:
#     f.write("name,lat, lon\n")
#     for swimming_hall in swimming_halls:
#         f.write(str(swimming_hall['name_en']) + "," + str(swimming_hall['latitude']) + "," + str(swimming_hall['longitude']) + "\n")



def get_closest_nodes():
    closest_stops = []
    nodes = pandas.read_csv(HELSINKI_NODES_FNAME)
    for swimming_hall in target_locations:
        swimming_hall_lat = swimming_hall['latitude']
        swimming_hall_lon = swimming_hall['longitude']
        min_distance = float('inf')
        min_node = None
        for node in nodes.itertuples():
            distance = wgs84_distance(swimming_hall_lat, swimming_hall_lon, node.lat, node.lon)
            if distance < min_distance:
                min_distance = distance
                min_node = node
        closest_stops.append(min_node.stop_I)
    return closest_stops


closest_stop_Is = get_data_or_compute(closest_stops_fname, get_closest_nodes, recompute=recompute_all)

targets = closest_stop_Is

from compute import _compute_profile_data, __compute_profile_stats_from_profiles

kwargs_for_computations = {
    "targets": targets,
    "track_vehicle_legs": True,
    "track_time": True
}

profile_data_fname = os.path.join(RESULTS_DIRECTORY, "profiles_targets_multiple_targets_" + fname_postfix + ".pickle")
profiles = get_data_or_compute(profile_data_fname, _compute_profile_data, recompute=recompute_all,
                               **kwargs_for_computations)['profiles']

profile_data_fname = os.path.join(RESULTS_DIRECTORY, "profile_stats_multiple_targets_" + fname_postfix + ".pickle")
profile_statistics = get_data_or_compute(profile_data_fname, __compute_profile_stats_from_profiles,
                                         profiles, recompute=recompute_all)

observables_to_plot = ["mean_temporal_distance", "mean_n_boardings_on_shortest_paths"]
boardings_data = numpy.array(profile_statistics["mean_n_boardings_on_shortest_paths"])
max_n_boardings = max(boardings_data[boardings_data < float('inf')])
max_n_boardings = min(5, max_n_boardings)

colormap_lims = [(0, 60), (0, max_n_boardings)]
labels = [r"Mean temporal distance $\tau_\mathrm{mean}$ (min)",
          r"Mean number of boardings $b_\mathrm{mean\,\,f.p.}$"]
colormaps = [
    cm.get_cmap(name="inferno_r", lut=None),
    NodeProfileAnalyzerTimeAndVehLegs.get_colormap_for_boardings(max_n_boardings=max_n_boardings)
]
gs1 = gridspec.GridSpec(1, 5)
gs1.update(left=0.01, right=0.45, wspace=0.15, bottom=0.05)
gs2 = gridspec.GridSpec(1, 5)
gs2.update(left=0.51, right=0.95, wspace=0.15, bottom=0.05)
gridspecs = [gs1, gs2]

fig = plt.figure(figsize=(12, 5))
axs = [plt.subplot(gs1[:, :4]), plt.subplot(gs2[:, :4])]
caxs = [plt.subplot(gs1[:, 4:]), plt.subplot(gs2[:, 4:])]

nodes = pandas.read_csv(HELSINKI_NODES_FNAME)
lats = nodes['lat'].values
lons = nodes['lon'].values


for i, (observable, lims, title, cmap, ax, cax) in enumerate(
        zip(observables_to_plot, colormap_lims, labels, colormaps, axs, caxs)):
    norm = Normalize(vmin=lims[0], vmax=lims[1])
    sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([norm.vmin, norm.vmax])

    values = numpy.array(profile_statistics[observable])
    to_sort = values.argsort()[::-1]

    if numpy.median(values) > 10:
        values /= 60.0

    target_lats = numpy.array([t['latitude'] for t in target_locations])
    target_lons = numpy.array([t['longitude'] for t in target_locations])
    _, smopy_map = _plot_smopy(lats[to_sort], lons[to_sort], values[to_sort],
                None, sm, None, None, ax=ax, return_smopy_map=True,
                               target_lats=target_lats, target_lons=target_lons,
                               target_marker_color="blue",
                               target_marker_width=2.5,
                               target_marker_size=8)


    if i == 1:
        ticks = list(range(int(max_n_boardings)))
    else:
        ticks = None

    cbar = fig.colorbar(sm, cax=cax, orientation="vertical",
                        label=title, ticks=ticks)

fig.savefig(os.path.join(RESULTS_DIRECTORY, "multiple_targets.pdf"))

for ax, cax, letter in zip(axs, caxs, "ABCDE"):
    ax0, ay0, aw1, ah1 = ax.get_position().bounds
    cx0, cy0, cw1, ch1 = cax.get_position().bounds
    print(cx0, ay0, cw1, ah1)
    cax.set_position([cx0, ay0, (cw1) / 2., ah1])
    ax.text(0.04, 0.96, "\\textbf{" + letter + "}",
            horizontalalignment="left",
            verticalalignment="top",
            transform=ax.transAxes,
            fontsize=15,
            color="white")

fig.savefig(os.path.join(FIGS_DIRECTORY, "multiple_targets_" + fname_postfix + ".pdf"))
plt.show()

