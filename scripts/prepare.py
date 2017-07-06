import os
import subprocess

import requests

from settings import DATA_DIRECTORY, EXTRA_LOCATIONS, HELSINKI_NODES_FNAME, HELSINKI_TRANSIT_CONNECTIONS_FNAME, HELSINKI_TRANSFERS_FNAME, DAY_START, DAY_END
from gtfspy.exports import write_nodes, write_temporal_network, write_walk_transfer_edges
from util import get_data_or_compute
from gtfspy.gtfs import GTFS
from gtfspy import import_gtfs

from settings import IMPORTED_DATABASE_PATH, RAW_GTFS_ZIP_PATH, SWIMMING_HALL_ID_PREFIX

def add_extra_locations_to_stops_table():
    g = GTFS(IMPORTED_DATABASE_PATH)
    for location in EXTRA_LOCATIONS:

        id = location['id']
        lat = location['lat']
        lon = location['lon']
        g.add_stop(id, "", id.replace("ADDED_", ""), "", lat, lon)

def add_swimming_halls_to_stops_table():
    g = GTFS(IMPORTED_DATABASE_PATH)
    halls = get_swimming_hall_data()
    for hall in halls:
        lat = hall['latitude']
        lon = hall['longitude']
        name = hall['name_en'].replace(" ", "_")
        id = SWIMMING_HALL_ID_PREFIX + name + "_" + str(hall['id'])
        g.add_stop(id, "NULL", name, "NULL", lat, lon)

def run_pedestrian_routing_java(osm_map_path, temp_folder='/tmp/'):
    from gtfspy.calc_transfers import calc_transfers
    g = GTFS(IMPORTED_DATABASE_PATH)
    print("Recalculated straight line stop_distances")
    calc_transfers(g.conn)
    JAR_PATH = '../gtfspy/java_routing/target/transit_osm_routing-1.0-SNAPSHOT-jar-with-dependencies.jar'
    subprocess.call(["java", '-jar', JAR_PATH, '-u', IMPORTED_DATABASE_PATH, '-osm', osm_map_path, '--tempDir', temp_folder])

def download_osm_data():
    url = "http://download.geofabrik.de/europe/finland-latest.osm.pbf"
    local_filename = os.path.join(DATA_DIRECTORY, "raw", url.split('/')[-1])
    if not os.path.exists(local_filename):
        download_large_file(url, local_filename)
    return local_filename

def _fetch_swimming_hall_data():
    url = "http://www.hel.fi/palvelukarttaws/rest/v2/unit/?service=33462"
    print("fetching data from " + url)
    r = requests.get(url)
    data = r.json()
    return data

def download_large_file(url, local_filename):
    print("Downloading file " + url + " to " + local_filename)
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename

def get_swimming_hall_data():
    fname = os.path.join(DATA_DIRECTORY, "swimming_halls_json.pickle")
    return get_data_or_compute(fname, _fetch_swimming_hall_data)

def import_database(force=False):
    if force or not os.path.exists(IMPORTED_DATABASE_PATH):
        import_gtfs.import_gtfs([RAW_GTFS_ZIP_PATH],  # input: list of GTFS zip files (or directories)
                                IMPORTED_DATABASE_PATH,  # output: where to create the new sqlite3 database
                                print_progress=True,  # whether to print progress when importing data
                                location_name="Helsinki")

def create_extracts():
    g = GTFS(IMPORTED_DATABASE_PATH)
    write_nodes(g, HELSINKI_NODES_FNAME)
    write_temporal_network(g, HELSINKI_TRANSIT_CONNECTIONS_FNAME, DAY_START, DAY_END)
    write_walk_transfer_edges(g, HELSINKI_TRANSFERS_FNAME)

def clear_extract_stops():
    # DELETE FROM stops WHERE SUBSTR(stop_id, 0, 7) = "SWIMMI"
    # DELETE FROM stops WHERE SUBSTR(stop_id, 0, 7) = "ADDED_"
    raise NotImplementedError()


if __name__ == "__main__":
    osm_path = download_osm_data()
    import_database()
    add_swimming_halls_to_stops_table()
    add_extra_locations_to_stops_table()
    run_pedestrian_routing_java(osm_map_path=osm_path)
    create_extracts()



