import os
import subprocess
import shutil
import sys
import tarfile
import yaml

ENV_PATH = os.getenv('PATH')
os.environ['PATH'] = os.getcwd() + '/bin:' + ENV_PATH
os.environ['FABRIC_CFG_PATH'] = './conf'

global_conf = None
with open('env.yaml') as f:
    global_conf = yaml.safe_load(f)

g_domain = global_conf['domain']
g_org = global_conf['org']
g_peer = global_conf['peer']

mode = sys.argv[1]

def install():
    # install binaries
    files = os.listdir('bin')
    files = [ f for f in files if not f.startswith('.') ]
    if not files:
        subprocess.call('script/install-fabric.sh binary', shell=True)

    # install docker images
    subprocess.call('script/install-fabric.sh docker', shell=True)

def deploy():
    arcfile = f'/tmp/{g_peer}-{g_org}.{g_domain}.tar.gz'
    docker_compose_file = f'/tmp/docker-compose-{g_peer}-{g_org}.{g_domain}.yaml'
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

def network_up():
    subprocess.call('docker-compose -f docker/docker-compose.yaml up -d', shell=True)

if mode == 'install':
    install()
elif mode == 'deploy':
    deploy()
elif mode == 'up':
    network_up()
elif mode == 'all':
    deploy()
    network_up()

