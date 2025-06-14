import setuptools
import re

with open("README.md", "r") as fh:
  long_description = fh.read()

version = ''

with open("shapesinc/__info__.py") as f:
  version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if version.endswith(('a', 'b', 'rc')):
  # append version identifier based on commit count
  try:
    import subprocess
    p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if out:
      version += out.decode('utf-8').strip()
    p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if out:
      version += '+g' + out.decode('utf-8').strip()
  except Exception:
    pass

setuptools.setup(
  name="shapesinc",
  version=version,
  author="Rishiraj0100",
  description="A module for interacting with shapes.inc API.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages(exclude=["docs", ".github", "examples", "tests"]),
  install_requires=["aiohttp"],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  project_urls={
    "Documentation": "https://shapesinc-py.rtfd.io/",
    "Issue tracker": "https://github.com/Rishiraj0100/shapesinc-py/issues"
  },
  python_requires=">=3.8",
  license="MIT",
  url="https://github.com/Rishiraj0100/shapesinc-py"
)
