import numpy
from matplotlib import pyplot as plt
import pandas
import matplotlib
import matplotlib.cm
import matplotlib.colors
from matplotlib.axes import Axes
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable

from plot_profiles_on_a_map import _plot_smopy
from compute import get_node_profile_statistics
from settings import OTANIEMI_STOP_ID, HELSINKI_NODES_FNAME, FIGS_DIRECTORY

from matplotlib import rc
import os

rc("text", usetex=True)

targets = [OTANIEMI_STOP_ID]  # [115, 3063]  # kamppi, kilo
nodes = pandas.read_csv(HELSINKI_NODES_FNAME)
print(len(nodes))
data = get_node_profile_statistics(targets, recompute=False, recompute_profiles=False)
observable_name_to_data = data
min_temporal_distances = numpy.array(data["min_temporal_distance"])
mean_temporal_distances = numpy.array(data["mean_temporal_distance"])
max_temporal_distances = numpy.array(data["max_temporal_distance"])
print(list(sorted(numpy.unique(numpy.ceil(max_temporal_distances / 60.0)))))
print(len(min_temporal_distances))
assert (len(min_temporal_distances) == len(nodes))

observable_name_to_data["mean_minus_min_temporal_distance"] = mean_temporal_distances - min_temporal_distances
observable_name_to_data["mean_minus_min_per_min"] = (
                                                        mean_temporal_distances - min_temporal_distances) / min_temporal_distances

print("Producing figures")
smopy_fig = plt.figure(figsize=(11, 6))
plt.subplots_adjust(hspace=0.1, top=0.95, bottom=0.01, left=0.03, right=0.97)

gs0 = gridspec.GridSpec(9, 1, hspace=1.4)
gs00 = gridspec.GridSpecFromSubplotSpec(1, 10, subplot_spec=gs0[0:4], wspace=0.0)
gs01 = gridspec.GridSpecFromSubplotSpec(1, 25, subplot_spec=gs0[4:])
_i_to_ax = {
    0: plt.subplot(gs00[0, 0:3]),
    1: plt.subplot(gs00[0, 3:6]),
    2: plt.subplot(gs00[0, 6:9]),
    5: smopy_fig.add_axes([0.89, 0.575, 0.03, 0.365]),
    3: plt.subplot(gs01[0, 0:11]),
    4: plt.subplot(gs01[0, 13:24])
}

# plot temporal distances
cmap = matplotlib.cm.get_cmap(name="inferno_r", lut=None)  # prism, viridis_r
norm = matplotlib.colors.Normalize(vmin=0, vmax=80)
sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([norm.vmin, norm.vmax])
observable_names = ["min_temporal_distance",
                    "mean_temporal_distance",
                    "max_temporal_distance"]

titles = [
    "Minimum temporal distance, $\\tau_\\mathrm{min}$",
    "Mean temporal distance, $\\tau_\\mathrm{mean}$",
    "Maximum temporal distance, $\\tau_\\mathrm{max}$"
]

for i, observable_name, title in zip(range(3), observable_names, titles):
    observable_values = numpy.array(observable_name_to_data[observable_name])
    nans = numpy.isnan(observable_values)
    observable_values[nans] = float('inf')
    observable_values_to_plot = observable_values / 60.0
    lats = list(nodes['lat'])
    lons = list(nodes['lon'])

    assert (len(observable_values_to_plot) == len(lats))
    zipped = list(zip(observable_values_to_plot,
                      list(lats),
                      list(lons),
                      [str(node) for node in nodes['desc']]))
    zipped = list(reversed(sorted(zipped)))
    observable_values_to_plot, lats, lons, node_desc = zip(*zipped)
    observable_values_to_plot = numpy.array(observable_values_to_plot)
    lats = numpy.array(lats)
    lons = numpy.array(lons)

    print(observable_values_to_plot)
    _plot_smopy(lats, lons, observable_values_to_plot,
                title, sm, None, node_desc, ax=_i_to_ax[i], s=6)

cax = _i_to_ax[5]
cbar = smopy_fig.colorbar(sm, cax=cax, orientation="vertical", label="minutes")

# DIFFERENCES
##################################################
cmap = matplotlib.cm.get_cmap(name="viridis", lut=None)  # prism, viridis_r
norm = matplotlib.colors.Normalize(vmin=0, vmax=30)
sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([norm.vmin, norm.vmax])
mean_minus_min = numpy.array(observable_name_to_data["mean_minus_min_temporal_distance"])
nans = numpy.isnan(mean_minus_min)
mean_minus_min[nans] = float('inf')
mean_minus_min /= 60.0
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
ax = _plot_smopy(lats, lons, observable_values_to_plot, "", sm, None, node_desc, ax=_i_to_ax[3], s=6)
smopy_fig.savefig('/tmp/tmp.pdf')
print(ax.get_position())

ax = _i_to_ax[3]
ax.set_title("Difference, $\\tau_\\mathrm{mean}-\\tau_\\mathrm{min}$")
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="10%", pad=0.1)
cbar = smopy_fig.colorbar(sm, cax=cax, orientation="vertical", label="minutes")

# RELATIVE DIFFERENCES
##################################################

cmap = matplotlib.cm.get_cmap(name="viridis", lut=None)  # prism, viridis_r
norm = matplotlib.colors.Normalize(vmin=0, vmax=1)
sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([norm.vmin, norm.vmax])
mean_minus_min = numpy.array(observable_name_to_data["mean_minus_min_per_min"])
nans = numpy.isnan(mean_minus_min)
mean_minus_min[nans] = 0
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
ax = _plot_smopy(lats, lons, observable_values_to_plot, "", sm, None, node_desc, ax=_i_to_ax[4], s=6)

ax = _i_to_ax[4]
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="10%", pad=0.1)
ax.set_title("Relative difference, $(\\tau_\\mathrm{mean}-\\tau_\\mathrm{min}) / \\tau_\\mathrm{min}$")
cbar = smopy_fig.colorbar(sm, cax=cax,
                          orientation="vertical")  # , label="$(\\tau_\\mathrm{mean}-\\tau_\\mathrm{min}) / \\tau_\\mathrm{min}$")

for i, letter in zip(range(5), "ABCDE"):
    ax = _i_to_ax[i]
    ax.text(0.04, 0.96, "\\textbf{" + letter + "}",
            horizontalalignment="left",
            verticalalignment="top",
            transform=ax.transAxes,
            fontsize=15,
            color="white")

smopy_fig.savefig(os.path.join(FIGS_DIRECTORY, "temporal_distances_on_map.pdf"))

print(ax.get_position())
