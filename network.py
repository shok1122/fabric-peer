import os
import subprocess
import shutil
import sys
import tarfile

ENV_PATH = os.getenv('PATH')
os.environ['PATH'] = os.getcwd() + '/bin:' + ENV_PATH
os.environ['FABRIC_CFG_PATH'] = './conf'

mode = sys.argv[1]

def install():
    # install binaries
    files = os.listdir('bin')
    files = [ f for f in files if not f.startswith('.') ]
    if not files:
        subprocess.call('script/install-fabric.sh binary', shell=True)

    # install docker images
    subprocess.call('script/install-fabric.sh docker', shell=True)

def deploy(arcfile, docker_compose_file):
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
    shutil.copyfile(docker_compose_file, f'docker/{os.path.basename(docker_compose_file)}')

if mode == 'install':
    install()
elif mode == 'deploy':
    deploy(sys.argv[2], sys.argv[3])

