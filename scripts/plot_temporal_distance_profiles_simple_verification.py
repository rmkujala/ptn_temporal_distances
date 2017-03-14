from __future__ import unicode_literals

import settings

"""
Plot temporal distance profile, using a simpler profiler keeping only of time.
Used for verifying results obtained for the multi-objective profiler.
"""

from gtfspy.routing.node_profile_analyzer_time import NodeProfileAnalyzerTime
from settings import AALTO_STOP_ID, ITAKESKUS_STOP_ID, MUNKKIVUORI_STOP_ID, TIMEZONE
from matplotlib import pyplot as plt
from matplotlib import rc
import compute

rc("text", usetex=True)
target_stop_I = AALTO_STOP_ID

params = {
    "targets": [settings.AALTO_STOP_ID],
    "routing_start_time_dep": settings.ROUTING_START_TIME_DEP,
    "routing_end_time_dep": settings.ROUTING_END_TIME_DEP
}

connections = compute.read_connections_pandas()
walk_network = compute.read_transfers_csv()
from gtfspy.routing.connection_scan_profile import ConnectionScanProfiler

csa = ConnectionScanProfiler(connections, target_stop_I, settings.ROUTING_START_TIME_DEP,
                             settings.ANALYSIS_END_TIME_DEP, transfer_margin=180, walk_network=walk_network,
                             walk_speed=70 / 60.0, verbose=True)
csa.run()
profiles = csa.stop_profiles

from_stop_Is = [
    # 123,    # Kamppi (as well)
    # 401,    # Kansanelakelaitos
    # 3356,   # Dipoli
    # 3063,   # Kilon asema
    # 5935,   # Sorvatie
    # 3101,   # lahderannanristi
    # 3373,     # Innopoli
    # 2843      # Vallikatu (Pohjois-Leppavaara)
    ITAKESKUS_STOP_ID,
    MUNKKIVUORI_STOP_ID
]

for i, from_stop_I in enumerate(from_stop_Is):
    stop_profile = profiles[from_stop_I]
    analyzer = NodeProfileAnalyzerTime(stop_profile, settings.ANALYSIS_START_TIME_DEP, settings.ANALYSIS_END_TIME_DEP)
    print(analyzer.mean_temporal_distance() / 60.)
    print(analyzer.min_temporal_distance() / 60.)
    print(analyzer.max_temporal_distance() / 60.)

    fig1 = analyzer.plot_temporal_distance_profile(timezone=TIMEZONE,
                                                   plot_tdist_stats=True,
                                                   format_string="%H:%M",
                                                   lw=3)
plt.show()
