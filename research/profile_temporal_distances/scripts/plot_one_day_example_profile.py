import os

import pickle

import settings
from matplotlib import pyplot as plt

from compute import _compute_profile_data
from util import get_data_or_compute
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs

from matplotlib import rc

rc("text", usetex=True)

recompute = True
itakeskus_profile_fname = os.path.join(settings.RESULTS_DIRECTORY, "itakeskus_profile.pickle")
try:
    if recompute:
        raise RuntimeError("Recomputing!")
    itakeskus_profile = pickle.load(open(itakeskus_profile_fname, 'rb'))
except:
    fname = os.path.join(settings.RESULTS_DIRECTORY, "long_profiles.pkl")
    print(fname)
    params = {
        "targets": [settings.OTANIEMI_STOP_ID],
        "routing_start_time_dep": settings.DAY_START,
        "routing_end_time_dep": settings.DAY_END
    }

    data = get_data_or_compute(fname, _compute_profile_data, recompute=recompute, **params)

    print(data["params"])

    profiles = data["profiles"]
    itakeskus_profile = profiles[settings.ITAKESKUS_STOP_ID]
    pickle.dump(itakeskus_profile, open(itakeskus_profile_fname, 'wb'), -1)

npa = NodeProfileAnalyzerTimeAndVehLegs(itakeskus_profile,
                                        settings.DAY_START + 6 * 3600,
                                        settings.DAY_START + 21 * 3600)

fig = plt.figure(figsize=(11, 3.5))
subplot_grid = (1, 8)
ax1 = plt.subplot2grid(subplot_grid, (0, 0), colspan=6, rowspan=1)
npa.plot_new_transfer_temporal_distance_profile(timezone=settings.TIMEZONE,
                                                format_string="%H:%M",
                                                plot_journeys=False,
                                                ax=ax1,
                                                highlight_fastest_path=False,
                                                default_lw=1.5,
                                                ncol_legend=1)


ax1.set_ylabel("Temporal distance $\\tau$")
ax1.set_title('From It\\"akeskus to Alvar Aalto\'s park')

ax1.set_xlabel("Departure time $t_{\\text{dep}}$ (min)")
ax1.set_ylabel("Temporal distance $\\tau$ (min)")

ax2 = plt.subplot2grid(subplot_grid, (0, 6), colspan=2, rowspan=1)
ax2 = npa.plot_temporal_distance_pdf_horizontal(use_minutes=True,
                                                ax=ax2,
                                                legend_font_size=11)
ax1.set_ylim(0, 70)
ax2.set_ylim(0, 70)

ax2.set_xticks([0.00, 0.05, 0.1])

ax2.set_ylabel("Temporal distance $\\tau$ (min)")
ax2.set_xlabel("Probability density $P(\\tau)$")

for ax, letter, x in zip([ax1, ax2], "AB", [0.01, 0.04]):
    ax2.text(x, 0.98,
              "\\textbf{" + letter + "}",
              horizontalalignment="left",
              verticalalignment="top",
              transform=ax.transAxes,
              fontsize=15,
              color="black")

fig.tight_layout()
fig.savefig(os.path.join(settings.FIGS_DIRECTORY, "long_profile_with_transfers.pdf"))


analyzer = npa
print("max_temporal_distance: ", analyzer.max_temporal_distance() / 60.0)
print("min_temporal_distance: ", analyzer.min_temporal_distance() / 60.0)
print("mean_temporal_distance: ", analyzer.mean_temporal_distance() / 60.0)
print("mean_temporal_distance_with_min_n_boardings: ", analyzer.mean_temporal_distance_with_min_n_boardings() / 60.0)
time_diff = analyzer.mean_temporal_distance_with_min_n_boardings() / 60.0 - analyzer.mean_temporal_distance() / 60.0
print("difference in mean t: ", time_diff)
print("mean_n_boardings: ", analyzer.mean_n_boardings_on_shortest_paths())
boarding_diff = analyzer.mean_n_boardings_on_shortest_paths() - analyzer.min_n_boardings()
print("difference in boardings: ", boarding_diff)
print("gain per boarding: ", time_diff / boarding_diff)

plt.show()
