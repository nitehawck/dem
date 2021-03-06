import unittest

import mock
from dem.dependency.yum import RpmInstaller
from dem.project.cache import PackageCache


class TestRpmInstaller(unittest.TestCase):
    @mock.patch('subprocess.call')
    def test_will_install_package_with_yum_if_not_found_in_remote(self, mock_subprocess):
        cache = mock.MagicMock(spec=PackageCache)
        cache.is_package_installed.return_value = False
        packages = [{'name': 'package', 'version': '1.3.0'}]
        installer = RpmInstaller(packages, cache)
        installer.install_packages()

        mock_subprocess.assert_called_once_with(['sudo', 'yum', 'install', 'package-1.3.0', '-y'])

    @mock.patch('subprocess.call')
    def test_will_install_all_packages_correctly(self, mock_subprocess):
        cache = mock.MagicMock(spec=PackageCache)
        cache.is_package_installed.return_value = False
        packages = [{'name': 'package', 'version': '1.3.0'},
                    {'name': 'package4', 'version': '0.3.0'}]
        installer = RpmInstaller(packages, cache)
        installer.install_packages()

        mock_subprocess.assert_any_call(['sudo', 'yum', 'install', 'package-1.3.0', '-y'])
        mock_subprocess.assert_any_call(['sudo', 'yum', 'install', 'package4-0.3.0', '-y'])

    @mock.patch('subprocess.call')
    def test_will_not_install_rpm_if_already_installed(self, mock_subprocess):
        cache = mock.MagicMock(spec=PackageCache)
        cache.is_package_installed.return_value = True
        packages = [{'name': 'package', 'version': '1.3.0'},
                    {'name': 'package4', 'version': '0.3.0'}]
        installer = RpmInstaller(packages, cache)
        installer.install_packages()
        mock_subprocess.assert_not_called()

    @mock.patch('subprocess.call')
    def test_will_not_add_version_if_version_is_latest(self, mock_subprocess):
        cache = mock.MagicMock(spec=PackageCache)
        cache.is_package_installed.return_value = False
        packages = [{'name': 'package', 'version': 'latest'},
                    {'name': 'package2', 'version': '0.3.0'}]
        installer = RpmInstaller(packages, cache)
        installer.install_packages()

        mock_subprocess.assert_any_call(['sudo', 'yum', 'install', 'package', '-y'])
        mock_subprocess.assert_any_call(['sudo', 'yum', 'install', 'package2-0.3.0', '-y'])

if __name__ == '__main__':
    unittest.main()
