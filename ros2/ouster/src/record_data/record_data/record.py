import rclpy
from rclpy.node import Node
from rclpy.serialization import serialize_message
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan,Image,PointCloud2,Imu
import rosbag2_py

class OusterBagRecorder(Node):
    def __init__(self):
        super().__init__('ouster_bag_recorder')
        self.writer = rosbag2_py.SequentialWriter()

        storage_options = rosbag2_py._storage.StorageOptions(
            uri='/RA/octo-succotash/ros2/data',
            storage_id='sqlite3')
        converter_options = rosbag2_py._storage.ConverterOptions('', '')
        self.writer.open(storage_options, converter_options)
        topic_infos = []
        self.subs = []
        
        #scan
        topic_infos.append(rosbag2_py._storage.TopicMetadata(
            name='scan',
            type='sensor_msgs/LaserScan',
            serialization_format='cdr'))
        self.writer.create_topic(topic_infos[-1])

        self.subs.append(self.create_subscription(
            LaserScan,
            'scan',
            lambda msg: self.writer.write('scan', serialize_message(msg), self.get_clock().now().nanoseconds),
            10))

        #range_image
        topic_infos.append(rosbag2_py._storage.TopicMetadata(
            name='range_image',
            type='sensor_msgs/Image',
            serialization_format='cdr'))
        self.writer.create_topic(topic_infos[-1])

        self.subs.append(self.create_subscription(
            Image,
            'range_image',
            lambda msg: self.writer.write('range_image', serialize_message(msg), self.get_clock().now().nanoseconds),
            10))

        #intensity_image
        topic_infos.append(rosbag2_py._storage.TopicMetadata(
            name='intensity_image',
            type='sensor_msgs/Image',
            serialization_format='cdr'))
        self.writer.create_topic(topic_infos[-1])

        self.subs.append(self.create_subscription(
            Image,
            'intensity_image',
            lambda msg: self.writer.write('intensity_image', serialize_message(msg), self.get_clock().now().nanoseconds),
            10))

        #noise_image
        topic_infos.append(rosbag2_py._storage.TopicMetadata(
            name='noise_image',
            type='sensor_msgs/Image',
            serialization_format='cdr'))
        self.writer.create_topic(topic_infos[-1])

        self.subs.append(self.create_subscription(
            Image,
            'noise_image',
            lambda msg: self.writer.write('noise_image', serialize_message(msg), self.get_clock().now().nanoseconds),
            10))

        #reflectivity_image
        topic_infos.append(rosbag2_py._storage.TopicMetadata(
            name='reflectivity_image',
            type='sensor_msgs/Image',
            serialization_format='cdr'))
        self.writer.create_topic(topic_infos[-1])
        
        self.subs.append(self.create_subscription(
            Image,
            'reflectivity_image',
            lambda msg: self.writer.write('reflectivity_image', serialize_message(msg), self.get_clock().now().nanoseconds),
            10))

        #points
        topic_infos.append(rosbag2_py._storage.TopicMetadata(
            name='points',
            type='sensor_msgs/PointCloud2',
            serialization_format='cdr'))
        self.writer.create_topic(topic_infos[-1])
        
        self.subs.append(self.create_subscription(
            PointCloud2,
            'points',
            lambda msg: self.writer.write('points', serialize_message(msg), self.get_clock().now().nanoseconds),
            10))

        #imu
        topic_infos.append(rosbag2_py._storage.TopicMetadata(
            name='imu',
            type='sensor_msgs/Imu',
            serialization_format='cdr'))
        self.writer.create_topic(topic_infos[-1])

        self.subs.append(self.create_subscription(
            Imu,
            'imu',
            lambda msg: self.writer.write('imu', serialize_message(msg), self.get_clock().now().nanoseconds),
            10))

        self.subs


def main(args=None):
    rclpy.init(args=args)
    obr = OusterBagRecorder()
    rclpy.spin(obr)
    rclpy.shutdown()


if __name__ == '__main__':
    main()