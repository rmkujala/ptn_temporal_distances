import numpy
import pandas
import seaborn as sns
import matplotlib.pyplot as plt
import settings

from compute import get_node_profile_statistics


def plot_time_measure_depencencies():
    pair_grid = sns.pairplot(df[profile_observable_names])
    for i in range(len(pair_grid.axes)):
        for j in range(len(pair_grid.axes[i])):
            ax = pair_grid.axes[i, j]
            ax.set_xlim(0, 120)
            if i != j:
                ax.set_ylim(0, 120)
                ax.plot([0, 120], [0, 120], "-", color="r")
    plt.savefig(settings.RESULTS_DIRECTORY + "helsinki_test_" + str(target_stop_I) + "_" + "measure_relationships.pdf")
    print("Done!")


def plot_counts_vs_time_measures():
    pair_grid = sns.pairplot(df, x_vars=profile_observable_names, y_vars=["n_trips"])
    for i in range(len(pair_grid.axes)):
        for j in range(len(pair_grid.axes[i])):
            ax = pair_grid.axes[i, j]
            ax.set_xlim(0, 120)
    plt.savefig(settings.RESULTS_DIRECTORY + "helsinki_test_" + str(target_stop_I) + "_" + "time_vs_ntrips.pdf")
    print("Done!")


def plot_time_lost():
    time_lost_string = "mean_tdistance-min_tdistance"
    df[time_lost_string] = df["mean_temporal_distance"] - df["min_temporal_distance"]

    pair_grid = sns.pairplot(df, x_vars=profile_observable_names, y_vars=[time_lost_string])
    for i in range(len(pair_grid.axes)):
        for j in range(len(pair_grid.axes[i])):
            ax = pair_grid.axes[i, j]
            ax.set_xlim(0, 120)
    plt.savefig(settings.RESULTS_DIRECTORY + "helsinki_test_" + str(target_stop_I) + "_" + "time_lost.pdf")
    plt.show()
    print("Done!")

if __name__ == "__main__":
    target_stop_I_s = 3063,  # [115, 3063]  # kamppi + kilo
    for target_stop_I in target_stop_I_s:
        observable_name_to_data = get_node_profile_statistics([target_stop_I], recompute=True, recompute_profiles=True)
        df = pandas.DataFrame.from_dict(observable_name_to_data)

        nodes_df = pandas.read_csv(settings.HELSINKI_NODES_FNAME)
        df.replace([numpy.inf, -numpy.inf], numpy.nan, inplace=True)
        df_with_node_info = pandas.concat([df, nodes_df], axis=1)
        # df.dropna(0, "any", inplace=True)
        for row in df_with_node_info.itertuples():
            if row.mean_temporal_distance - row.min_temporal_distance < 0:
                print(row)

        all_profile_observable_names = [
            "max_trip_duration",
            "max_temporal_distance",
            "mean_trip_duration",
            "mean_temporal_distance",
            "min_trip_duration",
            "min_temporal_distance",
            "median_trip_duration",
            "median_temporal_distance"
        ]
        for observable_name in all_profile_observable_names:
            df[observable_name] /= 60.0

        # used in actual plotting:
        profile_observable_names = [el for i, el in enumerate(all_profile_observable_names) if i in [0, 1, 2, 3, 4]]
        # plot_time_measure_dependencies()
        # plot_counts_vs_time_measures()
        # plot_time_lost()



