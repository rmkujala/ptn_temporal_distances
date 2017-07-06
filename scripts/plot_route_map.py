from gtfspy.mapviz import plot_route_network, ROUTE_TYPE_TO_ZORDER
from gtfspy.gtfs import GTFS
import matplotlib.pyplot as plt
import numpy
from settings import FIGS_DIRECTORY
import settings
from matplotlib import rc
rc('legend', framealpha=0.8)
rc("text", usetex=True)


fname = "../data/main.sqlite"  # A database imported using gtfspy
g = GTFS(fname)

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig = plt.figure(figsize=(5,3.5))
ax = fig.add_subplot(111)
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

stops = g.stops()
lats = stops["lat"].values
lons = stops["lon"].values

ROUTE_TYPE_TO_ZORDER[1] = 10  # set subway on top

spatial_bounds = {
    "lat_min": numpy.percentile(lats, 2),
    "lat_max": numpy.percentile(lats, 94),
    "lon_min": numpy.percentile(lons, 5),
    "lon_max": numpy.percentile(lons, 95)
}

ax, smopy_map = plot_route_network(g, ax, spatial_bounds=spatial_bounds, map_alpha=0.8, scalebar=True, return_smopy_map=True)

stop_lats = []
stop_lons = []
stop_Is = map(settings.get_stop_I_by_stop_id, [settings.AALTO_UNIVERSITY_ID, settings.ITAKESKUS_ID, settings.MUNKKIVUORI_ID])
chars = "AIM"
for stop_I in stop_Is:
    stop_info = g.stop(stop_I)
    lat = stop_info['lat'].values
    lon = stop_info['lon'].values
    stop_lats.append(lat)
    stop_lons.append(lon)

xs, ys = smopy_map.to_pixels(numpy.array(stop_lats), numpy.array(stop_lons))

for x, y, char in zip(xs, ys, chars):
    ax.text(x, y, r"\textbf{" + char + "}", fontsize=12, zorder=2000, ha="center", va="center", color="white")

# plt.show()
fig.savefig(FIGS_DIRECTORY + "/route_map.pdf")
