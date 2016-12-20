import os

import matplotlib
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt
import mplleaflet
import numpy
import smopy

smopy.TILE_SERVER = "http://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"

import folium

import pandas
from jinja2 import Template

from compute import get_node_profile_statistics, target_list_to_str

from jinja2.environment import Environment
from settings import HELSINKI_NODES_FNAME, DARK_TILES
from settings import RESULTS_DIRECTORY


def main():
    targets = [3373]  # [115, 3063]  # kamppi, kilo
    nodes = pandas.read_csv(HELSINKI_NODES_FNAME)

    data = get_node_profile_statistics(targets, recompute=True, recompute_profiles=False)
    observable_name_to_data = data
    observable_names = sorted(list(observable_name_to_data.keys()))

    print("Producing figures")
    basename = RESULTS_DIRECTORY + "/helsinki_test_" + target_list_to_str(targets) + "_"
    for observable_name in observable_names:
        print(observable_name)
        observable_values = observable_name_to_data[observable_name]
        # set up colors
        cmap = matplotlib.cm.get_cmap(name="gnuplot2_r", lut=None)  # prism, viridis_r
        if observable_name == "n_trips":
            observable_values_to_plot = observable_values
            norm = matplotlib.colors.Normalize(vmin=0, vmax=max(observable_values))
        elif "n_boardings" in observable_name:
            observable_values = numpy.array(observable_values)
            new_max = 7  # numpy.nanmax(observable_values[observable_values < float('inf')]) + 0.5
            nans = numpy.isnan(observable_values)
            observable_values[nans] = float('inf')
            observable_values_to_plot = observable_values
            norm = matplotlib.colors.Normalize(vmin=0, vmax=new_max)
        else:
            observable_values_to_plot = numpy.array(observable_values) / 90.0
            norm = matplotlib.colors.Normalize(vmin=0, vmax=90)

        sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([norm.vmin, norm.vmax])

        lats = nodes['lat']
        lons = nodes['lon']
        zipped = list(zip(observable_values_to_plot, lats, lons,
                          [str(node) for node in nodes['desc']]))
        zipped = reversed(sorted(zipped))
        observable_values_to_plot, lats, lons, node_desc = zip(*zipped)
        observable_values_to_plot = numpy.array(observable_values_to_plot)
        lats = numpy.array(lats)
        lons = numpy.array(lons)

        for plot_func in [_plot_smopy]:
            plot_func(lats, lons, observable_values_to_plot,
                      observable_name, sm, basename, node_desc)

        print("Done with " + observable_name)


def _plot_mplleafflet(lats, lons, observable_values_in_minutes, observable_name, scalar_mappable, basename, node_names):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    colors = scalar_mappable.to_rgba(observable_values_in_minutes)

    assert (isinstance(ax, matplotlib.axes.Axes))
    ax.scatter(lons, lats, c=colors, edgecolors=colors, s=10)
    cbar = fig.colorbar(scalar_mappable)

    ax.set_title(observable_name)
    mplleaflet.save_html(fig, basename + observable_name + ".html")


def _plot_smopy(lats, lons, observable_values_in_minutes, observable_name, scalar_mappable, basename, node_names):
    smopy_map = smopy.Map((lats.min(), lons.min(), lats.max(), lons.max()), z=10)

    fig = plt.figure(figsize=(12, 8), dpi=300)
    ax = fig.add_subplot(111)
    ax = smopy_map.show_mpl(figsize=(12, 8), ax=ax)
    xs, ys = smopy_map.to_pixels(lats, lons)

    ax.set_xlim(numpy.percentile(xs, 1), numpy.percentile(xs, 99))
    ax.set_ylim(numpy.percentile(ys, 99), numpy.percentile(ys, 1))


    colors = scalar_mappable.to_rgba(observable_values_in_minutes)

    assert(isinstance(ax, matplotlib.axes.Axes))
    ax.scatter(xs, ys, c=colors, edgecolors=colors, s=10)
    cbar = fig.colorbar(scalar_mappable)

    ax.set_title(observable_name)
    fig.savefig(basename + observable_name + ".png")


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
    main()
