import os

from matplotlib import pyplot as plt
from matplotlib import rc
rc("text", usetex=True)

journeys_str = """B	&	OcdefgD	&	08:08	&	08:28	&	3	&	20
                C	&	OcdeD	&	08:08	&	08:32	&	2	&	24
                D	&	OcdeD	&	08:08	&	08:59	&	2	&	51
                E	&	OabD	&	08:13	&	08:50	&	1	&	37
                F	&	OhijkD	&	08:19	&	08:39	&	2	&	20
                G	&	OhideD	&	08:19	&	08:59	&	2	&	40
                H	&	OcdeD	&	08:28	&	08:59	&	2	&	31
                I	&	OabD	&	08:33	&	09:10	&	1	&	37"""

DEPARTURE_TIME_MIN = 8*60

def to_journey(line):
    splitted = line.split("&")
    arrival_str = splitted[3].strip()
    arrival_hour = int(arrival_str[1])
    arrival_min = int(arrival_str[3:5])
    arrival_time_min = arrival_hour * 60 + arrival_min
    boardings = int(splitted[4].strip())
    return (arrival_time_min - DEPARTURE_TIME_MIN, boardings)

journeys = [to_journey(line) for line in journeys_str.split("\n")]
journeys.append((60, 0))
durations = [j[0] for j in journeys]
boardings = [j[1] for j in journeys]

fig = plt.figure(figsize=(4, 3))
ax = fig.add_subplot(111)

boardings_to_min_arr_time = {0: float('inf'), 1:float('inf'), 2:float('inf'), 3:float('inf')}
for j in journeys:
    boardings_to_min_arr_time[j[1]] = min(boardings_to_min_arr_time[j[1]], j[0])
pareto_front_boardings = list(boardings_to_min_arr_time.keys())
pareto_front_durations = list(boardings_to_min_arr_time.values())

ax.grid(linestyle=':', linewidth=0.5, zorder=-100)
ax.scatter(boardings, durations, color="k", label="All journeys", s=20, zorder=40)
ax.scatter(pareto_front_boardings, pareto_front_durations, color="red", s=70, alpha=0.5, label="Pareto frontier", zorder=20)

ax.set_xlabel(r"Number of boardings $b$")
ax.set_ylabel(r"Time to destination (min) $t_{arr} - t$")
ax.set_xticks([0, 1, 2, 3])
ylim = ax.get_ylim()
ax.set_ylim((ylim[0], 80))
ax.legend(loc="upper right")

plt.tight_layout()
from settings import FIGS_DIRECTORY
fig.savefig(os.path.join(FIGS_DIRECTORY, "pareto_front_schematic.pdf"))
plt.show()




