#! /bin/bash

set -x

cd ../functions/ || exit
mkdir -p coverage-reports
cd FileServiceTCPSTriggerFunction/ || exit
echo "Creating Virtual environment for FileServiceTCPSTriggerFunction"

python3 -m venv .env/
echo "Virtual environment created for FileServiceTCPSTriggerFunction"
source .env/bin/activate
echo "Venv activated"

echo "Installing requirements..."
pip install -r requirements_dev.txt
echo "Requirements installed for FileServiceTCPSTriggerFunction."

echo "Running coverage"
pwd=$(pwd)
coverage run --source="$pwd" --omit=*/.env/* -m pytest --junitxml=../test-reports/FileServiceTCPSTriggerFunction-test.xml
echo "Coverage run completed for FileServiceTCPSTriggerFunction. Saving the coverage xml file"

coverage xml -o ../coverage-reports/coverage-FileServiceTCPSTriggerFunction.xml
deactivate
echo "Done"