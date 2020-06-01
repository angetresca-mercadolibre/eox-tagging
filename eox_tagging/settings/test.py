"""
Test Django settings for eox_tagging project.
"""

from __future__ import unicode_literals

from .common import *  # pylint: disable=wildcard-import


class SettingsClass(object):
    """ dummy settings class """

    pass


SETTINGS = SettingsClass()
# This is executing the plugin_settings method imported from common module
plugin_settings(SETTINGS)
vars().update(SETTINGS.__dict__)
INSTALLED_APPS = vars().get("INSTALLED_APPS", [])
TEST_INSTALLED_APPS = [
    "django.contrib.sites",
]
for app in TEST_INSTALLED_APPS:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)


def plugin_settings(settings):  # pylint: disable=function-redefined, unused-argument
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    pass
