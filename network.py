import os
import subprocess
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

def deploy(arcfile):
    if not os.path.exists(arcfile):
        print(f'{arcfile} is not found...')
        return
    with tarfile.open(arcfile, 'r') as tar:
        tar.extractall()

if mode == 'install':
    install()
elif mode == 'deploy':
    deploy(sys.argv[2])

