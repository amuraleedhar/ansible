# -*- coding: utf-8 -*-
#
# Copyright: (c) 2017, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import pytest
import sys

from nose.plugins.skip import SkipTest
if sys.version_info < (2, 7):
    raise SkipTest("F5 Ansible modules require Python >= 2.7")

from units.compat import unittest
from units.compat.mock import Mock
from units.compat.mock import patch
from ansible.module_utils.basic import AnsibleModule

try:
    from library.modules.bigip_gtm_global import ApiParameters
    from library.modules.bigip_gtm_global import ModuleParameters
    from library.modules.bigip_gtm_global import ModuleManager
    from library.modules.bigip_gtm_global import ArgumentSpec
    from library.module_utils.network.f5.common import F5ModuleError
    from library.module_utils.network.f5.common import iControlUnexpectedHTTPError
    from test.unit.modules.utils import set_module_args
except ImportError:
    try:
        from ansible.modules.network.f5.bigip_gtm_global import ApiParameters
        from ansible.modules.network.f5.bigip_gtm_global import ModuleParameters
        from ansible.modules.network.f5.bigip_gtm_global import ModuleManager
        from ansible.modules.network.f5.bigip_gtm_global import ArgumentSpec
        from ansible.module_utils.network.f5.common import F5ModuleError
        from ansible.module_utils.network.f5.common import iControlUnexpectedHTTPError
        from units.modules.utils import set_module_args
    except ImportError:
        raise SkipTest("F5 Ansible modules require the f5-sdk Python library")

fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except Exception:
        pass

    fixture_data[path] = data
    return data


class TestParameters(unittest.TestCase):
    def test_module_parameters(self):
        args = dict(
            synchronization=True,
            synchronization_group_name='foo',
            synchronize_zone_files=True
        )

        p = ModuleParameters(params=args)
        assert p.synchronization is True
        assert p.synchronization_group_name == 'foo'
        assert p.synchronize_zone_files is True

    def test_api_parameters(self):
        args = load_fixture('load_gtm_global_settings_general_1.json')

        p = ApiParameters(params=args)
        assert p.synchronization is False
        assert p.synchronization_group_name == 'default'
        assert p.synchronize_zone_files is False


@patch('ansible.module_utils.f5_utils.AnsibleF5Client._get_mgmt_root',
       return_value=True)
class TestManager(unittest.TestCase):

    def setUp(self):
        self.spec = ArgumentSpec()

    def update(self, *args):
        set_module_args(dict(
            synchronization="yes",
            synchronization_group_name='foo',
            synchronize_zone_files="yes",
            server='localhost',
            password='password',
            user='admin'
        ))

        current = ApiParameters(params=load_fixture('load_gtm_global_settings_general_1.json'))
        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )

        # Override methods in the specific type of manager
        mm = ModuleManager(module=module)
        mm.update_on_device = Mock(return_value=True)
        mm.read_current_from_device = Mock(return_value=current)

        results = mm.exec_module()

        assert results['changed'] is True
        assert results['synchronization'] == 'yes'
        assert results['synchronization_group_name'] == 'foo'
        assert results['synchronize_zone_files'] == 'yes'
