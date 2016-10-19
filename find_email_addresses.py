#!/usr/bin/python
from lxml import html
from urlparse import urlsplit
from urlparse import urlunsplit
import re
import requests
import requests.exceptions as exceptions
import sys
import argparse

#Given a website, finds all emails on all discoverable pages on the webiste
def find_emails(website, max_seconds, *max_emails):
  if not max_emails: 
    max_emails = float("inf")
  else: 
    max_emails = max_emails[0]
  #Format url correctly and extract the domain name 
  parsed = urlsplit(website)
  if parsed.scheme: 
    starting_page = parsed.geturl()
    domain_name = parsed.netloc
  else: 
    starting_page = 'http://' + website
    parsed_page = urlsplit(starting_page)
    domain_name = parsed_page.netloc
  #Create a queue of pages that need to be checked, 
  #and a list of pages that have already been checked
  all_pages = [starting_page]
  finished_pages = set()
  #Keep track of email addresses that have been printed already
  email_addresses_found = set()
  while len(all_pages) > 0: 
    page_url = all_pages.pop(0)
    #If we've already checked the page, skip it
    if page_url in finished_pages:
      continue
    #print page_url
    try: 
      #Make sure the page is another webpage and not a file
      page_headers = requests.head(page_url).headers
      if page_headers.get('content-type'):
        header = page_headers.get('content-type').lower()
        if not header.startswith('text/html') and not header.startswith('application/xhtml+xml'):
          finished_pages.add(str(page_url))
          continue
      page = requests.get(page_url)
    except (exceptions.SSLError, exceptions.TooManyRedirects, exceptions.ConnectionError, exceptions.InvalidURL): 
      print "Cannot access " + page_url + "."
      finished_pages.add(str(page_url))
      continue
    #Create a tree of the page HTML
    tree = html.fromstring(page.content)
    #Find all <a> elements that contain the domain_name
    for url in tree.xpath('//a[contains(@href, "' + domain_name + '")]/@href'):
      #Strip scheme and/or www off URL
      check_url = re.sub(r'^((https?)?:?//)?(www\.)?', '', str(url))
      #Ignore URLs that are not directly in our domain
      if not check_url.startswith(domain_name):
        continue
      #Format URL before adding it to the queue
      parsed_url = urlsplit(url)
      if not parsed_url.scheme:
        #Set the scheme to be the scheme of the page we're already on
        parts = [urlsplit(page_url).scheme]
        for i in range(1, 5):
          parts.append(parsed_url[i])
        new_url = str(urlunsplit(parts))
      else: 
        new_url = str(url)
      all_pages.append(new_url)
    page_text = tree.text_content().replace(u'\xa0', u' ')
    #used emailregex.com
    for email_address in re.findall(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', page_text):
      if email_address not in email_addresses_found:
        print email_address
      email_addresses_found.add(email_address)
      if len(email_addresses_found) >= max_emails:
        print "got here"
        return
    for email_link in tree.xpath('//a[starts-with(@href, "mailto")]/@href'):
      #Make sure we're getting email address only
      mailto_content = email_link.split(":", 1)[1]
      email_address = mailto_content.split("?", 1)[0]
      if email_address not in email_addresses_found:
        print email_address
      email_addresses_found.add(email_address)
      if len(email_addresses_found) >= max_emails:
        return
    finished_pages.add(str(page_url))

def main(args):
  if args.max_emails:
    find_emails(args.website, args.max_seconds, args.max_emails)
  else: 
    find_emails(args.website, args.max_seconds)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Find emails on website.")
  parser.add_argument('website', type=str)
  parser.add_argument('-s', '--max-seconds', type=float, default=100)
  parser.add_argument('-e', '--max-emails', type=int)
  main(parser.parse_args())



