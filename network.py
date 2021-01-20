import os
import subprocess
import shutil
import sys
import tarfile
import yaml

ENV_PATH = os.getenv('PATH')
os.environ['PATH'] = os.getcwd() + '/bin:' + ENV_PATH
os.environ['FABRIC_CFG_PATH'] = './conf'

g_conf = None
with open('env.yaml') as f:
    g_conf = yaml.safe_load(f)

g_domain = g_conf['domain']
g_org = g_conf['org']
g_peer = g_conf['peer']
g_channel = g_conf['channel']

mode = sys.argv[1]

def setup():
    # install binaries
    files = os.listdir('bin')
    files = [ f for f in files if not f.startswith('.') ]
    if not files:
        subprocess.call('script/install-fabric.sh binary', shell=True)

    # install docker images
    subprocess.call('script/install-fabric.sh docker', shell=True)

def deploy():
    arcfile = f'/tmp/organizations.tar.gz'
    docker_compose_file = f'/tmp/docker-compose.yaml'
    configtx_conf_file = '/tmp/configtx.yaml'
    core_conf_file = '/tmp/core.yaml'

    # extract the fabric configuration files
    if not os.path.exists(arcfile):
        print(f'{arcfile} is not found...')
        return
    with tarfile.open(arcfile, 'r') as tar:
        tar.extractall()

    # copy the docker-compose configuration file
    if not os.path.exists(docker_compose_file):
        print(f'{docker_compose_file} is not found...')
        return
    shutil.copyfile(docker_compose_file, f'docker/docker-compose.yaml')

    # copy the configtx configuration file
    if not os.path.exists(configtx_conf_file):
        print(f'{configtx_conf_file} is not found...')
        return
    shutil.copyfile(configtx_conf_file, 'conf/configtx.yaml')

    # copy the configtx configuration file
    if not os.path.exists(core_conf_file):
        print(f'{core_conf_file} is not found...')
        return
    shutil.copyfile(core_conf_file, 'conf/core.yaml')

def network_up():
    subprocess.call('docker-compose -f docker/docker-compose.yaml up -d', shell=True)

if mode == 'setup':
    setup()
elif mode == 'deploy':
    deploy()
elif mode == 'up':
    network_up()
elif mode == 'all':
    deploy()
    network_up()

