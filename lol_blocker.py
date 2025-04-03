import psutil
import time
import datetime
import tkinter as tk
from tkinter import messagebox
import os
import sys

# --- Configuration ---
TARGET_PROCESS_NAME = "RiotClientServices.exe"  # The process name to block
ALLOWED_START_HOUR = 21  # 9 PM (24-hour format)
ALLOWED_END_HOUR = 1     # 1 AM (24-hour format) - Wraps around midnight
CHECK_INTERVAL_SECONDS = 3 # Check slightly more often
# --- End Configuration ---

# --- Global Variables ---
attempt_count = 0
# Initialize with yesterday's date to ensure the first check works correctly
last_check_date = datetime.date.today() - datetime.timedelta(days=1)
blocked_pids = set() # Keep track of PIDs we tried to terminate recently

def is_time_allowed():
    """Checks if the current time is within the allowed window."""
    now = datetime.datetime.now()
    current_hour = now.hour
    # Check if current hour is between start hour (inclusive) and midnight
    # OR if current hour is between midnight and end hour (exclusive)
    if (current_hour >= ALLOWED_START_HOUR) or (current_hour < ALLOWED_END_HOUR):
        return True
    else:
        return False

def show_popup(count):
    """Displays the 'Get to work' pop-up message."""
    try:
        root = tk.Tk()
        root.withdraw() # Hide the main tkinter window
        root.attributes("-topmost", True) # Try to bring messagebox to front
        messagebox.showinfo(
            "Access Denied",
            f"Get to work!\n\nLeague is blocked outside 9 PM - 1 AM.\nAttempts today: {count}"
        )
        root.destroy()
    except Exception as e:
        print(f"Error showing popup: {e}") # Log error if GUI fails

def check_and_block_process():
    """Checks for the target process and blocks it if outside allowed time."""
    global attempt_count, last_check_date, blocked_pids

    today = datetime.date.today()

    # --- Daily Reset Logic ---
    if today != last_check_date:
        print(f"Date changed to {today}. Resetting attempt count.")
        attempt_count = 0
        last_check_date = today
        blocked_pids.clear() # Clear recently blocked PIDs on day change

    # --- Blocking Logic ---
    if not is_time_allowed():
        processes_found_this_check = False
        current_pids = set()

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Store current PIDs to clean up blocked_pids set later
                current_pids.add(proc.info['pid'])

                # Check if process name matches (case-insensitive)
                if proc.info['name'].lower() == TARGET_PROCESS_NAME.lower():
                    pid = proc.info['pid']
                    # Check if we already tried blocking this specific process instance
                    if pid not in blocked_pids:
                        print(f"{datetime.datetime.now()}: Found {TARGET_PROCESS_NAME} (PID: {pid}) outside allowed hours. Blocking.")
                        processes_found_this_check = True
                        termination_success = False

                        # --- CHANGE: Attempt Termination FIRST ---
                        try:
                            p = psutil.Process(pid)
                            print(f"Attempting termination for PID: {pid}.")
                            p.terminate() # Ask politely first
                            # Optional: Check if it's still running after a very short delay and kill if needed
                            # time.sleep(0.1)
                            # if p.is_running( ):
                            #     print(f"Process {pid} still running after terminate, trying kill.")
                            #     p.kill()
                            termination_success = True # Assume success if no immediate error
                            blocked_pids.add(pid) # Add to set to prevent immediate re-blocking loop
                        except psutil.NoSuchProcess:
                            print(f"Process {pid} already exited before termination could be attempted.")
                            # We still count this as an attempt the user made
                            pass
                        except psutil.AccessDenied:
                            print(f"Access Denied when trying to terminate PID: {pid}. Run script as administrator?")
                            # Termination failed, but still count attempt and show popup
                        except Exception as e:
                            print(f"Error terminating process {pid}: {e}")
                            # Termination failed, but still count attempt and show popup

                        # --- THEN Increment Count and Show Popup ---
                        attempt_count += 1
                        print(f"Showing popup. Attempts today: {attempt_count}")
                        show_popup(attempt_count) # Show popup AFTER termination attempt

                        # Don't need to check for other instances in this same loop iteration
                        # If multiple launch very quickly, next check interval will catch them
                        break

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Ignore processes that ended prematurely or we can't access
                pass
            except Exception as e:
                print(f"Error processing process list: {e}")

        # Clean up the blocked_pids set - remove PIDs that no longer exist
        blocked_pids.intersection_update(current_pids)

    # --- End Blocking Logic ---


# --- Main Execution Loop ---
if __name__ == "__main__":
    print("--- League Time Blocker Script Started (v2 - Terminate First) ---")
    print(f"Monitoring for: {TARGET_PROCESS_NAME}")
    print(f"Allowed time: {ALLOWED_START_HOUR}:00 to {ALLOWED_END_HOUR}:00 Local Time ({datetime.datetime.now().astimezone().tzname()})")
    print(f"Checking every {CHECK_INTERVAL_SECONDS} seconds.")
    print("Press Ctrl+C in the console to stop the script if running manually.")
    # Ensure the first check happens immediately on startup if needed
    if last_check_date != datetime.date.today():
         last_check_date = datetime.date.today()
         print(f"Initialized daily check date to {last_check_date}")


    while True:
        try:
            check_and_block_process()
            time.sleep(CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("Script stopped by user (Ctrl+C).")
            sys.exit(0)
        except Exception as e:
            print(f"An unexpected error occurred in the main loop: {e}")
            print("Restarting check in 1 minute...")
            time.sleep(60) # Wait a bit longer after an unexpected error