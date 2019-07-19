'''
LUKSCTL
'''

from setuptools import setup
import ast, os, re
import sys

SOURCE_DIR = "luksctl"

#______________________________________
def readme():
    with open('README.rst') as f:
        return f.read()

#______________________________________
def is_virtual():
  """
  Return if we run in a virtual environtment.
  Check supports venv && virtualenv
  """
  return (getattr(sys, 'base_prefix', sys.prefix) != sys.prefix or hasattr(sys, 'real_prefix'))

#______________________________________
def get_config_dir():
  path='/etc/luks'
  if is_virtual() is True:
    path = sys.prefix + '/etc/luks/'
  return path

#______________________________________
with open('%s/__init__.py' % SOURCE_DIR, 'rb') as f:
  init_contents = f.read().decode('utf-8')

  def get_var(var_name):
    pattern = re.compile(r'%s\s+=\s+(.*)' % var_name)
    match = pattern.search(init_contents).group(1)
    return str(ast.literal_eval(match))

  version = get_var("__version__")

#______________________________________
setup(
  name='luksctl',
  version=version,
  description='luks volume management',
  long_description=readme(),
  url='https://github.com/mtangaro/luksctl',
  author='Marco Antonio Tangaro, Federico Zambelli',
  author_email='ma.tangaro@ibiom.cnr.it', 
  license='GPL-3.0',
  packages=['luksctl'],
  classifiers=[
    'Development Status :: 1 - Beta',
    'Topic :: Utilities',
    'License :: OSI Approved :: MIT License',
  ],
  keywords='LUKS',
  scripts=['bin/luksctl'],
  data_files=[
    (get_config_dir(), ['config/luks-cryptdev.ini.sample']),
  ],
)
