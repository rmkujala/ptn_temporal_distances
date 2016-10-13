import os

import matplotlib
import matplotlib.colors
import matplotlib.cm
import matplotlib.pyplot as plt

import mplleaflet
import numpy
import smopy

smopy.TILE_SERVER = "http://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"

import folium

import pandas
from jinja2 import Template

from compute_node_profiles import get_profile_data, _compute_node_profile_statistics, get_node_profile_statistics

from jinja2.environment import Environment
from settings import HELSINKI_NODES_FNAME, ANALYSIS_END_TIME_DEP, ANALYSIS_START_TIME_DEP, DARK_TILES
from settings import RESULTS_DIRECTORY


def main():
    target_stop_I = 115

    nodes = pandas.read_csv(HELSINKI_NODES_FNAME)
    data = get_node_profile_statistics(target_stop_I)
    observable_name_to_data = data
    observable_names = sorted(list(observable_name_to_data.keys()))

    print("Producing figures")
    for observable_name in observable_names:
        observable_values = observable_name_to_data[observable_name]
        # set up colors
        norm = matplotlib.colors.Normalize(vmin=0, vmax=60)
        cmap = matplotlib.cm.get_cmap(name="viridis_r", lut=None)
        sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([norm.vmin, norm.vmax])

        observable_values_min = numpy.array(observable_values) / 60.0
        for _plot_func in [_plot_smopy]:  # , _plot_folium]:
            _plot_func(nodes['lat'], nodes['lon'], observable_values_min, observable_name, sm)

        print("Done with " + observable_name)


def _plot_mplleafflet(lats, lons, observable_values_min, observable_name, scalar_mappable):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    colors = scalar_mappable.to_rgba(observable_values_min)

    assert (isinstance(ax, matplotlib.axes.Axes))
    ax.scatter(lons, lats, c=colors, edgecolors=colors, s=10)
    cbar = fig.colorbar(scalar_mappable)

    ax.set_title(observable_name)
    mplleaflet.save_html(fig, RESULTS_DIRECTORY + "/helsinki_test_mplleaflet_" + observable_name + ".html")


def _plot_smopy(lats, lons, observable_values_min, observable_name, scalar_mappable):
    smopy_map = smopy.Map((lats.min(), lons.min(), lats.max(), lons.max()), z=10)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax = smopy_map.show_mpl(figsize=(8, 6), ax=ax)
    xs, ys = smopy_map.to_pixels(lats, lons)

    ax.set_xlim(numpy.percentile(xs, 1), numpy.percentile(xs, 99))
    ax.set_ylim(numpy.percentile(ys, 99), numpy.percentile(ys, 1))
    colors = scalar_mappable.to_rgba(observable_values_min)

    assert(isinstance(ax, matplotlib.axes.Axes))
    ax.scatter(xs, ys, c=colors, edgecolors=colors, s=10)
    cbar = fig.colorbar(scalar_mappable)

    ax.set_title(observable_name)
    fig.savefig(RESULTS_DIRECTORY + "/helsinki_test_smopy_" + observable_name + ".pdf")


def _plot_folium(lats, lons, observable_values, observable_name, scalar_mappable):
    center_lat = (numpy.percentile(lats, 1) + numpy.percentile(lats, 99)) / 2.
    center_lon = (numpy.percentile(lons, 1) + numpy.percentile(lons, 99)) / 2.

    f = folium.map.FeatureGroup()
    for lat, lon, value in list(zip(lats, lons, observable_values)):
        circle = folium.features.CircleMarker(
            [lat, lon],
            radius=100,
            color=None,
            fill_color=matplotlib.colors.rgb2hex(scalar_mappable.to_rgba(value)),
            fill_opacity=0.6
        )
        # monkey patching the template to be less verbose (perhaps not idea, though)
        circle._template = Template(
            u" {% macro script(this, kwargs) %} var {{this.get_name()}} = L.circle( [{{this.location[0]}},{{this.location[1]}}], {{ this.radius }}, { color: '{{ this.color }}', fillColor: '{{ this.fill_color }}', fillOpacity: {{ this.fill_opacity }} } ).addTo({{this._parent.get_name()}}); {% endmacro %} ")
        circle._template.environment = Environment(trim_blocks=True, lstrip_blocks=True)
        f.add_child(circle)

    mapa = folium.Map([center_lat, center_lon], zoom_start=12, tiles=DARK_TILES, detect_retina=True)
    mapa.add_child(f)
    # mapa.add_child(cm)
    mapa.save(os.path.join(RESULTS_DIRECTORY, "helsinki_profile_test_folium_" + observable_name + ".html"))



if __name__ == "__main__":
    main()