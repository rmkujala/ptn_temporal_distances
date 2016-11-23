"""
Plot temporal distances based on pre-computed node-profiles
"""
import pandas
import pytz

from routing.node_profile_analyzer_time import NodeProfileAnalyzerTime
from routing.label import LabelTimeAndVehLegCount
from routing.node_profile_multiobjective import NodeProfileMultiObjective
from routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from settings import HELSINKI_NODES_FNAME, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP
from compute import get_profile_data
from matplotlib import pyplot as plt

target_stop_I = 115  # 3491  # Piispanaukio
profile_data = get_profile_data([target_stop_I], recompute=True)

nodes = pandas.read_csv(HELSINKI_NODES_FNAME)

profiles = profile_data["profiles"]

from_stop_Is = [
    123,    # Kamppi (as well)
    401,    # Kansanelakelaitos
    3356,   # Dipoli
    3063,   # Kilon asema
    5935,   # Sorvatie
    3101    # lahderannanristi
]

timezone = pytz.timezone("Europe/Helsinki")


target_stop_name = nodes[nodes["stop_I"] == target_stop_I]["name"].values[0]
for from_stop_I in from_stop_Is:
    print(from_stop_I)
    from_stop_name = nodes[nodes["stop_I"] == from_stop_I]["name"].values[0]
    stop_profile = profiles[from_stop_I]
    if isinstance(stop_profile, NodeProfileMultiObjective) and stop_profile.label_class == LabelTimeAndVehLegCount:
        analyzer = NodeProfileAnalyzerTimeAndVehLegs(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
    else:
        analyzer = NodeProfileAnalyzerTime(stop_profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
    fig = analyzer.plot_temporal_distance_variation(timezone=timezone)
    ax = fig.get_axes()[0]
    ax.set_title(u"From " + from_stop_name + u" to " + target_stop_name)
    fig.savefig(u"../results/" + from_stop_name + "_to_" + target_stop_name + ".pdf")
    plt.show()

