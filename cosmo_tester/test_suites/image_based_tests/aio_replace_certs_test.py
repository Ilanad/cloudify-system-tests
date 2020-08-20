from os.path import join, dirname

from cosmo_tester.framework.examples import get_example_deployment


def test_aio_replace_certs(image_based_manager, ssh_key, logger, test_config):
    example = get_example_deployment(
        image_based_manager, ssh_key, logger, 'aio_replace_certs', test_config)
    example.upload_and_verify_install()
    _validate_agents(image_based_manager, example.tenant)

    _create_new_certs(image_based_manager)
    replace_certs_config_path = '~/certificates_replacement_config.yaml'
    _create_replace_certs_config_file(image_based_manager,
                                      replace_certs_config_path,
                                      ssh_key.private_key_path)

    image_based_manager.run_command('cfy certificates replace -i {0} '
                                    '-v'.format(replace_certs_config_path))

    _validate_agents(image_based_manager, example.tenant)
    example.uninstall()


def _create_new_certs(manager):
    key_path = join('~', '.cloudify-test-ca',
                    manager.private_ip_address + '.key')
    manager.run_command('cfy_manager generate-test-cert -s {0},{1}'.format(
        manager.private_ip_address, manager.ip_address))
    manager.run_command('chmod 444 {0}'.format(key_path), use_sudo=True)


def _create_replace_certs_config_file(manager,
                                      replace_certs_config_path,
                                      local_ssh_key_path):
    script_name = 'aio_create_replace_certs_config_script.py'
    remote_script_path = '/tmp/' + script_name
    remote_ssh_key_path = '~/.ssh/ssh_key.pem'

    manager.put_remote_file(remote_ssh_key_path, local_ssh_key_path)
    manager.run_command('cfy profiles set --ssh-user {0} --ssh-key {1}'.format(
        manager.username, remote_ssh_key_path))

    manager.put_remote_file(remote_script_path,
                            join(dirname(__file__), script_name))
    command = '/opt/cfy/bin/python {0} --output {1} --host-ip {2}'.format(
        remote_script_path, replace_certs_config_path,
        manager.private_ip_address)
    manager.run_command(command)


def _validate_agents(manager, tenant):
    validate_agents = manager.run_command(
        'cfy agents validate --tenant-name {}'.format(tenant)).stdout
    assert 'Task succeeded' in validate_agents
