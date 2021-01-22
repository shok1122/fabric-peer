import os
import subprocess
import sys
import yaml

g_conf = None
with open('env.yaml') as f:
    g_conf = yaml.safe_load(f)

g_orderer_domain = g_conf['orderer']['domain']
g_channel = g_conf['channel']

FABRIC_CFG_PATH = os.environ['FABRIC_CFG_PATH']

g_path_orderer_ca = f'{FABRIC_CFG_PATH}/organizations/ordererOrganizations/{g_orderer_domain}/orderers/orderer.{g_orderer_domain}/msp/tlscacerts/tlsca.{g_orderer_domain}-cert.pem'

def install(package_name, cc_path):

    pwd = os.getcwd()
    os.chdir(cc_path)

    print('------------------------------------')
    print(' vendoring')
    print('------------------------------------')
    command = f" \
            go mod init"
    subprocess.call(command, shell=True)
    command = f" \
            GO111MODULE=on go mod vendor"
    subprocess.call(command, shell=True)

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
    subprocess.call(command, shell=True)

    print('------------------------------------')
    print(' install chaincode')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode install \
            cache/{package_name}.tar.gz"
    subprocess.call(command, shell=True)

    print('------------------------------------')
    print(' queryinstalled')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode queryinstalled \
            --output json"
    subprocess.call(command, shell=True)

def instantiate(chaincode_name, version, package_id):
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
    subprocess.call(command, shell=True)

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
    subprocess.call(command, shell=True)

mode = sys.argv[1]

if mode == 'install':
    package_name = sys.argv[2]
    cc_path = sys.argv[3]
    install(package_name, cc_path)
elif mode == 'instantiate':
    chaincode_name = sys.argv[2]
    version = sys.argv[3]
    package_id = sys.argv[4]
    instantiate(chaincode_name, version, package_id)
elif mode == 'check-commit-readiness':
    chaincode_name = sys.argv[2]
    version = sys.argv[3]
    check_commit_readiness(chaincode_name, version)

