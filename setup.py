# Originally contributed by Lorne McIntosh.
# Modified by Eric Xu
# Modified by Jose Santiago Rodriguez

import subprocess
import os
from distutils.core import setup
from distutils.spawn import find_executable
from distutils.extension import Extension

def get_ipopt_executable():

    # Find ipopt executable
    ipopt_executable = None

    for executable in ["ipopt"]:
        ipopt_executable = find_executable(executable)
        if ipopt_executable is not None:
            # Check that SWIG version is ok
            output = subprocess.check_output([ipopt_executable, "-v"]).decode('utf-8')
            ipopt_version = output.replace("Ipopt", "")
            ipopt_version = ipopt_version.replace("\n", "")

    if ipopt_executable is None:
        raise OSError("Unable to find IPOPT.")
    print("Found IPOPT: %s (version %s)" % (ipopt_executable, ipopt_version))
    return ipopt_executable

ipopt_executable = get_ipopt_executable()
ipopt_bin = os.path.dirname(ipopt_executable)
ipopt_base = os.path.dirname(ipopt_bin)
IPOPT_DIR = ipopt_base


# NumPy is much easier to install than pyipopt,
# and is a pyipopt dependency, so require it here.
# We need it to tell us where the numpy header files are.
import numpy
numpy_include = numpy.get_include()

# I personally do not need support for lib64 but I'm keeping it in the code.
def get_ipopt_lib():
    for lib_suffix in ('lib', 'lib64'):
        d = os.path.join(IPOPT_DIR, lib_suffix)
        if os.path.isdir(d):
            return d

IPOPT_LIB = get_ipopt_lib()
if IPOPT_LIB is None:
    raise Exception('failed to find ipopt lib')

ipopt_include = os.path.join(ipopt_base, 'include', 'coin')
IPOPT_INC = ipopt_include

print("\tInclude directory: {}".format(ipopt_include))
print("\tLibraries directory: {}".format(IPOPT_LIB))

FILES = ['src/callback.c', 'src/pyipoptcoremodule.c']

# The extra_link_args is commented out here;
# that line was causing my pyipopt install to not work.
# Also I am using coinmumps instead of coinhsl.
pyipopt_extension = Extension(
        'pyipoptcore',
        FILES,
        #extra_link_args=['-Wl,--rpath','-Wl,'+ IPOPT_LIB],
        library_dirs=[IPOPT_LIB],
        libraries=[
            'ipopt', 'coinblas',
            #'coinhsl',
            'coinmumps',
            'coinmetis',
            'coinlapack','dl','m',
            ],
        include_dirs=[numpy_include, IPOPT_INC],
        )

setup(
        name="pyipopt",
        version="0.8",
        description="An IPOPT connector for Python",
        author="Eric Xu",
        author_email="xu.mathena@gmail.com",
        url="https://github.com/xuy/pyipopt",
        packages=['pyipopt'],
        package_dir={'pyipopt' : 'pyipoptpackage'},
        ext_package='pyipopt',
        ext_modules=[pyipopt_extension],
        )

