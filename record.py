from contextlib import closing
from datetime import datetime
from more_itertools import time_limited
import argparse
from ouster import pcap, client

parser = argparse.ArgumentParser()
parser.add_argument('--hostname', type=str, required=True)
parser.add_argument('--lidarport', type=str, required=True)
parser.add_argument('--imuport', type=str, required=True)
parser.add_argument('--bufsize', type=str, default=640)
parser.add_argument('--nseconds', type=str, default=500)

hostname = parser.parse_args().hostname
lidar_port = parser.parse_args().lidarport
imu_port = parser.parse_args().imuport
buf_size = parser.parse_args().bufsize
n_seconds = parser.parse_args().nseconds

with closing(client.Sensor(hostname, lidar_port, imu_port, buf_size=buf_size)) as source:
    # make a descriptive filename for metadata/pcap files
    time_part = datetime.now().strftime("%Y%m%d_%H%M%S")
    meta = source.metadata
    fname_base = f"{meta.prod_line}_{meta.sn}_{meta.mode}_{time_part}"

    print(f"Saving sensor metadata to: {fname_base}.json")
    source.write_metadata(f"{fname_base}.json")

    print(f"Writing to: {fname_base}.pcap (Ctrl-C to stop early)")
    source_it = time_limited(n_seconds, source)
    n_packets = pcap.record(source_it, f"{fname_base}.pcap")

    print(f"Captured {n_packets} packets")
