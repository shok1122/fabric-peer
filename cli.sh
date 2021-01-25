#!/bin/bash
#docker-compose -f docker/docker-compose.yaml exec cli python3 scripts/peer-ctrl.py "$@"
docker exec cli python3 scripts/peer-ctrl.py "$@"

