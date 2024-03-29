import os
import subprocess
import sys
import yaml
import json
import time

g_conf_peer = None
with open('cache/config-peer.yaml') as f:
    g_conf_peer = yaml.safe_load(f)

g_conf_net = None
with open('cache/config-network.yaml') as f:
    g_conf_net = yaml.safe_load(f)

g_orderer_domain = g_conf_net['orderer']['domain']

FABRIC_CFG_PATH = os.environ['FABRIC_CFG_PATH']

g_path_orderer_ca = f'{FABRIC_CFG_PATH}/organizations/ordererOrganizations/{g_orderer_domain}/orderers/orderer.{g_orderer_domain}/msp/tlscacerts/tlsca.{g_orderer_domain}-cert.pem'

def call(command):
    start = time.time()
    subprocess.call(command, shell=True)
    elapsed_time = time.time() - start
    return elapsed_time

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

def queryinstalled():
    print('------------------------------------')
    print(' queryinstalled')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode queryinstalled \
            --output json"
    call(command)

def querycommitted(channel):
    print('------------------------------------')
    print(' querycommitted')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode querycommitted \
            --channelID {channel} \
            --output json"
    call(command)

def approve(channel, chaincode_name, version, sequence, package_id, init_required):
    print('------------------------------------')
    print(' approve for my org')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode approveformyorg \
            --orderer orderer.{g_orderer_domain}:7050 \
            --tls \
            --cafile {g_path_orderer_ca} \
            --channelID {channel} \
            --name {chaincode_name} \
            --version {version} \
            --sequence {sequence} \
            --package-id {package_id}"
    if init_required == "true":
        command = command + " --init-required"
    call(command)

def check_commit_readiness(channel, chaincode_name, version, sequence, init_required):
    print('------------------------------------')
    print(' check commit readiness')
    print('------------------------------------')
    command = f" \
        peer lifecycle chaincode checkcommitreadiness \
            --orderer orderer.{g_orderer_domain}:7050 \
            --tls \
            --cafile {g_path_orderer_ca} \
            --channelID {channel} \
            --name {chaincode_name} \
            --version {version} \
            --sequence {sequence}"

    if init_required == "true":
        command = command + " --init-required"
    call(command)

def commit(channel, chaincode_name, version, sequence, init_required):
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
            --channelID {channel} \
            --name {chaincode_name} \
            --version {version} \
            --sequence {sequence} \
            {peer_addr_list} \
            {tls_root_cert_list}"
    if init_required == "true":
        command = command + "--init-required"
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

def query(channel, chaincode_name, chaincode_func, chaincode_args):

    args = {}
    args["function"] = chaincode_func
    args["Args"] = chaincode_args

    args_text = json.dumps(args)

    command = f"\
        peer chaincode query \
            --channelID {channel} \
            --name {chaincode_name} \
            --ctor '{args_text}'"
    elapsed_time = call(command)
    print(f'query (func:{chaincode_func}, time:{elapsed_time}, args:{chaincode_args})')

def invoke(channel, chaincode_name, chaincode_func, chaincode_args, init_flag):

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

    command = f"\
        peer chaincode invoke \
            --channelID {channel} \
            --tls \
            --orderer orderer.{g_orderer_domain}:7050 \
            --cafile {g_path_orderer_ca} \
            {opt_peerAddresses} \
            {opt_tlsRootCertFiles} \
            {opt_isInit} \
            --waitForEvent \
            --name {chaincode_name} \
            --ctor '{args_text}'"
    elapsed_time = call(command)
    print(f'invoke (func:{chaincode_func}, time:{elapsed_time}, args:{chaincode_args})')

def init_ledger(channel, chaincode_name):
    invoke(channel, chaincode_name, "InitLedger", [], True)

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
        channel = sys.argv[3]
        chaincode_name = sys.argv[4]
        version = sys.argv[5]
        sequence = sys.argv[6]
        package_id = sys.argv[7]
        init_required = sys.argv[8]
        approve(channel, chaincode_name, version, sequence, package_id, init_required)
    elif subopt == 'commit':
        channel = sys.argv[3]
        chaincode_name = sys.argv[4]
        version = sys.argv[5]
        sequence = sys.argv[6]
        init_required = sys.argv[7]
        commit(channel, chaincode_name, version, sequence, init_required)
    elif subopt == 'get-package':
        package_id = sys.argv[3]
        peer_name = sys.argv[4]
        peer_domain = sys.argv[5]
        get_installed_package(package_id, peer_name, peer_domain)
    elif subopt == 'query':
        channel = sys.argv[3]
        chaincode_name = sys.argv[4]
        chaincode_func = sys.argv[5]
        chaincode_args = sys.argv[6:]
        query(channel, chaincode_name, chaincode_func, chaincode_args)
    elif subopt == 'invoke':
        channel = sys.argv[3]
        chaincode_name = sys.argv[4]
        chaincode_func = sys.argv[5]
        chaincode_args = sys.argv[6:]
        invoke(channel, chaincode_name, chaincode_func, chaincode_args, False)
    elif subopt == 'init-ledger':
        channel = sys.argv[3]
        chaincode_name = sys.argv[4]
        init_ledger(channel, chaincode_name)
elif opt == 'check':
    subopt = sys.argv[2]
    if subopt == 'commit-readiness':
        channel = sys.argv[3]
        chaincode_name = sys.argv[4]
        version = sys.argv[5]
        sequence = sys.argv[6]
        init_required = sys.argv[7]
        check_commit_readiness(channel, chaincode_name, version, sequence, init_required)
    elif subopt == 'installed-package':
        queryinstalled()
    elif subopt == 'committed-package':
        channel = sys.argv[3]
        querycommitted(channel)
