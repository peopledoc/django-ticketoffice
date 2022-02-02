# -*- coding: utf-8 -*-
"""Tests around project's distribution and packaging."""
import os
import unittest


tests_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(tests_dir)


class VersionTestCase(unittest.TestCase):
    """Various checks around project's version info."""
    def get_project_name(self):
        """Return project name."""
        return 'django-ticketoffice'

    def get_package_name(self):
        """Return package name."""
        return 'django_ticketoffice'

    def get_version(self, package):
        """Return project's version defined in package."""
        module = __import__(package, globals(), locals(), [], -1)
        return module.__version__

    def test_version_present(self):
        """:PEP:`396` - Project's package has __version__ attribute."""
        package_name = self.get_package_name()
        try:
            self.get_version(package_name)
        except ImportError:
            self.fail(f"{package_name}'s package has no __version__.")

    def test_version_match(self):
        """Package's __version__ matches pkg_resources info."""
        project_name = self.get_project_name()
        package_name = self.get_package_name()
        try:
            import pkg_resources
        except ImportError:
            self.fail('Cannot import pkg_resources module. It is part of '
                      'setuptools, which is a dependency of '
                      f'{project_name}.')
        distribution = pkg_resources.get_distribution(project_name)
        installed_version = self.get_version(package_name)
        registered_version = distribution.version
        self.assertEqual(registered_version, installed_version,
                         f'Version mismatch: {package_name}.__version__ '
                         f'is "{installed_version}" whereas pkg_resources '
                         f'tells "{registered_version}". You may need to run '
                         '``make develop`` to update the installed version in '
                         'development environment.')

    def test_version_file(self):
        """Project's __version__ matches VERSION file info."""
        package_name = self.get_package_name()
        version_file = os.path.join(project_dir, 'VERSION')
        installed_version = self.get_version(package_name)
        file_version = open(version_file).read().strip()
        self.assertEqual(file_version, installed_version,
                         f'Version mismatch: {package_name}.__version__ '
                         f'is "{installed_version}" whereas VERSION file '
                         f'tells "{file_version}". You may need to run '
                         '``make develop`` to update the installed version '
                         'in development environment.')
