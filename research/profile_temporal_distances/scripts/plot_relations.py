import numpy
import pandas
import seaborn as sns
import matplotlib.pyplot as plt
import settings

from compute_node_profiles import get_node_profile_statistics

target_stop_I = 115
observable_name_to_data = get_node_profile_statistics(target_stop_I=target_stop_I)

df = pandas.DataFrame.from_dict(observable_name_to_data)
df.replace([numpy.inf, -numpy.inf], numpy.nan, inplace=True)
df.dropna(0, "any", inplace=True)

profile_observable_names = [
    "max_trip_duration",
    "max_temporal_distance",
    "mean_trip_duration",
    "mean_temporal_distance",
    "min_trip_duration"
]

fig = plt.figure()
pair_grid = sns.pairplot(df[profile_observable_names])
for i in range(len(pair_grid.axes)):
    for j in range(len(pair_grid.axes[i])):
        ax = pair_grid.axes[i, j]
        ax.set_xlim(0, 7200)
        if i != j:
            ax.set_ylim(0, 7200)
            ax.plot([0, 7200], [0, 7200], "-", color="r")
plt.savefig(settings.RESULTS_DIRECTORY + "helsinki_test_" + str(target_stop_I) + "_" + "measure_relationships.pdf")
print("Done!")