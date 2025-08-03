import os
import sys
import time
import random
import threading
import customtkinter as ctk

from Utils.data import save, load

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # Optional

def Get_Random_User_Agent(file_path=os.path.join(os.path.dirname(__file__), "Utils", "UserAgents.txt")):
    with open(file_path, "r", encoding="utf-8") as f:
        user_agents = [line.strip() for line in f if line.strip()]
    return random.choice(user_agents)

def Login(username, password):
    global driver # <-- allow global access for force quit

    # Path to chromedriver in Utils folder
    local_driver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "Utils", "chromedriver.exe"))

    # webdriver check
    if os.path.exists(local_driver_path):
        service = Service(executable_path=local_driver_path)
    else:
        service = Service(ChromeDriverManager().install()) # Optional
        status_label.configure(text="webdriver not found installing...", text_color="yellow")

    # setup browser
    options = webdriver.ChromeOptions()
    options.add_argument("--no-first-run")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--log-level=3")  # only fatal errors
    options.add_argument(f"user-agent={Get_Random_User_Agent()}")

    service.creationflags = 0x08000000  # Hide console on Windows

    # apply services
    driver = webdriver.Chrome(service=service, options=options)
    
    # perform login
    status_label.configure(text="fetching data...", text_color="white")
    try:
        driver.get("https://netlogon-phetch.su.ac.th/su-internet.php")
        driver.find_element(By.XPATH, '//*[@id="CheckUser"]/div[1]/div/div[2]/div/div[1]/input').send_keys(username)
        driver.find_element(By.XPATH, '//*[@id="CheckUser"]/div[1]/div/div[2]/div/div[2]/input').send_keys(password)
        driver.find_element(By.XPATH, '//*[@id="CheckUser"]/div[1]/div/div[2]/div/button').click()

        # Close current window (login page)
        driver.close()
        time.sleep(1)

        try:
            # Switch to the newest (last) opened window
            driver.switch_to.window(driver.window_handles[-1])

            # Check if Extend button exist
            try:
                driver.find_element(By.XPATH, '/html/body/form[2]/input[1]') # Extend Button
                # driver.find_element(By.XPATH, '/html/body/form[2]/input[2]') # Logout Button

                status_label.configure(text="SUCCESS", text_color="green")

                try:
                    while True:
                        status_label.configure(text=f"Last Extend: {time.ctime()}", text_color="green")
                        # driver.refresh() # Optional
                        driver.find_element(By.XPATH, '/html/body/form[2]/input[1]').click() # click Extend Button
                        time.sleep(7200)  # 2 hours = 7200 seconds
                except:
                        status_label.configure(text="FAIL", text_color="red")
                        driver.quit()
                        sys.exit()
            except:
                status_label.configure(text="FAIL", text_color="red")
                driver.quit()
                sys.exit()
        except:
            status_label.configure(text="FAIL", text_color="red")
            driver.quit()
            sys.exit()

    except Exception as e:
        status_label.configure(text=f"Error: {e}", text_color="red")

def Submit():
    username = entry_user.get()
    password = entry_pass.get()
    
    if not username or not password:
        status_label.configure(text="Username or password cannot be empty!", text_color="red")
        return
        
    entry_user.configure(state="disabled")
    entry_pass.configure(state="disabled")
    submit_button.configure(state="disabled")

    status_label.configure(text="initializing...", text_color="white")

    # perform login in new thread
    threading.Thread(target=Login, args=(username, password), daemon=True).start()

def On_Close():
    # quit order matter, do not change
    app.destroy()
    driver.quit()
    sys.exit()

def Block_Space(event):
    if event.keysym == "space":
        return "break"  # prevent spacebar

if __name__ == "__main__":
    ctk.set_appearance_mode("System")

    # create window
    app = ctk.CTk()
    app.geometry("320x240")
    app.title("OAK SU NET LOGIN")
    app.resizable(False, False)

    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x = (screen_width // 2) - (320 // 2)
    y = (screen_height // 3) - (240 // 3)
    app.geometry(f"320x240+{x}+{y}")  # apply new centered geometry

    ctk.CTkLabel(app, text="Username").pack(pady=(10, 0))
    entry_user = ctk.CTkEntry(app)
    entry_user.pack()
    entry_user.bind("<Key>", Block_Space)

    ctk.CTkLabel(app, text="Password").pack(pady=(10, 0))
    entry_pass = ctk.CTkEntry(app, show="*")
    entry_pass.pack()

    # bind submit to ENTER key
    app.bind("<Return>", lambda event: Submit())
    submit_button = ctk.CTkButton(app, text="Login", command=Submit)
    submit_button.pack(pady=20)

    status_label = ctk.CTkLabel(app, text="")
    status_label.pack()

    # Handle window close
    app.protocol("WM_DELETE_WINDOW", On_Close)

    # initialize ui
    app.mainloop()