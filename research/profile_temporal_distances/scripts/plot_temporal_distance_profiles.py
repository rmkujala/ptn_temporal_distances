"""
Plot temporal distances based on pre-computed node-profiles
"""
import pandas
import pytz

from gtfspy.routing.node_profile_analyzer import NodeProfileAnalyzer
from settings import HELSINKI_NODES_FNAME, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP
from compute import get_profile_data


target_stop_I = 115
profile_data = get_profile_data(recompute=False)

nodes = pandas.read_csv(HELSINKI_NODES_FNAME)

profiles = profile_data["profiles"]

from_stop_Is = [
    123,    # Kamppi (as well)
    3356,   # Dipoli
    3063,   # Kilon asema
    5935    # Sorvatie
]

target_stop_name = nodes[nodes["stop_I"] == target_stop_I]["name"].values[0]
for from_stop_I in from_stop_Is:
    from_stop_name = nodes[nodes["stop_I"] == from_stop_I]["name"].values[0]
    stop_profile = profiles[from_stop_I]
    analyzer = NodeProfileAnalyzer(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
    timezone = pytz.timezone("Europe/Helsinki")
    fig = analyzer.plot_temporal_distance_variation(timezone=timezone)
    ax = fig.get_axes()[0]
    ax.set_title(u"From " + from_stop_name + u" to " + target_stop_name)
    fig.savefig(u"../results/" + from_stop_name + "_to_" + target_stop_name + ".pdf")


