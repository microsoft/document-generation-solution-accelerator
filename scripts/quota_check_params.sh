#!/bin/bash

# Default Models and Capacities (Comma-separated)
DEFAULT_MODELS="gpt-4o,text-embedding-ada-002,gpt-4"
DEFAULT_CAPACITY="30,80,30"  # Each model will be paired with a capacity in order

# Convert the comma-separated strings into arrays
IFS=',' read -r -a MODEL_NAMES <<< "$DEFAULT_MODELS"
IFS=',' read -r -a CAPACITIES <<< "$DEFAULT_CAPACITY"

# Default Regions to check (Comma-separated, now configurable)
DEFAULT_REGIONS="eastus,uksouth,eastus2,northcentralus,swedencentral,westus,westus2,southcentralus,canadacentral"
IFS=',' read -r -a DEFAULT_REGION_ARRAY <<< "$DEFAULT_REGIONS"  # Split into an array

# Read parameters (if any)
IFS=',' read -r -a MODEL_CAPACITY_PAIRS <<< "$1"  # Split the comma-separated model and capacity pairs into an array
USER_REGION="$2"

# If no parameters are passed, use default models and regions
if [ ${#MODEL_CAPACITY_PAIRS[@]} -lt 1 ]; then
    echo "No parameters provided, using default models: ${MODEL_NAMES[*]} with respective capacities: ${CAPACITIES[*]}"
    # Use default models and their respective capacities
    for i in "${!MODEL_NAMES[@]}"; do
        MODEL_CAPACITY_PAIRS+=("${MODEL_NAMES[$i]}:${CAPACITIES[$i]}")
    done
else
    echo "Using provided model and capacity pairs: ${MODEL_CAPACITY_PAIRS[*]}"
fi

# Extract model names and required capacities into arrays
declare -a FINAL_MODEL_NAMES
declare -a FINAL_CAPACITIES

for PAIR in "${MODEL_CAPACITY_PAIRS[@]}"; do
    MODEL_NAME=$(echo "$PAIR" | cut -d':' -f1)
    CAPACITY=$(echo "$PAIR" | cut -d':' -f2)

    if [ -z "$MODEL_NAME" ] || [ -z "$CAPACITY" ]; then
        echo "❌ ERROR: Invalid model and capacity pair '$PAIR'. Both model and capacity must be specified."
        exit 1
    fi

    FINAL_MODEL_NAMES+=("$MODEL_NAME")
    FINAL_CAPACITIES+=("$CAPACITY")
done

echo "🔄 Using Models: ${FINAL_MODEL_NAMES[*]} with respective Capacities: ${FINAL_CAPACITIES[*]}"

echo "🔄 Fetching available Azure subscriptions..."
SUBSCRIPTIONS=$(az account list --query "[?state=='Enabled'].{Name:name, ID:id}" --output tsv)
SUB_COUNT=$(echo "$SUBSCRIPTIONS" | wc -l)

if [ "$SUB_COUNT" -eq 1 ]; then
    # If only one subscription, automatically select it
    AZURE_SUBSCRIPTION_ID=$(echo "$SUBSCRIPTIONS" | awk '{print $2}')
    echo "✅ Using the only available subscription: $AZURE_SUBSCRIPTION_ID"
else
    # If multiple subscriptions exist, prompt the user to choose one
    echo "Multiple subscriptions found:"
    echo "$SUBSCRIPTIONS" | awk '{print NR")", $1, "-", $2}'

    while true; do
        echo "Enter the number of the subscription to use:"
        read SUB_INDEX

        # Validate user input
        if [[ "$SUB_INDEX" =~ ^[0-9]+$ ]] && [ "$SUB_INDEX" -ge 1 ] && [ "$SUB_INDEX" -le "$SUB_COUNT" ]; then
            AZURE_SUBSCRIPTION_ID=$(echo "$SUBSCRIPTIONS" | awk -v idx="$SUB_INDEX" 'NR==idx {print $2}')
            echo "✅ Selected Subscription: $AZURE_SUBSCRIPTION_ID"
            break
        else
            echo "❌ Invalid selection. Please enter a valid number from the list."
        fi
    done
fi

# Set the selected subscription
az account set --subscription "$AZURE_SUBSCRIPTION_ID"
echo "🎯 Active Subscription: $(az account show --query '[name, id]' --output tsv)"

# Check if the user provided a region, if not, use the default regions
if [ -n "$USER_REGION" ]; then
    echo "🔍 User provided region: $USER_REGION"
    IFS=',' read -r -a REGIONS <<< "$USER_REGION"  # Split into an array using comma
else
    echo "No region specified, using default regions: ${DEFAULT_REGION_ARRAY[*]}"
    REGIONS=("${DEFAULT_REGION_ARRAY[@]}")
fi

echo "✅ Retrieved Azure regions. Checking availability..."
declare -a TABLE_ROWS
INDEX=1

VALID_REGIONS=()
for REGION in "${REGIONS[@]}"; do
    echo "----------------------------------------"
    echo "🔍 Checking region: $REGION"

    # Fetch quota information for the region
    QUOTA_INFO=$(az cognitiveservices usage list --location "$REGION" --output json)
    if [ -z "$QUOTA_INFO" ]; then
        echo "⚠️ WARNING: Failed to retrieve quota for region $REGION. Skipping."
        continue
    fi

    # Initialize a flag to track if all models have sufficient quota in the region
    ALL_MODELS_AVAILABLE=true

    for index in "${!FINAL_MODEL_NAMES[@]}"; do
        MODEL_NAME="${FINAL_MODEL_NAMES[$index]}"
        REQUIRED_CAPACITY="${FINAL_CAPACITIES[$index]}"

        echo "🔍 Checking model: $MODEL_NAME with required capacity: $REQUIRED_CAPACITY"

        # Extract model quota information
        MODEL_INFO=$(echo "$QUOTA_INFO" | awk -v model="\"value\": \"OpenAI.Standard.$MODEL_NAME\"" '
            BEGIN { RS="},"; FS="," }
            $0 ~ model { print $0 }
        ')

        if [ -z "$MODEL_INFO" ]; then
            echo "⚠️ WARNING: No quota information found for model: OpenAI.Standard.$MODEL_NAME in $REGION. Skipping."
            ALL_MODELS_AVAILABLE=false
            break  # If any model is not available, no need to check further for this region
        fi

        CURRENT_VALUE=$(echo "$MODEL_INFO" | awk -F': ' '/"currentValue"/ {print $2}' | tr -d ',' | tr -d ' ')
        LIMIT=$(echo "$MODEL_INFO" | awk -F': ' '/"limit"/ {print $2}' | tr -d ',' | tr -d ' ')

        CURRENT_VALUE=${CURRENT_VALUE:-0}
        LIMIT=${LIMIT:-0}

        CURRENT_VALUE=$(echo "$CURRENT_VALUE" | cut -d'.' -f1)
        LIMIT=$(echo "$LIMIT" | cut -d'.' -f1)

        AVAILABLE=$((LIMIT - CURRENT_VALUE))

        echo "✅ Model: OpenAI.Standard.$MODEL_NAME | Used: $CURRENT_VALUE | Limit: $LIMIT | Available: $AVAILABLE"

        # Check if quota is sufficient
        if [ "$AVAILABLE" -lt "$REQUIRED_CAPACITY" ]; then
            echo "❌ ERROR: 'OpenAI.Standard.$MODEL_NAME' in $REGION has insufficient quota. Required: $REQUIRED_CAPACITY, Available: $AVAILABLE"
            echo "➡️  To request a quota increase, visit: https://aka.ms/oai/stuquotarequest"
            ALL_MODELS_AVAILABLE=false
        else
            TABLE_ROWS+=("$(printf "| %-4s | %-20s | %-35s | %-10s | %-10s | %-10s |" "$INDEX" "$REGION" "$MODEL_NAME" "$LIMIT" "$CURRENT_VALUE" "$AVAILABLE")")

            INDEX=$((INDEX + 1))
        fi
    done

    # If all models have sufficient quota, add region to valid regions
    if [ "$ALL_MODELS_AVAILABLE" = true ]; then
        echo "✅ All models have sufficient quota in $REGION."
        VALID_REGIONS+=("$REGION")
    fi
done

# Print table header
echo "----------------------------------------------------------------------------------------------------------"
printf "| %-4s | %-20s | %-35s | %-10s | %-10s | %-10s |\n" "No." "Region" "Model Name" "Limit" "Used" "Available"
echo "----------------------------------------------------------------------------------------------------------"

for ROW in "${TABLE_ROWS[@]}"; do
    echo "$ROW"
done

echo "----------------------------------------------------------------------------------------------------------"
echo "➡️  To request a quota increase, visit: https://aka.ms/oai/stuquotarequest"
echo "✅ Script completed."