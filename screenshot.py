import subprocess
import time
import datetime
import os

def list_open_windows_mac():
    """Returns a list of all user-facing applications currently running."""
    try:
        result = subprocess.check_output([
            "osascript", "-e",
            'tell application "System Events" to get name of (processes where background only is false)'
        ])
        return result.decode().strip().split(", ")
    except subprocess.CalledProcessError:
        return ["Error fetching open windows"]

def get_current_active_app():
    """Returns the name of the currently active application."""
    try:
        result = subprocess.check_output([
            "osascript", "-e",
            'tell application "System Events" to get name of first application process whose frontmost is true'
        ])
        return result.decode().strip()
    except subprocess.CalledProcessError:
        return None

def activate_application(app_name):
    """Activates the specified application by name."""
    if app_name == "Electron":
        app_name = "Code"
    subprocess.run(["osascript", "-e", f'tell application "{app_name}" to activate'])
    time.sleep(1)

def generate_screenshot_filename(app_name, window_only=True):
    """Generates a timestamped filename for the screenshot."""
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    kind = "window" if window_only else "full"
    safe_name = app_name.replace(" ", "_")
    return f"screenshots/{safe_name}_{kind}_{now}.png"

def capture_window_screenshot(window_id, filename):
    """Captures a screenshot of a specific window using its ID."""
    subprocess.run(["screencapture", "-l", window_id, filename])
    # print(f"✅ Screenshot of window saved to: {os.path.abspath(filename)}")
    return os.path.abspath(filename)

def capture_fullscreen_screenshot(filename):
    """Captures a full-screen screenshot."""
    subprocess.run(["screencapture", filename])
    # print(f"✅ Full screen screenshot saved to: {os.path.abspath(filename)}")
    return os.path.abspath(filename)

def get_window_id(app_name):
    """Attempts to get the window ID of the frontmost window of the application."""
    script = f'''
    tell application "System Events"
        set appProc to first application process whose name is "{app_name}"
        try
            set winID to id of front window of appProc
        on error
            return "error"
        end try
    end tell
    return winID
    '''
    try:
        window_id = subprocess.check_output(["osascript", "-e", script]).decode().strip()
        return window_id if window_id != "error" else None
    except subprocess.CalledProcessError:
        return None

def screenshot_active_window(app_name):
    """Captures a screenshot of the active window or full screen if the window capture fails."""
    # Save the currently active app
    previous_app = get_current_active_app()
    # Activate the target app
    activate_application(app_name)
    # Prepare output filenames
    window_output_file = generate_screenshot_filename(app_name, window_only=True)
    full_output_file = generate_screenshot_filename(app_name, window_only=False)
    # Ensure the 'screenshots' directory exists
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    # Try to capture the front window
    window_id = get_window_id(app_name)
    if window_id:
        screenshot_path = capture_window_screenshot(window_id, window_output_file)
    else:
        # print(f"⚠️ Could not capture window for '{app_name}' — falling back to full screen.")
        screenshot_path = capture_fullscreen_screenshot(full_output_file)

    # Switch back to the previous active app
    if previous_app:
        activate_application(previous_app)
    
    return screenshot_path

def list_open_apps():
    """Returns a list of open applications."""
    apps = list_open_windows_mac()
    if not apps or "Error" in apps[0]:
        print("❌ Could not get open applications.")
        return None
    
    print("Open Applications:")
    for i, app in enumerate(apps):
        print(f"[{i}] {app}")
    return apps

def get_user_choice(num_choices):
    """Gets the user's app choice and returns it."""
    try:
        choice = int(input("\nSelect an app to capture by number: "))
        if 0 <= choice < num_choices:
            return choice
        else:
            print("❌ Invalid selection.")
            return None
    except ValueError:
        print("❌ Invalid selection.")
        return None

def display_open_apps_and_select():
    """Displays the list of open applications and allows the user to select one."""
    apps = list_open_apps()
    if apps is None:
        return None

    choice = get_user_choice(len(apps))
    
    if choice is not None:
        return apps[choice]
    return None

def main():
    """Main function to drive the screenshot capture process."""
    apps = list_open_apps()
    if apps is None:
        return None

    choice = get_user_choice(len(apps))
    
    if apps[choice]:
        screenshot_path = screenshot_active_window(apps[choice])
        print(f"file saved to :{screenshot_path}")

    
if __name__ == "__main__":
    main()
