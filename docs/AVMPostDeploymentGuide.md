# AVM Post Deployment Guide

This document provides guidance on post-deployment steps after deploying the Document Generation Solution Accelerator from the AVM(Azure Verified Modules).
 
 ---

### Add Sample data
1. Clone the Repository
    First, clone this repository to access the post-deployment scripts:
    ```bash
    git clone https://github.com/microsoft/document-generation-solution-accelerator.git
    ```
    ```bash
    cd document-generation-solution-accelerato
    ```

2. Import Sample Data -Run bash command printed in the terminal. The bash command will look like the following:

    ```bash 
    ./infra/scripts/process_sample_data.sh <resourceGroupName> 
    ```
    If the deployment does not exist or has been deleted – The script will prompt you to manually enter the required values

1. Add App Authentication

    > Note: Authentication changes can take up to 10 minutes

    Follow steps in [App Authentication](https://github.com/microsoft/document-generation-solution-accelerator/blob/psl-postdeployentscript-new/docs/AppAuthentication.md) to configure authentication in app service.

1. Deleting Resources After a Failed Deployment

    Follow steps in [Delete Resource Group](https://github.com/microsoft/document-generation-solution-accelerator/blob/psl-postdeployentscript-new/docs/DeleteResourceGroup.md) if your deployment fails and/or you need to clean up the resources.

    
