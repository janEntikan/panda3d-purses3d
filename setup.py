import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="panda3d-purses3d",
    version="0.0.8",
    author="momojohobo",
    author_email="bandaibandai@rocketship.com",
    description="Ncurses-like text printing for Panda3D",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/momojohobo/panda3d-purses3d",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "panda3d",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
