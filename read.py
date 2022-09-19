try:
    import config

    metadata_path = config.metadata_path
    pcap_path = config.pcap_path
except (AttributeError, NameError, ImportError) as e:
    raise Exception("Problem with the config file")

from ouster import pcap, client
import matplotlib.pyplot as plt
from more_itertools import nth

with open(metadata_path, 'r') as f:
    metadata = client.SensorInfo(f.read())

source = pcap.Pcap(pcap_path, metadata)
scans = client.Scans(source)
scan = nth(scans, 84)
ranges = scan.field(client.ChanField.RANGE)
ranges_destaggered = client.destagger(source.metadata, ranges)

plt.imshow(ranges_destaggered, cmap='gray', resample=False)
plt.show()
