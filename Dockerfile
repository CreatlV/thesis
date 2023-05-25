# Use an official NVIDIA PyTorch base image
FROM nvidia/cuda:12.1.0-base-ubuntu22.04

# Set the working directory
WORKDIR /app

# Install Python, pip, and OpenSSH server
RUN apt-get update && \
    apt-get install -y python3 python3-pip openssh-server && \
    rm -rf /var/lib/apt/lists/*

# Configure SSH server with empty password for root
RUN mkdir /var/run/sshd && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitEmptyPasswords no/PermitEmptyPasswords yes/' /etc/ssh/sshd_config && \
    passwd -d root && \
    ssh-keygen -A

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the working directory contents into the container
COPY . .

# Make ports 80 and 22 available to the world outside this container
EXPOSE 80 22

# Define environment variable
ENV NAME World

# Run SSH server when the container launches
CMD /usr/sbin/sshd -D
