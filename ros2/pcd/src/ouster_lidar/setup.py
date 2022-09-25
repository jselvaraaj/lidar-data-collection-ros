from setuptools import setup

package_name = 'ouster_lidar'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='josndan@outlook.com',
    description='Record and store Ouster Sensor Data',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = ouster_lidar.talker:main',
            'listener = ouster_lidar.listener:main',
        ],
    },
)
