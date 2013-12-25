#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
import cStringIO
import logging
import os
import pickle
import sys
import webbrowser
import zlib
import requests
from bs4 import BeautifulSoup as Soup

# Todo
# Schedule loop
# Make output more friendly
# Fetch update
# Make sure only one instance is running

class WebHandler(object):
    def __init__(self, useragent=""):
        self.session = requests.Session()
        self.session.verify=True
        self.session.headers['User-Agent'] = useragent
    
    def open_url(self, url, method='get', data='', save_file=None):
        logger.debug("open_url() %s %s", method, url)
        if data:
            logger.debug("URL data: %s" % data)
        try:
            for loop in range(6): # Retry for 1 minute.
                if method.lower() == 'get':
                    pull = self.session.get
                else:
                    pull = self.session.post
                r = pull(url, data=data, timeout=10)
                
                if r.status_code != 200:
                    logging.error("Page error: %s %d" % (url, r.status_code))
                
                if save_file:
                    with open(save_file, 'w') as filehandle:
                        filehandle.write(r.text)
                
                return r.text
        except:
            logging.error("Could not connect")
            raise
    
    def open_browser(self=None, url=''):
        """
        Open a webpage in the desktop default browser like Firefox.
        """
        webbrowser.open(url, new=1)

class Updater(object):
    def check(self):
        web = WebHandler()
        #web.open_url("http://update url")

class Listing(object):
    """
    This is a simple class to hold all the listings to renew.
    It's primary function is to improve code readability.
    """
    def __init__(self, title="", url="", data={}):
        self.title = title
        self.url = url
        self.data = data
    
    def __str__(self):
        return '"%s" %s %s' % (self.title, self.url, self.data)

class RenewHandler(object):
    config_files = [] # List of possible config file locations.
    config_files.append(os.path.join(os.path.expanduser("~"), '.craigsrenewer'))
    config_files.append('.craigsrenewer')
    def __init__(self):
        file_read_success = None
        self.config = ConfigParser.SafeConfigParser()
        for cfile in self.config_files:
            try:
                file_read_success = self.config.read(cfile)
                #file_read_success = self.config.read("smurf")
                break
            except IOError:
                pass
        
        if not file_read_success:
            logging.error("ERROR: No configuration file found. %s" % self.config_files)
            raise IOError("No configuration file found.")
        logger.debug("Configuration file read: %s" % file_read_success)
        
        # This variable is a flag to let the GUI know if backend is currently renewing.
        self.processing = False
    
    def begin_renew_process(self):
        logger.info("Beginning renew process")
        
        # This variable is a flag to let the GUI know if backend is currently renewing.
        self.processing = True
        
        # Get login accounts from config.
        accounts = self.get_login_accounts()
        for account in accounts:
            # Create web browser session.
            self.web = WebHandler(self.config.get("useragent", "name"))
            # Log into website.
            page = self.log_into_site(account)
            # Is page requesting captcha.
            self.check_for_captcha(page)
            # Find items to renew.
            listings = self.get_renewable_listings(page)
            # Renew each item.
            self.renew_listings(listings)
        
        # This variable is a flag to let the GUI know if backend is currently renewing.
        self.processing = False
    
    def get_login_accounts(self):
        config = self.config
        accounts = []
        for section in config.sections():
            if section.lower().startswith("account"):
                d = { "user": config.get(section, "user"), 
                        "pass": config.get(section, "pass") }
                accounts.append(d)
        
        return accounts
    
    def log_into_site(self, account):
        url = "https://accounts.craigslist.org/login"
        page = self.web.open_url(url)
        
        data = {}
        for e in Soup(page).find('form', attrs={'name': 'login'}).findAll("input"):
            try:
                data[e['name']] = e['value']
            except(KeyError, TypeError):
                pass
        
        data.update({ 'inputEmailHandle': account['user'],
                'inputPassword': account['pass'] })
        
        page = self.web.open_url(url, data=data, method='post', save_file='listing.html')
        
        return page
    
    def check_for_captcha(self, page):
        result = Soup(page).find('div', id="recaptcha_table")
        logger.info('Captcha result: %s' % result)
    
    def get_renewable_listings(self, page):
        """
        Scrape page for renewable listings.
        Return a list of Listing objects.
        """
        listings = []
        for item in Soup(page).findAll('input', attrs={
                'name': 'go', 'value': 'renew', 'type': 'submit', 'class': 'managebtn' }):
            
            url = item.parent['action']
            
            data = {}
            while item:
                # Get name/value pairs for every nested input inside a form.
                data[item['name']] = item['value']
                logging.debug("item.previous_sibling %s" % item.previous_sibling)
                #item = item.parent
                item = item.previous_sibling
                logging.debug("data %s" % data)
            
            title = Soup(page).find('a', href=url).text
            tmplisting = Listing(title, url, data)
            
            logging.debug(tmplisting)
            
            listings.append(tmplisting)
        
        logging.info("Listings to renew %d", len(listings))
        
        return listings

    def renew_listings(self, listings):
        for tmplisting in listings:
            try:
                logging.debug("tmplisting.data %s" % tmplisting.data)
                self.web.open_url(tmplisting.url, 'post', tmplisting.data)
                logging.info("Update success: %s" % tmplisting.title)
            except:
                logging.warning("Update failed: %s" % tmplisting.title)
                raise

def main():
    global logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    renewhand = RenewHandler()
    
    if '--debug' in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    
    # If --no-gui is set, then run renew once in commandline mode.
    if '--no-gui' in sys.argv:
        renewhand.begin_renew_process()
        Updater().check()
        exit()
    

if __name__ == '__main__':
    main()
