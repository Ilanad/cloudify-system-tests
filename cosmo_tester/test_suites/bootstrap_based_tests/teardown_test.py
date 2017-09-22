########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import pytest

from cosmo_tester.framework.cluster import CloudifyCluster

from . import hello_worlds  # noqa (pytest fixture imported)


pre_bootstrap_state = None


def test_teardown(cfy, manager, hello_worlds):  # noqa (pytest fixture, not redefinition of hello_worlds)
    for hello in hello_worlds:
        hello.verify_all()

    cfy.teardown('-f')
    current_state = _get_system_state(manager)
    diffs = {}

    for key in current_state:
        pre_bootstrap_set = set(pre_bootstrap_state[key])
        current_set = set(current_state[key])

        diff = current_set - pre_bootstrap_set
        if diff:
            diffs[key] = diff

    assert not diffs, 'The following entities were not removed: ' \
                      '{0}'.format(diffs)


@pytest.fixture(scope='module')
def manager(request, cfy, ssh_key, module_tmpdir, attributes, logger):
    """Bootstraps a cloudify manager on a VM in rackspace OpenStack."""
    # The preconfigure callback populates the files structure prior to the BS
    cluster = CloudifyCluster.create_bootstrap_based(
            cfy, ssh_key, module_tmpdir, attributes, logger,
            preconfigure_callback=_preconfigure_callback)

    yield cluster.managers[0]

    cluster.destroy()


def _preconfigure_callback(managers):
    global pre_bootstrap_state
    mgr = managers[0]
    pre_bootstrap_state = _get_system_state(mgr)

    # Some manual additions, as we know these files will be generated by the BS
    pre_bootstrap_state['yum packages'] += [
        'python-pip', 'libxslt', 'daemonize'
    ]
    pre_bootstrap_state['folders in /opt'] += ['python_NOTICE.txt', 'lib']
    pre_bootstrap_state['folders in /var/log'] += ['yum.log']
    pre_bootstrap_state['init_d service files (/etc/rc.d/init.d/)'] += [
        'logstash.rpmsave', 'jexec'
    ]


def _get_system_state(mgr):
    with mgr.ssh() as fabric:
        systemd = fabric.run('ls /usr/lib/systemd/system').split()
        init_d = fabric.run('ls /etc/rc.d/init.d/').split()
        sysconfig = fabric.run('ls /etc/sysconfig').split()
        opt_dirs = fabric.run('ls /opt').split()
        etc_dirs = fabric.run('ls /etc').split()
        var_log_dirs = fabric.run('ls /var/log').split()

        packages = fabric.run('rpm -qa').split()
        # Prettify the packages output
        packages = [package.rsplit('-', 2)[0] for package in packages]

        users = fabric.run('cut -d: -f1 /etc/passwd').split()
        groups = fabric.run('cut -d: -f1 /etc/group').split()

    return {
        'systemd service files (/usr/lib/systemd/system)': systemd,
        'init_d service files (/etc/rc.d/init.d/)': init_d,
        'service config files (/etc/sysconfig)': sysconfig,
        'folders in /opt': opt_dirs,
        'folders in /etc': etc_dirs,
        'folders in /var/log': var_log_dirs,
        'yum packages': packages,
        'os users': users,
        'os groups': groups
    }
