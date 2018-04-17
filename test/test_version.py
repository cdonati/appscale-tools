import unittest
from xml.etree import ElementTree

import yaml
from mock import MagicMock, mock_open, patch

from appscale.tools.admin_api.version import Version
from appscale.tools.custom_exceptions import AppEngineConfigException

SIMPLE_APP_YAML = """
runtime: python27
""".lstrip()

SIMPLE_AE_WEB_XML = """
<?xml version="1.0" encoding="utf-8"?>
<appengine-web-app xmlns="http://appengine.google.com/ns/1.0">
</appengine-web-app>
""".lstrip()


class TestVersion(unittest.TestCase):
  def test_from_yaml(self):
    # Ensure an exception is raised if runtime is missing.
    with self.assertRaises(AppEngineConfigException):
      Version.from_yaml({})

    # Ensure runtime string is parsed successfully.
    app_yaml = yaml.safe_load(SIMPLE_APP_YAML)
    version = Version.from_yaml(app_yaml)
    self.assertEqual(version.runtime, 'python27')

  def test_from_xml(self):
    # Check the default runtime string for Java apps.
    # TODO: This should be updated when the Admin API accepts 'java7'.
    appengine_web_xml = ElementTree.fromstring(SIMPLE_AE_WEB_XML)
    version = Version.from_xml(appengine_web_xml)
    self.assertEqual(version.runtime, 'java')

  def test_from_yaml_file(self):
    open_path = 'appscale.tools.admin_api.version.open'
    with patch(open_path, mock_open(read_data=SIMPLE_APP_YAML)):
      version = Version.from_yaml_file('/example/app.yaml')

    self.assertEqual(version.runtime, 'python27')

  def test_from_xml_file(self):
    tree = MagicMock()
    tree.getroot.return_value = ElementTree.fromstring(SIMPLE_AE_WEB_XML)
    with patch.object(ElementTree, 'parse', return_value=tree):
      version = Version.from_xml_file('/example/appengine-web.xml')

    self.assertEqual(version.runtime, 'java')

  def test_from_directory(self):
    # Ensure an exception is raised if there are no configuration candidates.
    shortest_path_func = 'appscale.tools.admin_api.version.shortest_directory_path'
    with patch(shortest_path_func, side_effect=lambda fn, path: None):
      with self.assertRaises(AppEngineConfigException):
        Version.from_directory('/example/guestbook')

    with patch(shortest_path_func,
               side_effect=lambda fn, path: '/example/guestbook/app.yaml'):
      open_path = 'appscale.tools.admin_api.version.open'
      with patch(open_path, mock_open(read_data=SIMPLE_APP_YAML)):
        version = Version.from_yaml_file('/example/app.yaml')

      self.assertEqual(version.runtime, 'python27')

  def test_from_contents(self):
    version = Version.from_contents(SIMPLE_APP_YAML, 'app.yaml')
    self.assertEqual(version.runtime, 'python27')

    version = Version.from_contents(SIMPLE_AE_WEB_XML, 'appengine-web.xml')
    self.assertEqual(version.runtime, 'java')
