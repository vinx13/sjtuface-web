from setuptools import setup

setup(
    name='sjtuface',
    packages=['sjtuface'],
    include_package_data=True,
    install_requires=[
        'flask',
        'Flask-SQLAlchemy',
        'Flask-Login',
        'Flask-Cache',
        'Flask-RESTful',
        'Flask-Script',
        'Flask-Wtf',
        'MySQL-python'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
