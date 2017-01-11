import os

import settings
from matplotlib import pyplot as plt

from compute import _compute_profile_data
from util import get_data_or_compute
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs


fname = os.path.join(settings.RESULTS_DIRECTORY, "long_profiles.pkl")
params = {
    "targets": [settings.OTANIEMI_STOP_ID],
    "routing_start_time_dep": settings.DAY_START,
    "routing_end_time_dep": settings.DAY_END
}

data = get_data_or_compute(fname, _compute_profile_data, recompute=False, **params)
profiles = data["profiles"]
itakeskus_profile = profiles[settings.ITAKESKUS_STOP_ID]

npa = NodeProfileAnalyzerTimeAndVehLegs(itakeskus_profile,
                                        settings.DAY_START + 6 * 3600,
                                        settings.DAY_START + 21 * 3600)

print(npa.all_labels)
fig = plt.figure(figsize=(12, 4))
ax = fig.add_subplot(111)
npa.plot_new_transfer_temporal_distance_profile(timezone=settings.TIMEZONE,
                                                format_string="%H:%M",
                                                plot_journeys=False,
                                                ax=ax,
                                                highlight_fastest_path=False,
                                                default_lw=1.5,
                                                ncol_legend=1)

fig.tight_layout()
fig.savefig(os.path.join(settings.RESULTS_DIRECTORY, "long_profile_with_transfers.pdf"))

plt.show()
