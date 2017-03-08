import numpy
from matplotlib import pyplot as plt
import pandas
import matplotlib
import matplotlib.cm
import matplotlib.colors
from matplotlib.axes import Axes
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable

from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from plot_profiles_on_a_map import _plot_smopy
from compute import get_node_profile_statistics
from settings import OTANIEMI_STOP_ID, HELSINKI_NODES_FNAME, FIGS_DIRECTORY

from matplotlib import rc
import os



rc("text", usetex=True)

caxs = []

targets = [OTANIEMI_STOP_ID]  # [115, 3063]  # kamppi, kilo
nodes = pandas.read_csv(HELSINKI_NODES_FNAME)
targets_info = nodes[nodes.stop_I.isin(targets)]
target_lats = targets_info['lat']
target_lons = targets_info['lon']

data = get_node_profile_statistics(targets, recompute=True, recompute_profiles=True)
observable_name_to_data = data

min_n_boardings = numpy.array(data["min_n_boardings"])
mean_n_boardings = numpy.array(data["mean_n_boardings_on_shortest_paths"])
max_n_boardings = numpy.array(data["max_n_boardings_on_shortest_paths"])
journey_counts = numpy.array(data["n_pareto_optimal_trips"])
mean_temporal_distance_with_min_n_boardings = numpy.array(data["mean_temporal_distance_with_min_n_boardings"])
mean_temporal_distances = numpy.array(data["mean_temporal_distance"])

assert (len(journey_counts) == len(nodes))

observable_name_to_data["mean_minus_min_transfers"] = mean_n_boardings - min_n_boardings

smopy_fig = plt.figure(figsize=(11, 6))
plt.subplots_adjust(hspace=0.1, top=0.95, bottom=0.01, left=0.03, right=0.97)

gs0 = gridspec.GridSpec(9, 1, hspace=1.4)
gs00 = gridspec.GridSpecFromSubplotSpec(1, 10, subplot_spec=gs0[0:4], wspace=0.0)
gs01 = gridspec.GridSpecFromSubplotSpec(1, 25, subplot_spec=gs0[4:])
_i_to_ax = {
    0: plt.subplot(gs00[0, 0:3]),
    1: plt.subplot(gs00[0, 3:6]),
    2: plt.subplot(gs00[0, 6:9]),
    5: smopy_fig.add_axes([0.897, 0.575, 0.03, 0.365]),
    3: plt.subplot(gs01[0, 0:11]),
    4: plt.subplot(gs01[0, 13:24])
}

max_n_boardings = 5
cmap = NodeProfileAnalyzerTimeAndVehLegs.get_colormap_for_boardings(max_n_boardings)
norm = matplotlib.colors.Normalize(vmin=0, vmax=max_n_boardings)
sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([norm.vmin, norm.vmax])

titles = [
    "Min. boardings, $b_\\mathrm{min}$",
    "Mean boardings on f. p., $b_\\mathrm{mean\\,f.p.}$",
    "Max. boardings on f. p., $b_\\mathrm{max\\,f.p.}$"
]

observable_names_to_plot = ["min_n_boardings",
                            "mean_n_boardings_on_shortest_paths",
                            "max_n_boardings_on_shortest_paths"]

for i, (observable_name, title) in enumerate(zip(observable_names_to_plot, titles)):
    print(observable_name)
    observable_values = observable_name_to_data[observable_name]
    # set up colors

    observable_values = numpy.array(observable_values)

    nans = numpy.isnan(observable_values)
    observable_values[nans] = float('inf')
    observable_values_to_plot = observable_values

    lats = nodes['lat']
    lons = nodes['lon']
    zipped = list(zip(observable_values_to_plot, lats, lons,
                      [str(node) for node in nodes['desc']]))
    zipped = sorted(zipped)
    if "minus" not in observable_name:
        zipped = reversed(zipped)
    observable_values_to_plot, lats, lons, node_desc = zip(*zipped)
    observable_values_to_plot = numpy.array(observable_values_to_plot)
    lats = numpy.array(lats)
    lons = numpy.array(lons)

    _plot_smopy(lats, lons, observable_values_to_plot,
                title, sm, None, node_desc,
                ax=_i_to_ax[i], target_lats=target_lats, target_lons=target_lons, target_marker_color="blue")

# cax = _get_subplot(4)
cax = _i_to_ax[5]
caxs.append(cax)
cbar = smopy_fig.colorbar(sm, cax=cax, orientation="vertical", label="Number of boardings")
cbar.set_ticks(range(0, max_n_boardings + 1))

# DIFFERENCES IN BOARDING COUNTS (mean-min)
##################################################
cmap = matplotlib.cm.get_cmap(name="viridis", lut=None)  # prism, viridis_r
norm = matplotlib.colors.Normalize(vmin=0, vmax=2)  # 3.5)
sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([norm.vmin, norm.vmax])
mean_minus_min = numpy.array(observable_name_to_data["mean_minus_min_transfers"])
print(max(mean_minus_min[mean_minus_min < float('inf')]))

nans = numpy.isnan(mean_minus_min)
mean_minus_min[nans] = float('inf')
lats = list(nodes['lat'])
lons = list(nodes['lon'])
assert (len(mean_minus_min) == len(lats))
zipped = list(zip(mean_minus_min,
                  list(lats),
                  list(lons),
                  [str(node) for node in nodes['desc']]))
zipped = list((sorted(zipped)))
observable_values_to_plot, lats, lons, node_desc = zip(*zipped)
observable_values_to_plot = numpy.array(observable_values_to_plot)
lats = numpy.array(lats)
lons = numpy.array(lons)
ax = _plot_smopy(lats, lons, observable_values_to_plot, "", sm, None, node_desc, ax=_i_to_ax[3], s=6,
                 target_lats=target_lats, target_lons=target_lons)

ax = _i_to_ax[3]
ax.set_title("Difference, $b_\\mathrm{mean\\,f.p.}-b_\\mathrm{min}$")
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="10%", pad=0.1)
caxs.append(cax)
cbar = smopy_fig.colorbar(sm, cax=cax, orientation="vertical")

# NUMBER OF JOURNEYS OR ( mean_temporal_distance_with_min_n_boardings - mean_temporal_distance)
##################################################

journeys_instead_of_time_diff = False
if journeys_instead_of_time_diff:
    cmap = matplotlib.cm.get_cmap(name="viridis", lut=None)  # prism, viridis_r
    norm = matplotlib.colors.Normalize(vmin=0, vmax=30)
    sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([norm.vmin, norm.vmax])
    n_journeys = numpy.array(observable_name_to_data["n_pareto_optimal_trips"])
    print("Max n journeys", n_journeys.max())

    lats = list(nodes['lat'])
    lons = list(nodes['lon'])
    assert (len(mean_minus_min) == len(lats))
    zipped = list(zip(n_journeys,
                      list(lats),
                      list(lons),
                      [str(node) for node in nodes['desc']]))
    zipped = list((sorted(zipped)))
    observable_values_to_plot, lats, lons, node_desc = zip(*zipped)
    observable_values_to_plot = numpy.array(observable_values_to_plot)
    lats = numpy.array(lats)
    lons = numpy.array(lons)
    ax = _plot_smopy(lats, lons, observable_values_to_plot, "", sm, None, node_desc, ax=_i_to_ax[4], s=6,
                     target_lats=target_lats, target_lons=target_lons)

    ax = _i_to_ax[4]
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="10%", pad=0.1)
    caxs.append(cax)
    ax.set_title("Number of alternative journeys, $n_\\mathrm{journeys}$")
    cbar = smopy_fig.colorbar(sm,
                              cax=cax,
                              orientation="vertical")
else:
    #### mean_temporal_distance_with_min_n_boardings - mean_temporal_distance
    ##########################################################################
    cmap = matplotlib.cm.get_cmap(name="viridis", lut=None)  # prism, viridis_r
    max = 20
    norm = matplotlib.colors.Normalize(vmin=0, vmax=max)
    sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([norm.vmin, norm.vmax])
    difference = (mean_temporal_distance_with_min_n_boardings - mean_temporal_distances)
    # / (mean_n_boardings - min_n_boardings)
    difference /= 60.0

    difference[difference > max] = max

    lats = list(nodes['lat'])
    lons = list(nodes['lon'])
    assert (len(difference) == len(lats))
    zipped = list(zip(difference,
                      list(lats),
                      list(lons),
                      [str(node) for node in nodes['desc']]))
    zipped = list((sorted(zipped)))
    observable_values_to_plot, lats, lons, node_desc = zip(*zipped)
    observable_values_to_plot = numpy.array(observable_values_to_plot)
    lats = numpy.array(lats)
    lons = numpy.array(lons)
    ax = _plot_smopy(lats, lons, observable_values_to_plot, "", sm, None, node_desc, ax=_i_to_ax[4], s=6,
                     target_lats=target_lats, target_lons=target_lons
                     )

    ax = _i_to_ax[4]
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="10%", pad=0.1)
    caxs.append(cax)
    ax.set_title("Difference, $\\tau_\\mathrm{mean} - \\tau_\\mathrm{mean,min. b}$")
    cbar = smopy_fig.colorbar(sm, cax=cax,
                              orientation="vertical", label="minutes")

for i, letter in zip(range(5), "ABCDE"):
    ax = _i_to_ax[i]
    ax.text(0.04, 0.96, "\\textbf{" + letter + "}",
            horizontalalignment="left",
            verticalalignment="top",
            transform=ax.transAxes,
            fontsize=15,
            color="white")

for cax in caxs:
    yticklabels = cax.get_yticklabels()
    last_label = yticklabels[-1]
    last_label.set_text(u"$\\geq$ " + last_label.get_text())
    yticklabels[-1] = last_label
    cax.set_yticklabels(yticklabels)

plt.show()
smopy_fig.savefig(os.path.join(FIGS_DIRECTORY, "transfers_on_map.pdf"))
