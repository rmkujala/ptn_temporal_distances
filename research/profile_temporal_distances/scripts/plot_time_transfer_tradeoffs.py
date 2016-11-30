import numpy
import pandas
import seaborn as sns
from matplotlib import pyplot as plt

from gtfspy.routing.node_profile_analyzer_time_and_veh_legs import NodeProfileAnalyzerTimeAndVehLegs

from compute import get_profile_data
from settings import HELSINKI_NODES_FNAME, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP


def main():
    targets = [115, 3063]  # kamppi, kilo
    # nodes = pandas.read_csv(HELSINKI_NODES_FNAME)

    data = get_profile_data(targets, recompute=False)
    profiles = data["profiles"]
    node_to_n_veh_leg_temporaldistances = []
    max_n_veh_legs = 4
    for node, profile in profiles.items():
        analyzer = NodeProfileAnalyzerTimeAndVehLegs(profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
        distances = analyzer.median_temporal_distances(0, max_n_veh_legs)
        node_to_n_veh_leg_temporaldistances.append(distances)
        if ((numpy.array(distances) > 100000) * numpy.logical_not(numpy.isinf(numpy.array(distances)))).any():
            print(node, distances)
            analyzer = NodeProfileAnalyzerTimeAndVehLegs(profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
            distances = analyzer.median_temporal_distances(0, max_n_veh_legs)
    print("computed distances")

    node_to_n_veh_leg_temporaldistances = numpy.array(node_to_n_veh_leg_temporaldistances)
    node_to_n_veh_leg_temporaldistances[numpy.isinf(node_to_n_veh_leg_temporaldistances)] = float('nan')
    df = pandas.DataFrame(node_to_n_veh_leg_temporaldistances, columns=[str(i) for i in range(max_n_veh_legs + 1)])
    df.fillna(10000, inplace=True)
    sns.pairplot(df, dropna=True)
    plt.show()


if __name__ == "__main__":
    main()
