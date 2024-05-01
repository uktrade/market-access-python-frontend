#!/bin/bash

# Initialize variables
target=""
target_url=""
is_headless=false # Default is false (not headless)

# Function to parse arguments for flexibility
parse_args() {
    for arg in "$@"
    do
        case $arg in
            target=*)
                target="${arg#*=}"
                shift # Remove once we have processed it
                ;;
            target_url=*)
                target_url="${arg#*=}"
                shift # Remove once we have processed it
                ;;
            --is-headless)
                is_headless="true"
                shift # Remove once we have processed it
                ;;
            *)
                # Assume it's the target_url if target is already set
                if [ -n "$target" ] && [ -z "$target_url" ]; then
                    target_url="$arg"
                elif [ -z "$target" ]; then
                    target="$arg"
                fi
                shift
                ;;
        esac
    done
}

# Parse the input arguments
parse_args "$@"

# Activate python virtual environment
source .venv/bin/activate

# Install python dependencies if not already installed
pip install -r test_frontend/requirements.txt

if [ -z "$target_url" ]; then
    echo "Error: No target URL specified."
    exit 1
fi

# Run playwright with pytest
PWDEBUG=0 BASE_FRONTEND_TESTING_URL="$target_url" TEST_HEADLESS="$is_headless" pytest -c test_frontend/pytest.ini "test_frontend/$target"

# Deactivate python virtual environment
deactivate
