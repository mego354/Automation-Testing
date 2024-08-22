import base64
import subprocess
import time
import os
from typing import Dict, Any

from appium import webdriver
from appium.options.common import AppiumOptions
from django.core.files.base import ContentFile
import xml.etree.ElementTree as ET

from .models import AVD


class AppiumTestAutomation:
    def __init__(self, avd):
        """
        Initializes the test automation with the given AVD instance.
        """
        self.avd = avd
        self.avd_name = avd.name
        self.sdk_root = avd.sdk_root
        self.server_url = avd.service_url

        # Paths to emulator, adb, and aapt tools
        self.emulator_path = os.path.join(self.sdk_root, "emulator", "emulator.exe")
        self.adb_path = os.path.join(self.sdk_root, "platform-tools", "adb.exe")
        self.aapt_path = os.path.join(self.sdk_root, "build-tools", "34.0.0", "aapt.exe")

        self.driver = None

    def update_avd_status(self, key, value):
        """
        Update the specified field (e.g., booted) of the AVD in the database and refresh the instance.
        """
        AVD.objects.filter(pk=self.avd.id).update(**{key: value})
        self.avd.refresh_from_db()

    def launch_avd(self):
        """
        Launches the Android Virtual Device (AVD) with no GUI and waits for it to boot.
        Updates the AVD status in the database.

        Returns:
            bool: True if the emulator boots successfully, False otherwise.
        """
        MAX_RETRIES = 6
        RETRY_DELAY = 10  # seconds

        # Check if the AVD is already running
        try:
            output = subprocess.check_output([self.adb_path, "shell", "getprop", "sys.boot_completed"]).decode("utf-8").strip()
            if output == "1":
                print(f"AVD '{self.avd_name}' is already running.")
                self.update_avd_status('booted', True)
                return True
        except subprocess.CalledProcessError:
            print(f"AVD '{self.avd_name}' is not running. Starting AVD...")

        self.update_avd_status('booted', False)

        try:
            # Start the emulator with -no-window to suppress GUI !!!!!!!!
            subprocess.Popen([self.emulator_path, "-avd", self.avd_name, "-no-window", "-no-audio", "-no-snapshot-load"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        except subprocess.CalledProcessError as e:
            print(f"Error starting emulator: {e}")
            return False

        try:
            subprocess.run([self.adb_path, "wait-for-device"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error waiting for device: {e}")
            return False

        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                output = subprocess.check_output([self.adb_path, "shell", "getprop", "sys.boot_completed"]).decode("utf-8").strip()
                if output == "1":
                    self.update_avd_status('booted', True)
                    return True
                time.sleep(RETRY_DELAY)
            except subprocess.CalledProcessError as e:
                print(f"Error checking emulator status: {e}")
            retry_count += 1

        return False

    def stop_avd(self):
        """
        Stops the Android Virtual Device (AVD) and ensures it is fully stopped, updating its status in the database.

        Returns:
            bool: True if the emulator stops successfully, False if the emulator was not launched.
        """
        try:
            result = subprocess.run([self.adb_path, "emu", "kill"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            was_launched = 'bye' in result.stdout.decode("utf-8").strip()
            time.sleep(3)  # Wait for emulator to be stopped
        except subprocess.CalledProcessError:
            was_launched = False

        print("Emulator is fully stopped.")
        self.update_avd_status('booted', False)
        return was_launched

    def start_driver(self, apk_path):
        """
        initializes a new Appium driver.

        Returns:
            True if ready, or False if an error occurs or the driver cannot be connected.
        """
        try:
            self.driver.quit()
        except:
            pass
        try:
            cap: Dict[str, Any] = {
                "platformName": "Android",
                "automationName": "UIAutomator2",
                "deviceName": self.avd_name,
                "app": apk_path,
                "autoGrantPermissions": True, 
            }
            self.driver = webdriver.Remote(self.server_url, options=AppiumOptions().load_capabilities(cap))
            return True
        except Exception as e:
            print(f"Error starting driver: {e}")
            return False

    def get_package_name(self, apk_path: str):
        """
        Retrieves the package name from the APK.

        Args:
            apk_path (str): Path to the APK file.

        Returns:
            str: Package name if retrieved successfully, None otherwise.
        """
        print("Retrieving package name from the APK...")
        result = subprocess.run([self.aapt_path, "dump", "badging", apk_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        package_name = None
        for line in output.splitlines():
            if "package: name=" in line:
                package_name = line.split("'")[1]
                break

        if package_name:
            print(f"Package name: {package_name}")
            return package_name
        else:
            print("Failed to retrieve package name.")
            return None

    def find_first_button(self, element):
        """
        Recursively finds the first clickable button element in the XML hierarchy.

        Args:
            element: XML element to search within.

        Returns:
            str: The resource ID of the first clickable button, or None if not found.
        """
        for child in element:
            try:
                clickable = child.attrib['clickable'] == 'true'
                resource_id = child.attrib['resource-id']
                if clickable and resource_id:
                    return resource_id
            except KeyError:
                pass

            found = self.find_first_button(child)
            if found is not None:
                return found
        return None

    def click_button(self, id: str):
        """
        Clicks a button with the given resource ID.

        Args:
            id (str): The resource ID of the button to click.
        """
        btn = self.driver.find_element("id", id)
        btn.click()

    def navigate_home(self):
        """
        Navigates to the home screen of the device.
        """
        print("Navigating to the home screen...")
        self.driver.press_keycode(3)  # Keycode 3 is HOME
        time.sleep(2)

    def open_app_drawer(self):
        """
        Opens the app drawer by simulating a swipe gesture.
        """
        print("Opening the app drawer...")
        subprocess.run([self.adb_path, "shell", "input", "swipe", "500", "1500", "500", "500"], check=True)  # Swipe up
        time.sleep(2)

    def uninstall_app(self, package_name: str):
        """
        Uninstalls the specified app from the device.

        Args:
            package_name (str): The package name of the app to uninstall.
        """
        if package_name:
            print(f"Uninstalling the app {package_name}...")
            subprocess.run([self.adb_path, "uninstall", package_name], check=True)
            print("App uninstalled.")
        else:
            print("Could not determine the package name. App was not uninstalled.")

    def save_screenshot(self, step: int, app_model):
        """
        Captures a screenshot and stores it in the model's image field.

        Args:
            step (int): The step number to differentiate screenshots.
            app_model: The model instance to update with the screenshot.
        """
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_name = f"screenshot_{step}.png"
        content_file = ContentFile(screenshot, screenshot_name)
        
        if step == 1:
            app_model.first_screen_screenshot_path.save(screenshot_name, content_file, save=True)
        elif step == 2:
            app_model.second_screen_screenshot_path.save(screenshot_name, content_file, save=True)

        return True

    def start_screen_recording(self):
        """
        Starts screen recording on the device.
        """
        print("Starting screen recording...")
        self.driver.start_recording_screen(videoFps=60)
        time.sleep(2)  # Give some time for the recording to start

    def stop_screen_recording(self, app_model):
        """
        Stops screen recording and saves the video to the model's field.

        Args:
            app_model: The model instance to update with the video recording.
        """
        print("Stopping screen recording...")
        recording_data = self.driver.stop_recording_screen()
        decoded_recording_data = base64.b64decode(recording_data)
        recording_name = "video.mp4"
        content_file = ContentFile(decoded_recording_data, recording_name)
        app_model.video_recording_path.save(recording_name, content_file, save=True)
        print(f"Screen recording saved at: {app_model.video_recording_path.path}")

    def saves_initial_page_ui(self, app_model, page_source):
        """
        saves page source to the model's field.

        """
        file_name = "ui_hierarchy.xml"
        content_file = ContentFile(page_source, file_name)
        app_model.ui_hierarchy.save(file_name, content_file, save=True)
        return True

        
    def run_test(self, app_model):
        """
        Executes the test automation workflow on the provided app model.

        Args:
            app_model: The model instance representing the application to test.

        Returns:
            dict: Test result status and any error cause if applicable.
        """
        apk_path = app_model.apk_file_path.path
        if not self.launch_avd():
            return {'status': 'error', 'cause': 'cannot launch the AVD'}

        if not self.start_driver(apk_path):
            return {'status': 'error', 'cause': 'cannot start the driver'}


        try:
            package_name = self.get_package_name(apk_path)
            self.start_screen_recording()
            self.save_screenshot(1, app_model)

            # save the ui in the DB
            initial_page_source = self.driver.page_source
            initial_page_root = ET.fromstring(initial_page_source)
            self.saves_initial_page_ui(app_model, initial_page_source)


            first_button_id = self.find_first_button(initial_page_root)
            self.click_button(first_button_id)
            time.sleep(5)
            self.save_screenshot(2, app_model)
            time.sleep(2)

            subsequent_page_source = self.driver.page_source
            subsequent_page_root = ET.fromstring(subsequent_page_source)
            action_taken = ET.tostring(initial_page_root) != ET.tostring(subsequent_page_root)

            self.navigate_home()
            time.sleep(1)
            self.stop_screen_recording(app_model)
            self.uninstall_app(package_name)

            self.driver.quit()
            print("Script completed.")
            print("----------------------------.")

            self.update_avd_status('booted', False)
            return {'status': 'success', 'action_taken': action_taken}

        except Exception as e:
            print(f"Error during the test execution: {e}")
            self.update_avd_status('booted', False)
            try:
                self.uninstall_app(package_name)
            finally:
                return {'status': 'error', 'cause': str(e)}

# Example usage:
# app = get_object_or_404(APP, slug=kwargs['slug'])
# avd = AVD.objects.order_by('-id').first()
# test = AppiumTestAutomation(avd)
# result = test.run_test(app) 
