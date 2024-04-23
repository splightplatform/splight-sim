from setuptools import find_packages, setup

with open("requirements.txt") as fp:
    install_requires = fp.readlines()

dependency_links = [
    # External repositories different from pypi
]

setup(
    name="splight-dnp3",
    author="Splight",
    author_email="factory@splight-ae.com",
    packages=find_packages(),
    scripts=[],
    url=None,
    license="LICENSE.txt",
    description="Library for internal use only. Splight",
    long_description=open("README.md").read(),
    install_requires=install_requires,
    dependency_links=dependency_links,
)
