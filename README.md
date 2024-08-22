# Android APK Automation Testing with Appium DOCKER VERSION

A Django application designed to automate the testing of APK files on Android devices using Appium.

## Table of Contents

- [Setup Docker](#setup-docker)
- [Clone the Project](#clone-the-project)
- [Update Email Configuration](#update-email-configuration)
- [Run the Project](#run-the-project)
- [Create an AVD Model](#create-an-avd-model)
- [Run Appium](#run-appium)
- [Application Guidance](#application-guidance)


##  Setup Docker
1. Download Docker from - [Docker's official website](https://docs.docker.com/engine/install/)  .
2. Install Docker on your system.
3. Ensure Docker is Running:
 - Make sure Docker Desktop is running on your PC.

##  Clone the Project
Clone the repository using the following command:

   ```sh
    git clone -b master --single-branch https://github.com/mego354/Automation-Testing.git
   ```

## Update Email Configuration
Update the Email credentials in project/app/core/settings.py
   ```python
   EMAIL_HOST_USER = 'example@gmail.com'  # Replace with your EMAIL account
   EMAIL_HOST_PASSWORD = 'examplepass'  # Replace with your SMTP password 
   ```
you can get SMTP password from gmail 

## Run the Project
1. Change the directory to the project path:
   ```sh
    cd path/to/project
   ```

2. Build and Start the Containers:
   ```sh
    docker-compose up --build
   ```

This command will:

- Build the Docker images as defined in your Dockerfile.
- Set up and run the Django app and MySQL database as defined in your docker-compose.yml.
- Start the Django development server on http://localhost:8000.
- Make Appium available on http://localhost:4723.

3. Run migrations:

   ```sh
   docker-compose exec web python manage.py migrate
   ```

4. Create a superuser:

   ```sh
   docker-compose exec web python manage.py createsuperuser
   ```

5. Restart the Django development server:

   ```sh
   docker-compose down
   docker-compose up --build -d
   ```

6. Access the app at http://localhost:8000/admin to log in with the superuser credentials.

7. Create an AVD Model:
    - Go to the AVD model in the Django admin panel.
    - Create a new AVD entry with the following details:
    - Name: The name of the device (e.g., Pixel_7_Pro_API_33).
    - SDK Root Path: The SDK root path of your device.
    - Appium Link: http://localhost:4723.


Once the server is running, you can enter the app route, create applications, and run the automation tests as desired.

## Application Guidance

### Testing:
before using the application you can check the application:
1. Open  project/automation/tests.py
2. Edit lines 133, 134, 135 with the credentials of the craeted AVD Model from before
4. run the test using `docker-compose exec web python manage.py test`

### usage:
# this version is not done yet wait for next update
    


