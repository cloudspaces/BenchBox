#!/bin/bash


echo "Install Impressions"

cd ~/workload_generator/external/impresions-code

make

echo "Building complete"

mv impressions ../impressions

echo "Replace Exisiting Impressions"

echo "Completed!"