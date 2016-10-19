# Find All Email Addresses on a Website

Given some website, this program will find all email addresses on any of the pages with that domain name. However, it does not consider web pages on subdomains. 

Setup: 
 * I've included a `requirements.txt` file. 
 * The libraries I use can also be directly installed using the command line: `pip install lxml` and `pip install requests` 
 * To run, enter `python find_email_addresses.py [website] -e [max number of emails to print] -s [seconds to run the program before terminating]` into the command line from the project directory.
 * The website argument is a valid website URL. The -e and -s arguments are optional. -e should take an int, and -s should take a float; by default, the program will timeout after 200 seconds.
