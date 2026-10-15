from setuptools import setup
import os
from glob import glob

package_name = 'ros_solar_cleaner'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name] if os.path.exists('resource/' + package_name) else []),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Rakshith',
    maintainer_email='rakshithganjimut@gmail.com',
    description='ROS 2 Package for Autonomous 6-DOF Robotic Arm Solar Panel Cleaning and 4-Zone Current Sensor Telemetry',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'solar_telemetry_publisher = ros_solar_cleaner.nodes.solar_telemetry_publisher:main',
            'dust_monitor_subscriber = ros_solar_cleaner.nodes.dust_monitor_subscriber:main',
            'cleaning_executive_node = ros_solar_cleaner.nodes.cleaning_executive_node:main',
            'arm_hardware_node = ros_solar_cleaner.nodes.arm_hardware_node:main',
        ],
    },
)
