import os
import subprocess
import sys
import yaml

g_conf_peer = None
with open('cache/config-peer.yaml') as f:
    g_conf_peer = yaml.safe_load(f)

g_conf_net = None
with open('cache/config-network.yaml') as f:
    g_conf_net = yaml.safe_load(f)

g_orderer_domain = g_conf_net['orderer']['domain']
g_channel = g_conf_net['channel']

FABRIC_CFG_PATH = os.environ['FABRIC_CFG_PATH']

g_path_orderer_ca = f'{FABRIC_CFG_PATH}/organizations/ordererOrganizations/{g_orderer_domain}/orderers/orderer.{g_orderer_domain}/msp/tlscacerts/tlsca.{g_orderer_domain}-cert.pem'

def call(command):
    #print(command)
    subprocess.call(command, shell=True)

def get_tls_root_cert_path(peer_name, peer_domain):
    return f"{FABRIC_CFG_PATH}/organizations/peerOrganizations/{peer_domain}/peers/{peer_name}.{peer_domain}/tls/ca.crt"

def help():
    print('Usage: peer-ctrl.py [mode] [args...]')

def packaging(package_name, cc_path):

    pwd = os.getcwd()
    os.chdir(cc_path)

    print('------------------------------------')
    print(' vendoring')
    print('------------------------------------')
    command = f" \
            go mod init"
    call(command)
    command = f" \
            GO111MODULE=on go mod vendor"
    call(command)

    os.chdir(pwd)

    print('------------------------------------')
    print(' packaging chaincode')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode package \
            cache/{package_name}.tar.gz \
            --path {cc_path} \
            --lang golang \
            --label {package_name}"
    call(command)

def install(package_path):
    print('------------------------------------')
    print(' install chaincode')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode install {package_path}"
    call(command)

    print('------------------------------------')
    print(' queryinstalled')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode queryinstalled \
            --output json"
    call(command)

def approve(chaincode_name, version, package_id):
    print('------------------------------------')
    print(' approve for my org')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode approveformyorg \
            --orderer orderer.{g_orderer_domain}:7050 \
            --tls \
            --cafile {g_path_orderer_ca} \
            --channelID {g_channel} \
            --name {chaincode_name} \
            --version {version} \
            --init-required \
            --package-id {package_id}"
    call(command)

def check_commit_readiness(chaincode_name, version):
    print('------------------------------------')
    print(' check commit readiness')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode checkcommitreadiness \
            --orderer orderer.{g_orderer_domain}:7050 \
            --tls \
            --cafile {g_path_orderer_ca} \
            --channelID {g_channel} \
            --name {chaincode_name} \
            --version {version} \
            --init-required"
    call(command)

def commit(chaincode_name, version):
    print( '------------------------------------')
    print(f' commit chaincode ({chaincode_name})')
    print( '------------------------------------')
    peer_addr_list = []
    tls_root_cert_list = []
    for org in g_conf_net['orgs']:
        peer_domain = org['domain']
        peer_name = org['peers'][0]['name']
        peer_addr_list.append(f"--peerAddresses {peer_name}.{peer_domain}:7051")
        tls_root_cert_path = get_tls_root_cert_path(peer_name, peer_domain)
        tls_root_cert_list.append(f"--tlsRootCertFiles {tls_root_cert_path}")
    peer_addr_list = ' '.join(peer_addr_list)
    tls_root_cert_list = ' '.join(tls_root_cert_list )
    command = f"\
        peer lifecycle chaincode commit \
            --orderer orderer.{g_orderer_domain}:7050 \
            --tls \
            --cafile {g_path_orderer_ca} \
            --channelID {g_channel} \
            --name {chaincode_name} \
            --version {version} \
            --init-required \
            {peer_addr_list} \
            {tls_root_cert_list}"
    call(command)

def get_installed_package(package_id, peer_domain, peer_name):
    print( '---------------------------------------------------')
    print(f' get installed package ({chaincode_name})')
    print( '---------------------------------------------------')
    tls_root_cert_path = get_tls_root_cert_path(peer_name, peer_domain)
    command = f"\
        peer lifecycle chaincode getinstalledpackage \
            --package-id {package_id} \
            --output-directory ./cache \
            --peerAddresses {peer_name}.{peer_domain}:7051 \
            --tlsRootCertFiles {tls_root_cert_path}"
    call(command)

mode = sys.argv[1]

if mode == 'help':
    help()
elif mode == 'packaging':
    package_name = sys.argv[2]
    cc_path = sys.argv[3]
    packaging(package_name, cc_path)
elif mode == 'install':
    package_path = sys.argv[2]
    install(package_path)
elif mode == 'approve':
    chaincode_name = sys.argv[2]
    version = sys.argv[3]
    package_id = sys.argv[4]
    approve(chaincode_name, version, package_id)
elif mode == 'check-commit-readiness':
    chaincode_name = sys.argv[2]
    version = sys.argv[3]
    check_commit_readiness(chaincode_name, version)
elif mode == 'commit':
    chaincode_name = sys.argv[2]
    version = sys.argv[3]
    commit(chaincode_name, version)
elif mode == 'getinstalledpackage':
    package_id = sys.argv[2]
    get_installed_package(package_id)

