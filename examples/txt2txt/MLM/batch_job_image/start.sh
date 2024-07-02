#!/bin/bash

# Start the model server
python /opt/ml/code/model.py &

# Start the GPU metrics collection once the model server is running, customize the health check endpoint if needed
while true; do
    if curl http://localhost:8080/ping; then
        break
    fi
    sleep 1
done

python /opt/ml/code/collect_gpu_metrics.py &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?