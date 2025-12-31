#!/bin/bash

git fetch
git pull

# provide execute permission to deploy scripts
sudo chmod +x ./scripts/deploy.sh
sudo chmod +x ./scripts/local_dev.sh
