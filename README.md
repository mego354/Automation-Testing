# Android APK Automation Testing with Appium

A Django application designed to automate the testing of APK files on Android devices using Appium.

## Table of Contents

- [Installation](#installation)
- [Creating an AVD](#creating-an-avd)
- [MySQL Setup](#mysql-setup)
- [Clone the Project](#clone-the-project)
- [Update Database Configuration](#update-database-configuration)
- [Run the Project](#run-the-project)
- [Create an AVD Model](#create-an-avd-model)
- [Run Appium](#run-appium)
- [Application Guidance](#application-guidance)

## Installation

To get started, install the following software:

### Java JDK (Java Development Kit)

1. Download the Java JDK from - [Oracle's official website](https://www.oracle.com/java/technologies/downloads/)  .
2. Install the Java JDK on your system.
3. Set the `JAVA_HOME` environment variable to `C:\Program Files\Java\jdk-22`.
4. Update the `PATH` system variable to include `C:\Program Files\Java\jdk-22\bin`.

### Android Studio and SDK

1. Download Android Studio from - [Android Studio's official website.](https://developer.android.com/studio) 
2. If you require emulators, consider downloading and installing Android Studio.
3. Set the `ANDROID_HOME` environment variable to point to your Android SDK directory.
4. Update the `PATH` system variable to include the following:
   - `%ANDROID_HOME%\tools`
   - `%ANDROID_HOME%\build-tools`
   - `%ANDROID_HOME%\platform-tools`

After you install and open Android Studio, install the Android API 35 SDK as follows:

1. In Android Studio Click Tools > SDK Manager.
2. In the SDK Platforms tab, expand the the Android API 35.
3. Click Apply > OK to download and install the selected packages.

### Node.js

1. Download and install Node.js from - [Node.js official website.](https://nodejs.org/en/learn/getting-started/how-to-install-nodejs) 
2. Update the `PATH` system variable to include `C:\Program Files\nodejs\`.

### Appium

1. Install Appium 2.0 by running the following command:
   ```sh
   npm i -g appium@next
   ```
2. Install Appium drivers:
   ```sh
    appium driver install uiautomator2
    appium driver install xcuitest
   ```

### MySQL

1. Download and install MySQL from - [MySQL official website.](https://www.mysql.com/downloads/) 
2. Update the PATH system variable to include C:\Program Files\MySQL\MySQL Server 8.0\bin.

### System Environment Variables
Ensure the following environment variables are correctly set on your system:

| Variable | Value |
| ------ | ------ |
| JAVA_HOME | C:\Program Files\Java\jdk-22 |
| ANDROID_HOME | C:\Users\YOUR_USER_NAME\AppData\Local\Android\Sdk |

PATH: Include the following paths in system variable path:
| Value |
| ------ |
| C:\Program Files\nodejs\ |
| C:\Program Files\Java\jdk-22\bin |
| C:\Program Files\MySQL\MySQL Server 8.0\bin |
| %ANDROID_HOME%\tools |
| %ANDROID_HOME%\build-tools |
| %ANDROID_HOME%\platform-tools |

## Creating an AVD
1. Open Android Studio.
2. Navigate to Tools > AVD Manager.
3. Click on Create Virtual Device.
4. Select a device definition (e.g., Pixel 7 Pro).
5. Choose a system image (API Level 35).
6. Complete the AVD creation process and copy the avd name (e.g., Pixel_7_Pro_API_33).

## MySQL Setup
1. Open MySQL Workbench.
2. Create a new connection.
3. Create a new schema for your project, e.g., django_db.
4. Create a user with all privilege:
   ```sh
    mysql -u root -p
   ```
enter the root's password
   ```sh
    CREATE USER 'username'@'host' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON *.* TO 'username'@'host' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
    exit
   ```

##  Clone the Project
1. Clone the repository using the following command:

   ```sh
    git clone https://github.com/mego354/automation-test.git
   ```

2. Update Database Configuration
Open project/core/settings.py.
Update the MySQL database connection settings:

   ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'automation_test_db',
            'USER': 'your_username',
            'PASSWORD': 'your_password',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }
   ```

## Run the Project
1. Change the directory to your project path:
   ```sh
    cd path/to/your/project
   ```

2. Run migrations:

   ```sh
    python manage.py migrate
   ```

3. Create a superuser:

   ```sh
    python manage.py createsuperuser
   ```

4. Start the Django development server:

   ```sh
    python manage.py runserver
   ```

5. Access the app at http://localhost:8000/admin to log in with the superuser credentials.

6. Create an AVD Model:
    - Go to the AVD model in the Django admin panel.
    - Create a new AVD entry with the following details:
    - Name: The name of the device (e.g., Pixel_7_Pro_API_33).
    - SDK Root Path: The SDK root path of your device.
    - Appium Link: http://localhost:4724.

7. Run Appium
Start the Appium server using the following command:

   ```sh
    appium -p 4724
   ```

Once the server is running, you can enter the app route, create applications, and run the automation tests as desired.

## Application Guidance
### Testing:
before using the application you can check the application using
   ```sh
    py manage.py test
   ```

### usage:
1. Run Appium with `appium -p 4724` and verify it's running by checking the logs.
2. Run the app with `py manage.py runserver`.
3. Open the login route at `http://127.0.0.1:8000/login/`.
4. Register a new account or log in with a previously created account.
5. Navigate to `Apps` from the navbar.
6. Click on `Create New App`.
7. Fill in the Name field and upload the APK file (only .apk files are accepted).
8. Test the app using the Run Test button.

###  Check Logs for Errors
Some errors you might encounter if the test does not go well:
1. Your device may not be able to handle the emulator. In this case, try running the test again.
2. The driver might be stuck; if so, restart the Django app. This issue is rare.

### Debugging the Test Process
To see what's happening under the hood:

1. Comment line 67 in project/automation/testing.
2. Uncomment line 64 in project/automation/testing.
3. Restart the server and start the app test again. This will allow you to observe the emulator while the test is running.


    


