from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')


class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "0.5.0"
        self.company_name = "No Company"
        self.copyright = "no copyright"
        self.name = "py2exe sample files"


myservice = Target(
    # used for the versioninfo resource
    description = "A sample Windows NT service",
    # what to build.  For a service, the module name (not the
    # filename) must be specified!
    modules = ["pyth_svc_template"]
    )


setup(
    options = {'py2exe': {'bundle_files': 1}},
    service = [myservice],
    zipfile = None,
)
