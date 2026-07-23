from setuptools import find_packages, setup

package_name = 'migro_tf2_001'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='migro-tech',
    maintainer_email='ayosoremiobafemi@gmail.com',
    description='ROS 2 package demonstrating TF2 Broadcasters and Coordinate Frames.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'tf_broadcaster = migro_tf2_001.tf_broadcaster:main',
            'tf_listener = migro_tf2_001.tf_listener:main',
        ],
    },
)
