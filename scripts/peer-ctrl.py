import os
import subprocess
import sys
import yaml
import json

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

def get_anchor_addr_list():
    addr_list = []
    for org in g_conf_net['orgs']:
        peer_domain = org['domain']
        if peer_domain == g_conf_peer['domain']:
            continue
        peer_name = org['peers'][0]['name']
        addr_list.append(
            {
                "name": peer_name,
                "domain": peer_domain,
                "port": "7051"
            }
        )
    return addr_list

def get_tls_root_cert_path(peer_name, peer_domain):
    return f"{FABRIC_CFG_PATH}/organizations/peerOrganizations/{peer_domain}/peers/{peer_name}.{peer_domain}/tls/ca.crt"

def help():
    print('Usage: peer-ctrl.py [opt] [args...]')

def create_channel(channel_name):
    print('------------------------------------')
    print(' create channel')
    print('------------------------------------')
    command = f"\
        configtxgen \
            -profile SampleSingleMSPChannel \
            -outputCreateChannelTx ./channel-artifacts/{channel_name}.tx \
            -channelID {channel_name}"
    call(command)

    command = f"\
        peer channel create \
            --channelID {channel_name} \
            --file ./channel-artifacts/{channel_name}.tx \
            --tls \
            --orderer orderer.{g_orderer_domain}:7050 \
            --cafile {g_path_orderer_ca}"
    call(command)

def join_channel(channel_name):
    print('------------------------------------')
    print(' join channel')
    print('------------------------------------')
    command = f"\
        peer channel fetch 0 ./channel-artifacts/{channel_name}.block \
            --channelID {channel_name} \
            --tls \
            --orderer orderer.{g_orderer_domain}:7050 \
            --cafile {g_path_orderer_ca}"
    call(command)

    command = f"\
        peer channel join \
            --blockpath ./channel-artifacts/{channel_name}.block"
    call(command)

def packaging(package_name, cc_dir_name):

    pwd = os.getcwd()

    cc_path = f"src/{cc_dir_name}"
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
            --path {cc_dir_name} \
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

def queryinstalled():
    print('------------------------------------')
    print(' queryinstalled')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode queryinstalled \
            --output json"
    call(command)

def querycommitted():
    print('------------------------------------')
    print(' querycommitted')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode querycommitted \
            --channelID {g_channel} \
            --output json"
    call(command)

def approve(chaincode_name, version, sequence, package_id):
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
            --sequence {sequence} \
            --init-required \
            --package-id {package_id}"
    call(command)

def check_commit_readiness(chaincode_name, version, sequence):
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
            --sequence {sequence} \
            --init-required"
    call(command)

def commit(chaincode_name, version, sequence):
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
            --sequence {sequence} \
            --init-required \
            {peer_addr_list} \
            {tls_root_cert_list}"
    call(command)

def get_installed_package(package_id, peer_name, peer_domain):
    print( '---------------------------------------------------')
    print(f' get installed package')
    print( '---------------------------------------------------')
    tls_root_cert_path = get_tls_root_cert_path(peer_name, peer_domain)
    command = f"\
        peer lifecycle chaincode getinstalledpackage \
            --package-id {package_id} \
            --output-directory ./cache \
            --tls \
            --peerAddresses {peer_name}.{peer_domain}:7051 \
            --tlsRootCertFiles {tls_root_cert_path}"
    call(command)

def query(chaincode_name, chaincode_func, chaincode_args):

    args = {}
    args["function"] = chaincode_func
    args["Args"] = chaincode_args

    args_text = json.dumps(args)

    print( '---------------------------------------------------')
    print(f' query: {chaincode_func}')
    print( '---------------------------------------------------')
    command = f"\
        peer chaincode query \
            --channelID {g_channel} \
            --name {chaincode_name} \
            --ctor '{args_text}'"
    call(command)

def invoke(chaincode_name, chaincode_func, chaincode_args, init_flag):

    args = {}
    args["function"] = chaincode_func
    args["Args"] = chaincode_args

    args_text = json.dumps(args)

    addr_list = get_anchor_addr_list()

    list_peerAddresses = []
    list_tlsRootCertFiles = []
    for x in addr_list:
        list_peerAddresses.append(f"--peerAddresses {x['name']}.{x['domain']}:{x['port']}")
        tls_root_cert_path = get_tls_root_cert_path(x['name'], x['domain'])
        list_tlsRootCertFiles.append(f"--tlsRootCertFiles {tls_root_cert_path}")
    opt_peerAddresses = ' '.join(list_peerAddresses)
    opt_tlsRootCertFiles = ' '.join(list_tlsRootCertFiles)

    opt_isInit = ""
    if init_flag:
        opt_isInit = "--isInit"

    print( '---------------------------------------------------')
    print(f' invoke: {chaincode_func}')
    print( '---------------------------------------------------')
    command = f"\
        peer chaincode invoke \
            --channelID {g_channel} \
            --tls \
            --orderer orderer.{g_orderer_domain}:7050 \
            --cafile {g_path_orderer_ca} \
            {opt_peerAddresses} \
            {opt_tlsRootCertFiles} \
            {opt_isInit} \
            --name {chaincode_name} \
            --ctor '{args_text}'"
    call(command)

def init_ledger(chaincode_name):
    invoke(chaincode_name, "InitLedger", [], True)

opt = sys.argv[1]

if opt == 'help':
    help()
elif opt == 'channel':
    subopt = sys.argv[2]
    if subopt == 'create':
        channel_name = sys.argv[3]
        create_channel(channel_name)
    elif subopt == 'join':
        channel_name = sys.argv[3]
        join_channel(channel_name)
elif opt == 'cc':
    subopt = sys.argv[2]
    if subopt == 'packing':
        package_name = sys.argv[3]
        cc_dir_name = sys.argv[4]
        packaging(package_name, cc_dir_name)
    elif subopt == 'install':
        package_path = sys.argv[3]
        install(package_path)
    elif subopt == 'approve':
        chaincode_name = sys.argv[3]
        version = sys.argv[4]
        sequence = sys.argv[5]
        package_id = sys.argv[6]
        approve(chaincode_name, version, sequence, package_id)
    elif subopt == 'commit':
        chaincode_name = sys.argv[3]
        version = sys.argv[4]
        sequence = sys.argv[5]
        commit(chaincode_name, version, sequence)
    elif subopt == 'get-package':
        package_id = sys.argv[3]
        peer_name = sys.argv[4]
        peer_domain = sys.argv[5]
        get_installed_package(package_id, peer_name, peer_domain)
    elif subopt == 'query':
        chaincode_name = sys.argv[3]
        chaincode_func = sys.argv[4]
        chaincode_args = sys.argv[5:]
        query(chaincode_name, chaincode_func, chaincode_args)
    elif subopt == 'invoke':
        chaincode_name = sys.argv[3]
        chaincode_func = sys.argv[4]
        chaincode_args = sys.argv[5:]
        invoke(chaincode_name, chaincode_func, chaincode_args, False)
    elif subopt == 'init-ledger':
        chaincode_name = sys.argv[3]
        init_ledger(chaincode_name)
elif opt == 'check':
    subopt = sys.argv[2]
    if subopt == 'commit-readiness':
        chaincode_name = sys.argv[3]
        version = sys.argv[4]
        sequence = sys.argv[5]
        check_commit_readiness(chaincode_name, version, sequence)
    elif subopt == 'installed-package':
        queryinstalled()
    elif subopt == 'committed-package':
        querycommitted()
