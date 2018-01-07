"""
sloth
-----

sloth is a tool for labeling image and video data for computer vision research.

The documentation can be found at http://sloth.readthedocs.org/ .

"""
import os
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
import sloth


# the following installation setup is based on django's setup.py
def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages = []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
sloth_dir = 'sloth'

for dirpath, dirnames, filenames in os.walk(sloth_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))

package_data = {'sloth.gui' : ['labeltool.ui', 'icons/*']}

setup(name='sloth',
      version=sloth.VERSION,
      description='The Sloth Labeling Tool',
      author='CV:HCI Research Group',
      url='http://sloth.readthedocs.org/',
      requires=['importlib', 'PyQt4', 'numpy'],
      packages=packages,
      package_data=package_data,
      scripts=['sloth/bin/sloth']
)
