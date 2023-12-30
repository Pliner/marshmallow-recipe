import re
from pathlib import Path

from setuptools import setup, Extension

install_requires = ("marshmallow>=2,<4",)


def read(*parts: str):
    return Path(__file__).resolve().parent.joinpath(*parts).read_text().strip()


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*\"([\d.abrc]+)\"")
    for line in read("marshmallow_recipe", "__init__.py").splitlines():
        match = regexp.match(line)
        if match is not None:
            return match.group(1)
    else:
        raise RuntimeError("Cannot find version in marshmallow_recipe/__init__.py")


long_description_parts = []
with open("README.md", "r") as fh:
    long_description_parts.append(fh.read())

with open("CHANGELOG.md", "r") as fh:
    long_description_parts.append(fh.read())

long_description = "\r\n".join(long_description_parts)

# custom PyPI classifier for pytest plugins
setup(
    name="marshmallow_recipe",
    version=read_version(),
    description="Bake marshmallow schemas based on dataclasses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=["macOS", "POSIX", "Windows"],
    author="Yury Pliner",
    python_requires=">=3.10",
    project_urls={},
    url="https://github.com/Pliner/marshmallow-recipe",
    author_email="yury.pliner@gmail.com",
    license="MIT",
    packages=["marshmallow_recipe"],
    package_dir={"marshmallow_recipe": "./marshmallow_recipe"},
    package_data={"marshmallow_recipe": ["py.typed"]},
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ],
    ext_modules=[
        Extension(
            '_marshmallow_recipe',
            sources=[
                'marshmallow_recipe/_marshmallow_recipe.c',
            ],
            depends=[
                'marshmallow_recipe/jansson.h',
                'marshmallow_recipe/jansson_config.h',
            ],
            libraries=['jansson'],
        )
    ],
)
