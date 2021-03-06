import os
import unittest

import mock
import pyfakefs.fake_filesystem_unittest as fake_filesystem_unittest
from dem.dependency.pip import PipRunner
from dem.dependency.uninstaller import PackageUninstaller
from dem.project import reader as reader
from dem.project.cache import PackageCache

SAMPLE_YAML_CONTENT = '''
config:
    remote-locations:
        ['/opt',
        'http://github.com']
packages:
    qt:
        version: 4.8.6
        type: archive
    json:
        version: 1.9
        type: archive
'''

DIFFERENT_SAMPLE_YAML_CONTENT = '''
config:
    remote-locations:
        ['/opt',
        'http://github.com']
packages:
    qt:
        version: 4.8.6
        type: archive
    gcc:
        version: 5.2.1
        type: rpm
    git-python:
        version: 0.3.12
        type: pip
'''

SAMPLE_CACHE_CONTENT = '''
{
    "md5": "b084deb42d4daefe7c29d4eae24c2d2d",

    "packages":
    {
        "qt": {"version": "4.8.6", "type": "local", "install_locations": [".devenv/dependencies/qt"]},
        "json": {"version": "1.8", "type": "local", "install_locations": [".devenv/dependencies/json"]},
        "gcc": {"version": "5.2.0", "type": "system"},
        "git-python": {"version": "0.3.10", "type": "pip"}
    }
}
'''

class TestPackageUninstaller(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

        self._base_path = os.path.abspath('base_path')
        self._yaml_file = os.path.join(self._base_path, 'devenv.yaml')
        self._dev_env = os.path.join(self._base_path, '.devenv')
        self._deps = os.path.join(self._dev_env, 'dependencies')
        self._cache_file = os.path.join(self._dev_env, 'cache.json')

        self.setup_directories()

    @mock.patch('sys.platform', "win32")
    @mock.patch('dem.dependency.pip.PipRunner.remove')
    @mock.patch('subprocess.call')
    def test_will_remove_archive_packages_that_have_changed(self, mock_subprocess, mock_pip_runner):
        self.setup_files(SAMPLE_YAML_CONTENT, SAMPLE_CACHE_CONTENT)
        self.create_package('qt')
        self.create_package('json')
        cache = PackageCache('myProject', self._base_path)
        (config, packages) = reader.devenv_from_file(self._yaml_file)

        uninstaller = PackageUninstaller(cache, packages, mock_pip_runner)
        uninstaller.uninstall_changed_packages()

        self.assertFalse(os.path.exists(os.path.join(self._deps, 'json')))

    @mock.patch('sys.platform', "win32")
    @mock.patch('dem.dependency.pip.PipRunner.remove')
    @mock.patch('subprocess.call')
    def test_will_remove_archive_packages_that_have_been_removed(self, mock_subprocess, mock_pip_runner):
        self.setup_files(DIFFERENT_SAMPLE_YAML_CONTENT, SAMPLE_CACHE_CONTENT)
        self.create_package('qt')
        self.create_package('json')
        cache = PackageCache('myProject', self._base_path)
        (config, packages) = reader.devenv_from_file(self._yaml_file)

        uninstaller = PackageUninstaller(cache, packages, mock_pip_runner)
        uninstaller.uninstall_changed_packages()

        self.assertFalse(os.path.exists(os.path.join(self._deps, 'json')))

    @mock.patch('sys.platform', "win32")
    @mock.patch('dem.dependency.pip.PipRunner.remove')
    @mock.patch('subprocess.call')
    def test_will_call_yum_for_removed_system_packages(self, mock_subprocess, mock_pip_runner):
        self.setup_files(DIFFERENT_SAMPLE_YAML_CONTENT, SAMPLE_CACHE_CONTENT)
        self.create_package('qt')
        self.create_package('json')
        cache = PackageCache('myProject', self._base_path)
        (config, packages) = reader.devenv_from_file(self._yaml_file)

        uninstaller = PackageUninstaller(cache, packages, mock_pip_runner)
        uninstaller.uninstall_changed_packages()

        mock_subprocess.assert_called_once_with(['sudo', 'yum', 'remove', 'gcc', '-y'])

    @mock.patch('sys.platform', "win32")
    @mock.patch('dem.dependency.pip.PipRunner', spec=PipRunner)
    @mock.patch('subprocess.call')
    def test_will_call_pip_for_removed_system_packages(self, mock_subprocess, mock_pip_runner):
        self.setup_files(DIFFERENT_SAMPLE_YAML_CONTENT, SAMPLE_CACHE_CONTENT)
        self.create_package('qt')
        self.create_package('json')
        cache = PackageCache('myProject', self._base_path)
        (config, packages) = reader.devenv_from_file(self._yaml_file)

        uninstaller = PackageUninstaller(cache, packages, mock_pip_runner)
        uninstaller.uninstall_changed_packages()

        mock_pip_runner.remove.assert_called_once_with('git-python', '0.3.10')

    def setup_directories(self):
        self.fs.CreateDirectory(self._base_path)
        self.fs.CreateDirectory(self._dev_env)
        self.fs.CreateDirectory(self._deps)

    def setup_files(self, yaml_file_data, cache_file_data):
        self.fs.CreateFile(self._yaml_file, contents=yaml_file_data)
        self.fs.CreateFile(self._cache_file, contents=cache_file_data)

    def create_package(self, name):
        self.fs.CreateDirectory(os.path.join(self._deps, name))

if __name__ == '__main__':
    unittest.main()
