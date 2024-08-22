# Use Ubuntu as the base image
FROM ubuntu:20.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk wget unzip curl && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y build-essential libssl-dev libffi-dev python3-dev default-libmysqlclient-dev pkg-config

# Install Node.js and Appium
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g appium --unsafe-perm=true && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Android SDK
RUN mkdir -p /opt/android-sdk/cmdline-tools && \
    cd /opt/android-sdk/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip && \
    unzip commandlinetools-linux-8512546_latest.zip && \
    rm commandlinetools-linux-8512546_latest.zip && \
    mkdir latest && \
    mv cmdline-tools/* latest/ && \
    rmdir cmdline-tools

# Set Android SDK environment variables
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools/bin"

# Install platform-tools
RUN yes | sdkmanager --sdk_root=/opt/android-sdk "platform-tools"

# Set the working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . /app/

# Expose the port your app runs on
EXPOSE 8000

# Command to run the application
CMD ["python3", "app/manage.py", "runserver", "0.0.0.0:8000"]
