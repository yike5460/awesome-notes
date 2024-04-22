#!/bin/bash

# Check if containerd is installed
if ! command -v containerd &> /dev/null
then
    echo "containerd is not installed. Installing containerd..."
    # Install containerd
    sudo apt-get update
    sudo apt-get install -y containerd
fi

# Check if ctr-enc is installed
if ! command -v ctr-enc &> /dev/null
then
    echo "ctr-enc is not installed. Installing ctr-enc..."
    # Install ctr-enc
    sudo apt-get update
    sudo apt-get install -y golang-go
    go get github.com/containerd/cri/cmd/ctr-enc
    sudo mv ~/go/bin/ctr-enc /usr/local/bin/
fi

# Generate encryption keys
openssl genrsa -out mykey.pem 2048
openssl rsa -in mykey.pem -pubout -out mypubkey.pem

# Pull the container image
sudo ctr images pull docker.io/library/bash:latest

# Encrypt the container image
sudo ctr-enc images encrypt \
  --recipient jwe:mypubkey.pem \
  --platform linux/amd64 \
  docker.io/library/bash:latest bash.enc:latest

# Inspect the encrypted image
sudo ctr-enc images layerinfo --platform linux/amd64 bash.enc:latest

# Tag the encrypted image for Docker Hub
sudo ctr images tag bash.enc:latest yike5460/bash.enc:latest

# Log in to Docker Hub
echo "Please enter your Docker Hub password:"
read -s password
echo "$password" | sudo ctr images login -u yike5460 --password-stdin docker.io

# Push the encrypted image to Docker Hub
sudo ctr images push yike5460/bash.enc:latest

# Attempt to run the encrypted container without the private key
echo "Attempting to run the encrypted container without the private key..."
sudo ctr run --rm yike5460/bash.enc:latest test echo 'Hello World!'

# Check the exit status of the previous command
if [ $? -ne 0 ]; then
    echo "As expected, running the encrypted container without the private key failed."
else
    echo "Unexpected behavior: Running the encrypted container without the private key succeeded."
fi

# Run the encrypted container with the correct private key
echo "Running the encrypted container with the correct private key..."
sudo ctr run --rm --key mykey.pem yike5460/bash.enc:latest test echo 'Hello World!'

# Check the exit status of the previous command
if [ $? -eq 0 ]; then
    echo "As expected, running the encrypted container with the correct private key succeeded."
else
    echo "Unexpected behavior: Running the encrypted container with the correct private key failed."
fi
