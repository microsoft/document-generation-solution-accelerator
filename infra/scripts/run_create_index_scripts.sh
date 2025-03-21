#!/bin/bash
echo "started the script"

# Variables
baseUrl="$1"
keyvaultName="$2"
managedIdentityClientId="$3"
requirementFile="requirements.txt"
requirementFileUrl=${baseUrl}"infra/scripts/index_scripts/requirements.txt"

echo "Script Started"

# Download the create_index and create table python files
curl --output "01_create_search_index.py" ${baseUrl}"infra/scripts/index_scripts/01_create_search_index.py"
curl --output "02_process_data.py" ${baseUrl}"infra/scripts/index_scripts/02_process_data.py"



# RUN apt-get update
# RUN apt-get install python3 python3-dev g++ unixodbc-dev unixodbc libpq-dev
# apk add python3 python3-dev g++ unixodbc-dev unixodbc libpq-dev
 
# # RUN apt-get install python3 python3-dev g++ unixodbc-dev unixodbc libpq-dev
# pip install pyodbc

# Download the requirement file
curl --output "$requirementFile" "$requirementFileUrl"

echo "Download completed"

#Replace key vault name 
sed -i "s/kv_to-be-replaced/${keyvaultName}/g" "01_create_search_index.py"
sed -i "s/mici_to-be-replaced/${managedIdentityClientId}/g" "01_create_search_index.py"
sed -i "s/kv_to-be-replaced/${keyvaultName}/g" "02_process_data.py"
sed -i "s/mici_to-be-replaced/${managedIdentityClientId}/g" "02_process_data.py"

pip install -r requirements.txt

python 01_create_search_index.py
python 02_process_data.py
