#! /bin/bash

set -x

cd ../functions/FileServiceTCPSTriggerFunction/ || exit
echo "Deleting the tests directory"
rm -r tests
echo "Done"