#/bin/sh

if [ "go" = "$1" ]; then
    pushd cache
    wget https://golang.org/dl/go1.11.13.linux-amd64.tar.gz
    tar zxf go1.11.13.linux-amd64.tar.gz
    sudo rm -rf /usr/local/go-1.11
    sudo mv go /usr/local/go-1.11
    popd > /dev/null
    echo "export GOPATH=$PWD/chaincode" > ~/.gosettings
    echo "export GOROOT=/usr/local/go-1.11" >> ~/.gosettings
    echo 'export PATH=$GOROOT/bin:$PATH' >> ~/.gosettings
    echo ""
    echo 'Created ~/.gosettings successfully.'
    echo 'You should call ~/.gosettings in ~/.bashrc with `source`'
fi

