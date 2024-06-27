#!/bin/bash
# Start the package phase, this is inside the batch job container, set the flag to make sure such phase is only run once
if [ ! -f /opt/ml/code/.packaged ]; then
    python /opt/ml/code/model_pack.py
    touch /opt/ml/code/.packaged
fi

# Wait for the package phase to complete
wait -n

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