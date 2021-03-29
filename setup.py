import os.path as op
from setuptools import setup, find_packages


def get_version():
    with open(op.join(op.dirname(__file__), "dwellml", "__init__.py")) as fp:
        ns = {}
        exec(fp.read(), ns, ns)
        return ns["__version__"]


setup(
    name="dwellml",
    version=get_version(),
    description="Dwell Accelerators",
    author="DwellAnalytics",
    author_email="grajakumar@team.dgtl-factory.com",
    packages=find_packages(),
    zip_safe=False,
    license="Proprietary",
    install_requires=[
        "pandas",
        "matplotlib",
        "mplleaflet",
        "datetime",
        "sklearn",
        "shapely",
        "googlemaps",
        "Bunch",
        "tqdm",
        "time"
        ],
)
