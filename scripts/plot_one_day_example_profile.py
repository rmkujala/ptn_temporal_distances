import os
import pickle

from matplotlib import pyplot as plt
from matplotlib import rc

import settings
from compute import _compute_profile_data
from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs
from util import get_data_or_compute

rc("text", usetex=True)

recompute = False

# change to settings.ITAKESKUS_STOP_ID to see the opposite direction:
destination_stop_id = settings.AALTO_UNIVERSITY_ID
destination_stop_I = settings.get_stop_I_by_stop_id(destination_stop_id)

# some setting up of filenames and origin stops
if destination_stop_id is settings.AALTO_UNIVERSITY_ID:
    origin_stop_id = settings.ITAKESKUS_ID
    profile_fname_prefix = "itakeskus_to_aalto"
    ax1_title = 'From It\\"akeskus to Aalto University'
else:
    origin_stop_id = settings.AALTO_UNIVERSITY_ID
    profile_fname_prefix = "aalto_to_itakeskus"
    ax1_title = 'From Aalto University to It\\"akeskus'

origin_stop_I = settings.get_stop_I_by_stop_id(origin_stop_id)

# Computing the profile and caching some of the data
profile_fname = os.path.join(settings.RESULTS_DIRECTORY, profile_fname_prefix + "_profile.pickle")
try:
    if recompute:
        raise RuntimeError("Recomputing!")
    print(profile_fname)
    profile = pickle.load(open(profile_fname, 'rb'))
except:
    fname = os.path.join(settings.RESULTS_DIRECTORY, "long_profiles_" + profile_fname_prefix + ".pkl")
    params = {
        "targets": [destination_stop_I],
        "routing_start_time_dep": settings.DAY_START,
        "routing_end_time_dep": settings.DAY_END
    }

    data = get_data_or_compute(fname, _compute_profile_data, recompute=recompute, **params)

    print(data["params"])

    profiles = data["profiles"]
    profile = profiles[origin_stop_I]
    pickle.dump(profile, open(profile_fname, 'wb'), -1)


# Spawn an analyzer object, and plot the boarding-count-augmented temporal distance profile
npa = NodeProfileAnalyzerTimeAndVehLegs(profile,
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
ax1.set_title(ax1_title)
ax1.set_xlabel("Departure time $t_{\\text{dep}}$ (min)")
ax1.set_ylabel("Temporal distance $\\tau$ (min)")

# Plot the boarding-count-augmented temporal distance distribution:
ax2 = plt.subplot2grid(subplot_grid, (0, 6), colspan=2, rowspan=1)
ax2 = npa.plot_temporal_distance_pdf_horizontal(use_minutes=True,
                                                ax=ax2,
                                                legend_font_size=11)
ax1.set_ylim(0, 80)
ax2.set_ylim(0, 80)
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
fig.savefig(os.path.join(settings.FIGS_DIRECTORY, "long_profile_with_transfers_" + profile_fname_prefix + ".pdf"))

# Print some statistics:
print("max_temporal_distance: ", npa.max_temporal_distance() / 60.0)
print("min_temporal_distance: ", npa.min_temporal_distance() / 60.0)
print("mean_temporal_distance: ", npa.mean_temporal_distance() / 60.0)
print("mean_temporal_distance_with_min_n_boardings: ", npa.mean_temporal_distance_with_min_n_boardings() / 60.0)
time_diff = npa.mean_temporal_distance_with_min_n_boardings() / 60.0 - npa.mean_temporal_distance() / 60.0
print("difference in mean t: ", time_diff)
print("mean_n_boardings: ", npa.mean_n_boardings_on_shortest_paths())
boarding_diff = npa.mean_n_boardings_on_shortest_paths() - npa.min_n_boardings()
print("difference in boardings: ", boarding_diff)
print("gain per boarding: ", time_diff / boarding_diff)

# Show the plot:
plt.show()
