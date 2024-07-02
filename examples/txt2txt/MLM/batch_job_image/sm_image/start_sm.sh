#!/bin/bash
# Start the package phase, this is inside the batch job container
python /opt/ml/code/model_pack.py

# Wait for the package phase to complete
wait -n

# Exit with status of process that exited first
exit $?