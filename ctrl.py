import os
import subprocess
import shutil
import sys
import tarfile
import yaml
from jinja2 import Template, Environment, FileSystemLoader

ENV_PATH = os.getenv('PATH')
os.environ['PATH'] = os.getcwd() + '/bin:' + ENV_PATH
os.environ['FABRIC_CFG_PATH'] = './conf'

g_conf_peer = None
g_domain = None
g_org = None
g_peer = None

g_conf_net = None

def render(file_name, conf):
    env = Environment(loader=FileSystemLoader('template'))
    template = env.get_template(file_name)
    return template.render(conf)

def save_file(path, data):
    with open(path, 'w') as f:
        f.write(data)

def install():
    # install binaries
    files = os.listdir('bin')
    files = [ f for f in files if not f.startswith('.') ]
    if not files:
        subprocess.call('script/install-fabric.sh binary', shell=True)

    # install docker images
    subprocess.call('script/install-fabric.sh docker', shell=True)

def load_config_peer():
    global g_conf_peer
    global g_domain
    global g_org
    global g_peer

    if not os.path.isfile('cache/config-peer.yaml'):
        return

    with open('cache/config-peer.yaml') as f:
        g_conf_peer = yaml.safe_load(f)

    g_domain = g_conf_peer['domain']
    g_org = g_conf_peer['org']
    g_peer = g_conf_peer['peer']

def load_config_net():
    global g_conf_net

    if not os.path.isfile('cache/config-network.yaml'):
        return

    with open('cache/config-network.yaml') as f:
        g_conf_net = yaml.safe_load(f)

def deploy():
    arcfile = f'/tmp/organizations.tar.gz'
    docker_compose_file = f'/tmp/docker-compose.yaml'
    configtx_conf_file = '/tmp/configtx.yaml'
    core_conf_file = '/tmp/core.yaml'
    config_net_file = '/tmp/config-network.yaml'
    config_peer_file = '/tmp/config-peer.yaml'

    # extract the fabric configuration files
    if not os.path.exists(arcfile):
        print(f'{arcfile} is not found...')
        return False
    with tarfile.open(arcfile, 'r') as tar:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar)

    # copy the configtx configuration file
    if not os.path.exists(configtx_conf_file):
        print(f'{configtx_conf_file} is not found...')
        return False
    shutil.copyfile(configtx_conf_file, 'conf/configtx.yaml')

    # copy the core configuration file
    if not os.path.exists(core_conf_file):
        print(f'{core_conf_file} is not found...')
        return False
    shutil.copyfile(core_conf_file, 'conf/core.yaml')

    # copy the network configuration file
    if not os.path.exists(config_net_file):
        print(f'{config_net_file} is not found...')
        return False
    shutil.copyfile(config_net_file, 'cache/config-network.yaml')

    # copy the peer configuration file
    if not os.path.exists(config_peer_file):
        print(f'{config_peer_file} is not found...')
        return False
    shutil.copyfile(config_peer_file, 'cache/config-peer.yaml')

    # generate a docker-compose configuration file from the template
    with open('cache/config-peer.yaml') as f:
        peer_conf = yaml.safe_load(f)
        ret_text = render('docker-compose.yaml.tmpl', peer_conf)
        save_file('docker/docker-compose.yaml', ret_text)

    load_config_peer()
    load_config_net()

    return True

def network_up():
    subprocess.call('docker-compose -f docker/docker-compose.yaml up -d', shell=True)

def network_down():
    subprocess.call('docker-compose -f docker/docker-compose.yaml down', shell=True)

def clean():
    subprocess.call('rm -rf cache/*', shell=True)
    subprocess.call('rm -rf conf/*', shell=True)
    subprocess.call('rm -rf organizations/*', shell=True)

# -- ENTRYPOINT -- #

load_config_peer()
load_config_net()

mode = sys.argv[1]

is_success = True

if mode == 'install':
    install()
elif mode == 'deploy':
    is_success = deploy()
elif mode == 'up':
    network_up()
elif mode == 'down':
    network_down()
elif mode == 'all':
    is_success = deploy()
    network_up()
elif mode == 'clean':
    clean()

if not is_success:
    print("failure...")
    sys.exit(1)

sys.exit(0)
