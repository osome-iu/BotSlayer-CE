from distutils.core import setup
from distutils.util import convert_path


main_ns = {}
ver_path = convert_path('bev_backend/utils/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(
    name='bev_backend',
    version=main_ns['__version__'],
    author='Pik-Mai Hui',
    packages=['bev_backend'],
    description='package for BEV backend',
    install_requires=[
        "circus",
        "asyncpg",
        "tweepy",
        "pandas",
        "numpy"
    ],
)
