from setuptools import find_packages, setup

package_name = 'migro_action_001'

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
        (
            'share/' + package_name + '/launch',
            ['launch/count_until.launch.py']
         ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='migro-tech',
    maintainer_email='ayosoremiobafemi@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'count_until_action_server = migro_action_001.action_server:main',
            'count_until_action_client = migro_action_001.action_client:main',
        ],
    },
)
