
import os
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

# Confirm that specific packages and versions are installed

@pytest.mark.parametrize("name,version", [
    ("nginx", "1.21"),
])

def test_packages(host, name, version):
    pkg = host.package(name)
    assert pkg.is_installed
    assert pkg.version.startswith(version)


def test_nginx_running_and_enabled(host):
    nginx = host.service("nginx")
    assert nginx.is_running
    assert nginx.is_enabled


# Test that app.conf is present and has expected permissions
@pytest.mark.parametrize("filename,owner,group,mode", [
    ("/etc/nginx/nginx.conf", "root", "root", 0o644),
])

def test_file(host, filename, owner, group, mode):
    target = host.file(filename)
    assert target.exists
    assert target.user == owner
    assert target.group == group
    assert target.mode == mode


def test_if_nginx_conf_contains_configuration(host):
    conf_file = host.file('/etc/nginx/conf.d/default.conf')

    assert conf_file.contains('listen       80;')
    assert conf_file.contains('index  index.html index.htm;')

def test_logrotate_conf(host):
    conf = host.file('/etc/logrotate.d/nginx').content
    assert b'rotate 14' in conf
    assert b'/var/log/nginx/*.log' in conf
