#!/bin/bash

git fetch
git pull

# provide execute permission to deploy scripts
sudo chmod +x ./content-gen/scripts/deploy.sh
sudo chmod +x ./content-gen/scripts/local_dev.sh
sudo chmod +x ./content-gen/scripts/deploy.ps1
sudo chmod +x ./content-gen/scripts/local_dev.ps1
