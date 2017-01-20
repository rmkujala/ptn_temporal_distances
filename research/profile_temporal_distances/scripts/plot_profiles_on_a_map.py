import matplotlib
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt
import mplleaflet
import numpy
import smopy

from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from util import _get_smopy_map

smopy.TILE_SERVER = "http://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
# smopy.TILE_SERVER = "http://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"

import folium

import pandas
from jinja2 import Template

from compute import get_node_profile_statistics, target_list_to_str

from jinja2.environment import Environment
from settings import HELSINKI_NODES_FNAME, DARK_TILES
from settings import RESULTS_DIRECTORY
from settings import OTANIEMI_STOP_ID








def plot_temporal_distances():
    # old code here to plot plenty of stuff
    targets = [OTANIEMI_STOP_ID]  # [115, 3063]  # kamppi, kilo
    nodes = pandas.read_csv(HELSINKI_NODES_FNAME)
    data = get_node_profile_statistics(targets, recompute=True, recompute_profiles=False)
    observable_name_to_data = data


    min_temporal_distances = numpy.array(data["min_temporal_distance"])
    mean_temporal_distances = numpy.array(data["mean_temporal_distance"])
    max_temporal_distances = numpy.array(data["max_temporal_distance"])
    observable_name_to_data["max_minus_min_temporal_distance"] = max_temporal_distances - min_temporal_distances
    observable_name_to_data["max_minus_mean_temporal_distance"] = max_temporal_distances - mean_temporal_distances
    observable_name_to_data["mean_minus_min_temporal_distance"] = mean_temporal_distances - min_temporal_distances
    observable_name_to_data["mean_minus_min_temporal_distance"] = mean_temporal_distances - min_temporal_distances
    observable_name_to_data["mean_minus_mean_min_n_boardings"] = numpy.array(observable_name_to_data["mean_temporal_distance_with_min_n_boardings"]) - mean_temporal_distances
    observable_name_to_data["min_minus_min_min_n_boardings"] = numpy.array(observable_name_to_data["min_temporal_distance_with_min_n_boardings"]) - min_temporal_distances
    observable_name_to_data["max_minus_min_per_min"] = (max_temporal_distances - min_temporal_distances) / min_temporal_distances
    observable_name_to_data["mean_minus_min_per_min"] = (mean_temporal_distances - min_temporal_distances) / min_temporal_distances
    observable_name_to_data["max_minus_min_per_min_per_mean_minus_min"] = (max_temporal_distances - min_temporal_distances) / (mean_temporal_distances - min_temporal_distances)


    print("Producing figures")
    basename = RESULTS_DIRECTORY + "/helsinki_test_" + target_list_to_str(targets) + "_"
    observable_names = sorted(list(observable_name_to_data.keys()))
    observable_names = ["min_temporal_distance",
                        "min_temporal_distance_with_min_n_boardings",
                        "mean_temporal_distance",
                        "mean_temporal_distance_with_min_n_boardings",
                        "min_minus_min_min_n_boardings",
                        "mean_minus_mean_min_n_boardings",
                        "max_temporal_distance",
                        "mean_minus_min_temporal_distance",
                        "max_minus_min_temporal_distance",
                        "max_minus_mean_temporal_distance",
                        "mean_minus_min_per_min", "max_minus_min_per_min",
                        # "max_minus_min_per_min_per_mean_minus_min",
                        ]
    # observable_names = ["min_temporal_distance",
    #                     "mean_temporal_distance",
    #                     "max_temporal_distance",
    #                     "mean_minus_min_temporal_distance",
    #                     "max_minus_min_temporal_distance",
    #                     "max_minus_mean_temporal_distance"
    #                     ]
    smopy_fig = plt.figure(figsize=(15, 10))  # , dpi=300)
    # smopy_fig.tight_layout()
    plt.subplots_adjust(hspace=0.05, top=0.99, bottom=0.01, left=0.01, right=0.99, wspace=0.01)

    for i, observable_name in enumerate(observable_names):
        print(observable_name)
        observable_values = observable_name_to_data[observable_name]
        # set up colors
        cmap = matplotlib.cm.get_cmap(name="plasma_r", lut=None)  # prism, viridis_r
        if observable_name == "pareto":
            observable_values_to_plot = observable_values
            norm = matplotlib.colors.Normalize(vmin=0, vmax=max(observable_values))
        elif "relative" in observable_name:
            observable_values = numpy.array(observable_values)
            nans = numpy.isnan(observable_values)
            observable_values[nans] = float('inf')
            observable_values_to_plot = observable_values
            norm = matplotlib.colors.Normalize(vmin=0, vmax=1)
            cmap = matplotlib.cm.get_cmap(name="viridis", lut=None)  # prism, viridis_r
        elif "minus" in observable_name:
            observable_values = numpy.array(observable_values)
            new_max = 7  # numpy.nanmax(observable_values[observable_values < float('inf')]) + 0.5
            nans = numpy.isnan(observable_values)
            observable_values[nans] = float('inf')
            observable_values_to_plot = observable_values / 60.0
            norm = matplotlib.colors.Normalize(vmin=0, vmax=30)
            cmap = matplotlib.cm.get_cmap(name="viridis", lut=None)  # prism, viridis_r
        else:
            observable_values_to_plot = numpy.array(observable_values) / 60.0
            norm = matplotlib.colors.Normalize(vmin=0, vmax=90)

        sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([norm.vmin, norm.vmax])

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

        for plot_func in [_plot_smopy]:
            plot_func(lats, lons, observable_values_to_plot,
                      observable_name, sm, basename, node_desc, ax=smopy_fig.add_subplot(4, 3, i + 1))
        print("Done with " + observable_name)
    smopy_fig.savefig(RESULTS_DIRECTORY + "multiple_measures.pdf")


def _plot_mplleafflet(lats, lons, observable_values_in_minutes, observable_name, scalar_mappable, basename, node_names):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    colors = scalar_mappable.to_rgba(observable_values_in_minutes)

    assert (isinstance(ax, matplotlib.axes.Axes))
    ax.scatter(lons, lats, c=colors, edgecolors=colors, s=10)
    cbar = fig.colorbar(scalar_mappable)

    ax.set_title(observable_name)
    mplleaflet.save_html(fig, basename + observable_name + ".html")




def _plot_smopy(lats, lons, observable_values_in_minutes, observable_name, scalar_mappable, basename, node_names,
                ax=None, return_smopy_map=False, s=12):
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
    ax.scatter(xs[valids], ys[valids], c=colors[valids], edgecolors=colors[valids], s=s)
    if observable_name:
        ax.set_title(observable_name)
    if return_smopy_map:
        return ax, smopy_map
    else:
        return ax


def _plot_folium(lats, lons, observable_values, observable_name, scalar_mappable, basename, node_names):
    center_lat = (numpy.percentile(lats, 1) + numpy.percentile(lats, 99)) / 2.
    center_lon = (numpy.percentile(lons, 1) + numpy.percentile(lons, 99)) / 2.

    f = folium.map.FeatureGroup()
    for lat, lon, value, node_name in list(zip(lats, lons, observable_values, node_names)):
        circle = folium.features.CircleMarker(
            [lat, lon],
            radius=100,
            color=None,
            fill_color=matplotlib.colors.rgb2hex(scalar_mappable.to_rgba(value)),
            fill_opacity=0.6,
            popup=str(node_name)
        )
        # monkey patching the template to be less verbose (perhaps not idea, though)
        circle._template = Template(
            u" {% macro script(this, kwargs) %} var {{this.get_name()}} = L.circle( [{{this.location[0]}},{{this.location[1]}}], {{ this.radius }}, { color: '{{ this.color }}', fillColor: '{{ this.fill_color }}', fillOpacity: {{ this.fill_opacity }} } ).addTo({{this._parent.get_name()}}); {% endmacro %} ")
        circle._template.environment = Environment(trim_blocks=True, lstrip_blocks=True)
        f.add_child(circle)

    mapa = folium.Map([center_lat, center_lon], zoom_start=12, tiles=DARK_TILES, detect_retina=True)
    mapa.add_child(f)
    # mapa.add_child(cm)
    mapa.save(basename + observable_name + ".html")


if __name__ == "__main__":
    plot_transfers()
    # plot_temporal_distances()
