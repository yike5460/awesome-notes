#!/bin/bash

# Launch model serving in background
nohup python /opt/ml/code/model.py & 

# Launch metric collection in background
nohup python /opt/ml/code/collect_gpu_metrics.py &

# Keep the script running to prevent container exit  
tail -f /dev/null
