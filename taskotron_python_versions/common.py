import logging
import os

import rpm

log = logging.getLogger('python-versions')
log.setLevel(logging.DEBUG)
log.addHandler(logging.NullHandler())

BUG_URL = 'https://github.com/fedora-python/task-python-versions/issues'

TEMPLATE = """
{message}

Read the following document to find more information and a possible cause:
{info_url}
Or ask at #fedora-python IRC channel for help.

If you think the result is false or intentional, file a bug against:
{bug_url}

-----------
"""


def write_to_artifact(artifact, message, info_url):
    """Write failed check result details to atrifact."""
    with open(artifact, 'a') as f:
        f.write(TEMPLATE.format(
            message=message,
            info_url=info_url,
            bug_url=BUG_URL))


class PackageException(Exception):

    """Base Exception class for Package API."""


class Package(object):

    """RPM Package API."""

    def __init__(self, path):
        """Given the path to the RPM package, initialize
        the RPM package header containing its metadata.
        """
        self.filename = os.path.basename(path)
        self.path = path
        # To be populated in the first check.
        self.py_versions = None

        ts = rpm.TransactionSet()
        with open(path, 'rb') as fdno:
            try:
                self.hdr = ts.hdrFromFdno(fdno)
            except rpm.error as err:
                raise PackageException('{}: {}'.format(self.filename, err))

    @property
    def is_srpm(self):
        return self.filename.endswith('.src.rpm')

    @property
    def name(self):
        """Package name as a string."""
        return self.hdr[rpm.RPMTAG_NAME].decode()

    @property
    def nvr(self):
        """Package name and version as a string."""
        return self.hdr[rpm.RPMTAG_NVR].decode()

    @property
    def require_names(self):
        return self.hdr[rpm.RPMTAG_REQUIRENAME]

    @property
    def require_nevrs(self):
        return self.hdr[rpm.RPMTAG_REQUIRENEVRS]

    @property
    def files(self):
        """Package file names as a list of strings."""
        return [name.decode() for name in self.hdr[rpm.RPMTAG_FILENAMES]]
