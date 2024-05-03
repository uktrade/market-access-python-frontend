#!/bin/bash

# Initialize variables
target=""
target_url=""
is_headless=false # Default is false (not headless)
is_load_test=false # Default is false (not load test)
requirements_file="test_frontend/requirements.txt"
pytest_config_file="test_frontend/pytest.ini"

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
            --is-load-test)
                is_load_test="true"
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

# Update requirements file and pytest configuration file if it's a load test
if [ "$is_load_test" = "true" ]; then
    requirements_file="test_frontend_load/requirements.txt"
    pytest_config_file="test_frontend_load/pytest.ini"
fi

# Install python dependencies from the chosen requirements file
pip install -r $requirements_file

if [ -z "$target_url" ]; then
    echo "Error: No target URL specified."
    exit 1
fi

# Conditionally set configuration and run tests
if [ "$is_load_test" = "true" ]; then
    # load testing with Playwright and pytest
    PWDEBUG=0 BASE_FRONTEND_TESTING_URL="$target_url" TEST_HEADLESS="$is_headless" pytest -c $pytest_config_file "test_frontend_load/$target"
else
    # Normal end-to-end testing with Playwright and pytest
    PWDEBUG=0 BASE_FRONTEND_TESTING_URL="$target_url" TEST_HEADLESS="$is_headless" pytest -c $pytest_config_file "test_frontend/$target"
fi

# Deactivate python virtual environment
deactivate
