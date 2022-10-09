from contextlib import closing
import datetime as dt
from multiprocessing.connection import Client
from more_itertools import time_limited
from ouster import pcap, client
import yaml
from loguru import logger
from pathlib import Path
import sys

lidar_params = None
ouster_sensor_params = None
n_seconds = None
log_rotation = None

def is_global_log(record):
    return True
    # return record['message'].find("[Global]") != -1

def is_local_log(record):
    return record['message'].find("[File Specific]") != -1

def is_stderr(record):
    return not(is_global_log(record) or is_local_log(record))

current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

global_log_path = Path("logs","global")

global_log_path.mkdir(exist_ok=True,parents=True)
Path("logs","stderr").mkdir(exist_ok=True,parents=True)

sys.stderr = open(Path("logs","stderr",f"{current_time}.log"), 'a')
logger.add(sys.stderr, filter=is_stderr)

with open('config.yml', 'r') as config_file:
    config_dict = yaml.safe_load(config_file)
    try:
        #required in the config file; if not specified raise key error
        lidar_params = config_dict['LIDAR']
        ouster_sensor_params = lidar_params["sensor"]

        ouster_sensor_params['hostname']
        ouster_sensor_params['lidar_port']
        ouster_sensor_params['imu_port']
        ouster_sensor_params['buf_size']

        n_seconds = lidar_params['everynseconds']
        
        log_rotation = config_dict['LOGGER']['rotation']
    except KeyError:
        logger.error("Conifg file is corrupted")
        exit(1)

g_logger_id = logger.add(global_log_path.joinpath(f"{current_time}.log"), format="{time} {level} {message}", level="DEBUG", filter=is_global_log,rotation=log_rotation)
logger.info("[Global] Global Logger initialized")

try:
    ouster_client = client.Sensor(**ouster_sensor_params)
except client.ClientError as e:
    logger.critical(f"[Global] Unable to connect to Ouster Sensor: Initialization failed {str(e)}")
    exit(1)
except RuntimeError as e:
    logger.critical(f"[Global] Unable to connect to Ouster Sensor: Runtime Error {str(e)}")
    exit(1)

with closing(ouster_client) as source:
    logger.info("[Global] Established connection to Ouster Sensor")

    Path("lidar_data").mkdir(exist_ok=True)
    meta = source.metadata

    i=0
    while True:
        logger.info(f"[Global] Started Recording: {i+1}th iteration")

        current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname_base = Path("lidar_data",f"{meta.prod_line}_{meta.sn}_{meta.mode}_{current_time}")
        logger.info(f"[Global] Logs associated with this recording is stored in {fname_base}")
        
        try:
            Path(fname_base).mkdir(exist_ok=False)
        except:
            logger.warning(f"{str(fname_base)} already exists")

        local_logger_id = logger.add(fname_base.joinpath("individual.log"), format="{time} {level} {message}", level="DEBUG", filter = is_local_log, rotation=log_rotation)

        logger.info(f"[File Specific] Started Saving sensor metadata to: {str(fname_base)}")
        source.write_metadata(str(fname_base.joinpath("metadata.json")))
        logger.info(f"[File Specific] Finished Saving sensor metadata to: {str(fname_base)}")

        logger.info(f"[File Specific] Started Writing to: {str(fname_base)} (Ctrl-C to stop early)")
        try:
            source_it = time_limited(n_seconds, source)
            n_packets = pcap.record(source_it, str(fname_base.joinpath("data.pcap")))
            logger.info(f"[File Specific] Captured {n_packets} packets")
        except client.ClientTimeout as e:
            logger.error(f"[File Specific] no packets were received within the configured timeout {str(e)}")
        except client.ClientError as e:
            logger.error(f"[File Specific] client entered an unspecified error state {str(e)}")
        except ValueError as e:
            logger.error(f"[File Specific] packet source has already been closed {str(e)}")
        except client.ClientOverflow as e:
            logger.warning(f"[File Specific] data loss is possible - internal buffers filled up {str(e)}")

        logger.info(f"[File Specific] Finished Writing to: {str(fname_base)}")
        logger.remove(local_logger_id)
        
        logger.info(f"[Global] Finished Recording: {i+1}th iteration")
        i+=1

ouster_client.close() #Precatious
logger.info("[Global] Closed connection to Ouster Sensor")
