# .scrape
A new natural coding language for web scraping.
#### example.scrape :
~~~
go to google.com
type "Sam Altman Wikipedia"
press enter
click the first link containing "Sam Altman"
~~~
The above example is basic .scrape code that navigates to Sam Altman's wikipedia page. 

## Why
Web scraping with Python has a high learning curve, even for basic tasks. It would be much easier if there was a wrapper for Python's Selenium library that enables users to use natural language to describe what they want to achieve. 

## How
The Dot Scrape Interpreter (DSI) (dsi.py) converts .scrape natural language into Python Selenium code. You can use natural language like "go to google.com", "click on the text "Submit"", "wait 3 seconds", or even "solve recaptcha". This way, you can start web scraping quickly while keeping your code readable and clean. 

## Usage
There are two ways to use the DSI. The best way to use it is to integrate it into your Python code. You can also write a .scrape file and run the DSI directly.

### DSI integration into your code
First, download dsi.py from this repo and put it directly in your project. For example, if you are running main.py, put dsi.py in the same directory as main.py.
There are Python library installation requirements located in this repo's requirements.txt. Download that file, then use "pip install -r requirements.txt".
Then, you can use the DSI like this (very basic example):
~~~ Python
from dsi import run_dot_scrape
# This .scrape code goes to Sam Altman's Wikipedia page, then waits there.
dot_scrape_code = """
go to google.com
type "Sam Altman Wikipedia"
press enter
click the first link containing "Sam Altman"
wait forever
"""
run_dot_scrape(dot_scrape_code)
~~~
The run_do_scrape() function can return a dictionary with (at most) two keys: "driver" and "variables". This way, you can continue using the driver where the .scrape code left off, or save text that you scraped from a page into a Python variable. 
This example scrapes the text content from Sam Altman's Wikipedia page, and returns the driver and the text content it scraped. 
~~~ Python
from dsi import run_dot_scrape
# This .scrape code goes to Sam Altman's Wikipedia page, then waits there.
dot_scrape_code = """
Notes:
automatically solve recaptchas

go to google.com
type "Sam Altman Wikipedia"
press enter
click the first link containing "Sam Altman"
set the variable "wiki_page_content" to be the text in the id "mw-content-text"
return the driver and the variable "wiki_page_content"
"""
returned_content = run_dot_scrape(dot_scrape_code)
driver = returned_content["driver"]
scraped_content = returned_content["variables"]

# You can chain together .scrape by passing in the driver it returned as an argument
dot_scrape_code_2 = """
Click the link with "wiki/Stanford" in the url
wait forever
"""
run_dot_scrape(dot_scrape_code_2, driver=driver)
~~~
The above example also constantly checks for recaptchas between each .scrape command and tries to solve them. This extra check drastically slows the .scrape code. You should also be aware that returned_content["variables"] will be a dictionary of variable names you created as its keys. This happens when your .scrape code contains "return all variables" or "return the driver and all variables" instead of returning a specific variable like "return variable "{variable name}"". 

### Running the DSI with a .scrape file
Download the DSI (dsi.py) to your local machine. 
At the bottom of that file, there is code commented out with triple qoutes. Delete the two triple quote lines. Save the edited file. 
There are Python library installation requirements located in this repo's requirements.txt. Download that file, then use "pip install -r requirements.txt".
Create your .scrape file. In this example, we will name it "test.scrape" and write the following content in it:
~~~
go to google.com
type "Sam Altman Wikipedia"
press enter
click the first link containing "Sam Altman"
~~~
Then run the command "python dsi.py test.scrape".

## Docs: How to write .scrape 
Each line of .scrape code is referred to as a command. While .scrape code reads naturally, there are some basic syntax rules. Use this documentation as a reference when writing your .scrape code. Capitalization and using periods do not matter.

### Waiting some time
Syntax:
~~~
Wait {time amount} {time unit}
~~~
Example #1:
~~~
wait 5 seconds
~~~
Example #2:
~~~
Wait 10 minutes.
~~~
You can use any amount of time and "seconds", "minutes", or "hours". 

### Wait forever
Syntax:
~~~
wait forever
~~~
Helpful for developing, debugging, and testing .scrape code, this puts .scrape into an infinite loop, waiting endlessly. 

### Type something
Syntax:
~~~
type "{text to type}"
~~~
Example #1:
~~~
Type the text "My name is Adam".
~~~
Example #2:
~~~
type "My name is Adam"
~~~
Make sure you clicked on the text box that you want to type in before using this syntax. Otherwise, it might not type in the correct place or at all. 
You need to use double quotes in your command. 

### Hit the enter key
Syntax:
~~~
{"click", "type", "hit", or "press"} enter
~~~
Example #1:
~~~
Press the Enter key.
~~~
Example #2:
~~~
hit enter
~~~
As expected, this simply hits enter, which is useful to submit an input form after typing something, rather than finding and pressing the submit button.

### Navigating to a URL or website
Syntax:
~~~
Go to {url}
~~~
Example #1:
~~~
go to google.com
~~~
Example #2:
~~~
Go to https://google.com
~~~
You can use the entire url with or without "http(s)://". Not specifying "http(s)://" will use HTTPS. 

### Solving the recaptcha
Syntax:
~~~
solve recaptcha
~~~
Example #1:
~~~
Solve the recaptcha.
~~~
Example #2:
~~~
solve recaptcha
~~~
If your .scrape command starts with the word "solve" and contains "recaptcha", it will locate and solve the recaptcha on the current page.

### Clicking on text
Syntax:
~~~
Click on the text "{text to click}"
~~~
Example #1:
~~~ 
click on the text "Click Me"
~~~
Example #2:
~~~
Click on the text "Submit".
~~~
It will try to find the readable text you specified, and will try to click it. You need to use double quotes in your command. 
This is not the most reliable way to click things with .scrape code. See the next section for a better way to identify what you want to click.

### Clicking on a div by class name
Syntax:
~~~
click on the div with class "{class name}"
~~~
Example #1:
~~~
Click on the div with class "LGOjhe"
~~~
Example #2:
~~~
click on the div with class "DasDJd"
~~~
When you use "inspect element" in your browser on the page, you will see lines of HTML like "<div class="LGOjhe" ..." Use the class name seen there in this type of .scrape command.
You need to use double quotes in your command. 

### Clicking on a link with a specific URL substring
Syntax:
~~~
click the link with "{URL substring}"
~~~
Example #1:
~~~
click the link with "example.com"
~~~
Example #2:
~~~
Click the link with "https://example".
~~~
This will click on the first link with the URL substring provided, so be very specific with your provided URL substring so there is not confusion due to duplicates.
You need to use double quotes in your command. 

### Click the link with specific visible link text
Syntax:
~~~
click the first link containing "{link text}"
~~~
Example #1:
~~~
click the first link containing "Click Me"
~~~
Example #2:
~~~
Click the first link containing "Submit".
~~~
This will click on the first link on the page that contains the specified link text. The link text is the text you can see that represents a link on a page. 
You need to use double quotes in your command. 

### Click on a specific button
Syntax:
~~~
Click the "{button text}"
~~~
Example #1:
~~~
Click the "Submit" button.
~~~
Example #2:
~~~
Click the "Click Me" button on the page.
~~~
This will click any button or input button on the page with the provided button text. You need to use double quotes in your command. 

### Using variables to save scraped information
Syntax:
~~~
Set the variable "{variable name}" to be the text in the {class or id} "{class or id name}"
~~~
Example #1:
~~~
Set the variable "person_age" to be the text in the class "age".
~~~
Example #2:
~~~
Set the variable "person_age" to be the text in the div with id "age". 
~~~
This will save the visible text in a variable "person_age". Reference the following command syntax to access the content of the variable.

### Returning the driver and/or your variables
Syntax:
~~~
Return the driver
Return the driver and all variables
Return the variable {variable name}
Return the driver and the variable {variable name}
Return all variables
~~~
Using one of the above lines will terminate the .scrape code and return a dictionary.
If you returned the driver only, it will have one key named "driver". 
If you used "Return all variables" only, it will have one key named "variables" that is a dictionary of variables as keys and their variable values as the values. 
If you used "Return the variable {variable name}" It will have the key "variables" that is a string.
If you returned the driver and the variable(s), It will have two keys: "driver" and "variables".
