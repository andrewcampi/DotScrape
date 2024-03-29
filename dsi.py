from byerecaptcha import solveRecaptcha
from time import sleep
import random
import re
import sys
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, NoSuchFrameException, TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
import undetected_chromedriver as uc


BROWSER = "UndetectedChrome" # "Chrome", "UndetectedChrome", or "Firefox"

def do_nothing():
    pass


def parse_scrape_file(dot_scrape_filename):
    # Initialize the lists for notes and commands
    notes = []
    commands = []

    # Read the contents of the file
    with open(dot_scrape_filename, 'r') as file:
        lines = file.readlines()
    
    # Process the first line to check for notes
    first_line = lines[0].strip().lower()
    if "note" in first_line:
        # Collect all lines until an empty line is found, and add them to the notes list
        for line in lines[1:]:
            if line.strip() == "":  # Empty line check
                break
            notes.append(line.strip())

        # The commands start after the empty line and the note block
        start_index = len(notes) + 2
    else:
        # If there are no notes, commands start from the first line
        start_index = 0

    # Process the rest of the lines as commands
    for line in lines[start_index:]:
        if line.strip():  # Only process lines with characters
            # Convert line to lowercase and strip escape characters, then add to commands list
            commands.append(line.strip().lower().replace('\n', '').replace('\r', ''))

    return notes, commands


def parse_scrape_content(dot_scrape_content):
    # Initialize the lists for notes and commands
    notes = []
    commands = []

    # Read the contents into a list
    lines = dot_scrape_content.split('\n')
    
    # Process the first line to check for notes
    first_line = lines[0].strip().lower()
    if "note" in first_line:
        # Collect all lines until an empty line is found, and add them to the notes list
        for line in lines[1:]:
            if line.strip() == "":  # Empty line check
                break
            notes.append(line.strip())

        # The commands start after the empty line and the note block
        start_index = len(notes) + 2
    else:
        # If there are no notes, commands start from the first line
        start_index = 0

    # Process the rest of the lines as commands
    for line in lines[start_index:]:
        if line.strip():  # Only process lines with characters
            # Convert line to lowercase and strip escape characters, then add to commands list
            commands.append(line.strip().replace('\n', '').replace('\r', ''))

    return notes, commands


def click_on_text(driver, text_to_click):
    found = False
    for i in range(len(text_to_click), 1, -1):
        substring_to_click = text_to_click[:i]
        xpath_expression = f"//*[contains(text(), '{substring_to_click}')]"
        try:
            # Wait until the elements are available to be clicked or a timeout occurs
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath_expression))
            )
            if len(elements) == 1:
                elements[0].click()  # Click on the element if only one is found
                found = True
                break
            elif len(elements) > 1:
                continue  # If more than one element is found, keep reducing the substring
        except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
            continue  # If an exception occurs, try with a shorter substring

    return found


def run_scraper(notes, commands, driver=None, quiet=False, headless=False):
    if driver == None:
        # Set up the driver
        if BROWSER == "Firefox":
            options = FirefoxOptions()
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            if headless:
                options.add_argument("--headless")
            #options.add_argument(f'user-agent={user_agent}')
            # Initialize the driver using webdriver_manager
            if driver == None:
                driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        elif BROWSER == "Chrome":
            options = ChromeOptions()
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            if headless:
                options.add_argument("--headless")
            #options.add_argument(f'user-agent={user_agent}')
            # Initialize the driver using webdriver_manager
            if driver == None:
                driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        elif BROWSER == "UndetectedChrome":
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            if headless:
                driver = uc.Chrome(options=options, headless=True, version_main=119)
            else:
                driver = uc.Chrome(options=options, version_main=119)

    auto_solve_recaptcha = False
    for note in notes:
        if "solve" in note and "recaptcha" in note:
            auto_solve_recaptcha = True

    variables = {}

    # Process each command
    for command in commands:
        case_sensitive_command = command
        command = command.lower()
        if not ("store the current url" in command or "snapshot this page into a variable" in command or command.startswith("return") or command.startswith("wait")):
            time_to_wait = round(random.uniform(1, 3), 5)
            print(f"WAITING: {time_to_wait} seconds") if not quiet else None
            sleep(time_to_wait)

        if auto_solve_recaptcha:
            try:
                print("--> Looking for recaptcha to solve") if not quiet else None
                result = solveRecaptcha(driver)
                print("--> SOLVED") if not quiet else None
                driver.switch_to.default_content()
                sleep(round(random.uniform(1, 2), 5))
            except:
                print("--> Could not find a recatpcha") if not quiet else None
                do_nothing()

        print("DOING:", command) if not quiet else None

        if command.startswith('go to '):
            # Extract the URL and navigate to it
            url = command.replace('go to ', '').replace('"', '').strip()
            if "http" not in url:
                url = "https://" + url
            driver.get(url)

        elif command.startswith('go back'):
            driver.back()

        elif command.startswith('refresh'):
            driver.refresh()

        elif command.startswith('click on the element with class name "') and "or the text" in command:
            parts = command.split('"')
            class_to_click = parts[1].strip()
            alternative_text = parts[3].strip().lower()  # The second substring inside double quotes
            try:
                element = driver.find_element(By.CLASS_NAME, class_to_click)
                # Click on the element
                element.click()
            except:
                click_on_text(alternative_text)

        elif command.startswith('click on the text "'):
            print("Command:", command)
            text_to_click = command.split('"')[1]
            click_on_text(driver, text_to_click)

        elif command.startswith('click on the div with class'):
            class_to_click = command.split('"')[1]  # Extract the class name from the command
            # Create an XPath expression that matches a div element with the specified class
            xpath_expression = f"//div[contains(@class, '{class_to_click}')]"
            # Find the element using the XPath selector
            elements = driver.find_elements(By.XPATH, xpath_expression)
            element_found_and_clicked = False
            # Click the first visible div element with the specified class
            for element in elements:
                if element.is_displayed():  # Check if the element is visible
                    element.click()  # Click on the visible element
                    element_found_and_clicked = True
                    break

            # If no visible element was clicked, search within iframes and popups
            if not element_found_and_clicked:
                # Switch to each iframe and search for the element
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    driver.switch_to.frame(iframe)
                    elements_in_iframe = driver.find_elements(By.XPATH, xpath_expression)
                    for element in elements_in_iframe:
                        if element.is_displayed():
                            element.click()
                            element_found_and_clicked = True
                            break
                    driver.switch_to.default_content()  # Switch back to the main content
                    if element_found_and_clicked:
                        break

                # If element is still not found, search in any popups
                if not element_found_and_clicked:
                    for handle in driver.window_handles:
                        driver.switch_to.window(handle)
                        elements_in_popup = driver.find_elements(By.XPATH, xpath_expression)
                        for element in elements_in_popup:
                            if element.is_displayed():
                                element.click()
                                element_found_and_clicked = True
                                break
                        if element_found_and_clicked:
                            break


        elif command.startswith('click on the div with id'):
            id_to_click = command.split('"')[1]  # Extract the id from the command
            # Create an XPath expression that matches a div element with the specified id
            xpath_expression = f"//div[contains(@id, '{id_to_click}')]"
            # Find the element using the XPath selector
            elements = driver.find_elements(By.XPATH, xpath_expression)
            # Click the first visible div element with the specified id
            for element in elements:
                if element.is_displayed():  # Check if the element is visible
                    element.click()  # Click on the visible element
                    break

        elif command.startswith('slow type "'):
            # Extract the text
            text_to_type = case_sensitive_command.split('"')[1]
            # Initialize ActionChains
            actions = webdriver.ActionChains(driver)
            # Iterate over each character in the string
            for char in text_to_type:
                # Type the character
                actions.send_keys(char).perform()    
                # Wait for a random time between 0.02 and 0.5 seconds
                sleep(random.uniform(0.02, 0.5))

        elif command.startswith('type "'):
            # Extract the text and type it into the focused element
            text_to_type = case_sensitive_command.split('"')[1]
            webdriver.ActionChains(driver).send_keys(text_to_type).perform()

        elif ('enter' in command) and (command.startswith('click') or command.startswith('press') or command.startswith('hit') or command.startswith('type')):
            # Simulate pressing Enter
            webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

        elif command.startswith('wait forever'):
            # Wait indefinitely
            while True:
                sleep(1)

        elif command.startswith("wait for user"):
            input("===> Waiting for user. Press [ENTER] to proceed when ready.")

        elif command.startswith('wait '):
            # Extract the number of seconds and wait
            seconds_to_sleep = int(command.split(' ')[1])
            if "minutes" in command:
                seconds_to_sleep = seconds_to_sleep * 60
            elif "hours" in command:
                seconds_to_sleep = (seconds_to_sleep * 60) * 60
            sleep(seconds_to_sleep)

        elif command.startswith('click the link with ') and "url" in command:
            sublink = command.split('"')[1]
            # Find all links on the page
            links = driver.find_elements(By.TAG_NAME, 'a')
            # Click the first one with the specified substring in its URL
            for link in links:
                url = link.get_attribute('href')
                if url:
                    if sublink in url.lower():
                        link.click()
                        break

        elif command.startswith('click the link that says "'):
            link_text = command.split('"')[1]
            # Find all links on the page
            links = driver.find_elements(By.TAG_NAME, 'a')
            # Click the first one containing the specified text
            for link in links:
                text = link.text
                if link_text.lower() in text.lower():  # Using lower to make it case-insensitive
                    try:
                        link.click()
                        break
                    except ElementNotInteractableException:
                        href = link.get_attribute('href')
                        driver.get(href)
                        break

        elif command.startswith('click the "'):
            button_substring_text = command.split('"')[1].lower()  # Extract the target text and convert it to lowercase
            # Initialize button_found as False
            button_found = False
            # List of possible selectors for buttons
            button_selectors = [
                By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{}')]".format(button_substring_text),
                By.XPATH, "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{}') and (@type='submit' or @type='button')]".format(button_substring_text),
                By.XPATH, "//textarea[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{}')]".format(button_substring_text)
            ]
            # Check main content and iframes
            for selector_type, selector in zip(button_selectors[::2], button_selectors[1::2]):
                # Try to find the button in the main content first
                buttons = driver.find_elements(selector_type, selector)
                for button in buttons:
                    button.click()
                    button_found = True
                    break
                if button_found:
                    break
                
                # If the button wasn't found in the main content, look through each iframe
                if not button_found:
                    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                    for index, iframe in enumerate(iframes):
                        # Switch to the iframe
                        driver.switch_to.frame(index)
                        # Search for the button within this iframe
                        buttons = driver.find_elements(selector_type, selector)
                        for button in buttons:
                            button.click()
                            button_found = True
                            break  # Break out of buttons loop
                        driver.switch_to.default_content()  # Switch back to the main content before moving to the next iframe
                        if button_found:
                            break  # Break out of iframes loop if button is clicked

        elif command.startswith('return to main'):
            driver.switch_to.default_content()

        elif command.startswith('scroll') and ("top" in command or "start" in command):
            # Scroll to the top of the page
            driver.execute_script("window.scrollTo(0, 0);")

        elif command.startswith('scroll up'):
            # Scroll up a maximum of 1 page view
            driver.execute_script("window.scrollBy(0, -window.innerHeight);")

        elif command.startswith('scroll') and ("bottom" in command or "end" in command):
            # Scroll to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        elif command.startswith('scroll down'):
            # Scroll down a maximum of 1 page view
            driver.execute_script("window.scrollBy(0, window.innerHeight);")

        elif command.startswith('solve') and "recaptcha" in command:
            try:
                print("--> Looking for recaptcha to solve") if not quiet else None
                result = solveRecaptcha(driver) 
                print("--> SOLVED") if not quiet else None
                driver.switch_to.default_content()
                sleep(round(random.uniform(1, 2), 5))
            except:
                print("--> Could not find a recatpcha") if not quiet else None
                do_nothing()

        elif command.startswith('snapshot this page into a variable'):
            variable_name = command.split('"')[1].lower()
            variables[variable_name] = driver.page_source

        elif command.startswith('store the current url into a variable'):
            variable_name = command.split('"')[1].lower()
            variables[variable_name] = driver.current_url

        elif command.startswith('set the variable "'):
            parts = command.split('"')
            variable_name = parts[1]  # The first substring inside double quotes
            item_name = parts[3]  # The second substring inside double quotes
            if " class " in command:
                # Find the element with the specified class name and extract its text content
                try:
                    element = driver.find_element(By.CLASS_NAME, item_name)
                except selenium.common.exceptions.NoSuchElementException:
                    print("\n======= AN ERROR OCCURED =======") if not quiet else None
                    raise Exception(f'Could not find the class "{item_name}".')
                visible_text_content = element.text
                variables[variable_name] = visible_text_content.strip().lower()
            elif " id " in command:
                # Find the element with the specified class name and extract its text content
                try:
                    element = driver.find_element(By.ID, item_name)
                except selenium.common.exceptions.NoSuchElementException:
                    print("\n======= AN ERROR OCCURED =======") if not quiet else None
                    raise Exception(f'Could not find the id "{item_name}".')
                visible_text_content = element.text
                variables[variable_name] = visible_text_content.strip().lower()

        elif command.startswith('return '):
            if "driver" in command:
                if "all" in command and "variables" in command:
                    return {"driver":driver, "variables":variables}
                elif "the variable" in command:
                    variable_to_return = command.split('"')[1].lower()
                    return {"driver":driver, "variables":variables[variable_to_return]}
                else:
                    return {"driver":driver}
            else:
                if "the variable" in command:
                    variable_to_return = command.split('"')[1].lower()
                    driver.quit()
                    return {"variables":variables[variable_to_return]}
                elif "all" in command and "variables" in command:
                    driver.quit()
                    return {"variables":variables}

    # Assuming the driver should be closed at the end of the script
    driver.quit()
    return None

# IF IMPORTING FROM ANOTHER FILE (i.e. you did "import dsi"), simply provide your multi-line .scrape language as an argument and run this function.
def run_dot_scrape(dot_scrape_content, driver=None, quiet=False, headless=False):
    notes, commands = parse_scrape_content(dot_scrape_content)
    return run_scraper(notes, commands, driver=driver, quiet=quiet, headless=headless) # Returns a dictionary with (at most) keys "driver" and "variables"


# MAIN -- You can use this code to run the DSI from the command line, given a .scrape file path as an argument.
"""
# Check if the command-line arguments include the filename
if len(sys.argv) > 1:
    dot_scrape_filename = sys.argv[1]
else:
    print("No dot scrape filename provided.")
    sys.exit(1)  # Exit the script if no argument is given
notes, commands = parse_scrape_file(dot_scrape_filename)
return_value = run_scraper(notes, commands)
if return_value:
    print(return_value)
"""
