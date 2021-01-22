#!/bin/sh

echo 'stop docker images...'
docker-compose -f docker/docker-compose.yaml down --volumes

echo 'remove cache/*...'
rm -rf cache/*

echo 'remove conf/*...'
rm -rf conf/*

echo 'remove organizations/*...'
rm -rf organizations/*
