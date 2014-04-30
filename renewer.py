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

try
    import requests
    from bs4 import BeautifulSoup as Soup
except
    print "A required library was not found. Please see https://github.com/Sepero/CraigsRenewer#dependencies"
    raise

# Todo
# Schedule loop
# Fetch update
# Make sure only one instance is running

global logger
logger = logging.getLogger(__name__)

class WebHandler(object):
    def __init__(self, useragent=""):
        self.session = requests.Session()
        self.session.verify = True
        self.session.headers['User-Agent'] = useragent
    
    def open_url(self, url, method='get', data='', save_file=None):
        logger.debug("open_url() %s %s", method, url)
        if data:
            logger.debug("URL data: %s" % data)
        try: # TODO: Move loop outside try/except
            for loop in range(6): # Retry 6 up to times, 10 seconds each try.
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
    config_files.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '.craigsrenewer'))
    def __init__(self):
        for cfile in self.config_files:
            try:
                self.config = ConfigParser.SafeConfigParser()
                self.config.readfp(open(cfile), cfile)
                print "Using config file: %s" % cfile
                break
            except IOError:
                logger.debug("Error reading: %s" % cfile, exc_info=True)
        
        if not self.config.sections():
            logging.error("ERROR: No configuration file found. %s" % self.config_files)
            raise IOError("No configuration file found.")
        
        # This variable is a flag to let the GUI know if backend is currently renewing.
        self.processing = False
    
    def begin_renew_process(self):
        """ Starts loop of renewing listings on all accounts. """
        logger.info("Beginning renew processes.")
        
        # This variable is a flag to let the GUI know if backend is currently renewing.
        self.processing = True
        
        # Get login accounts from config.
        accounts = self.get_login_accounts()
        print "Beginning renewal processes for %d accounts." % len(accounts)
        for account in accounts:
            # Create web browser session.
            if self.config.has_option("useragent", "name"):
                self.web = WebHandler(self.config.get("useragent", "name"))
            else:
                self.web = WebHandler("")
            
            # Log into website.
            print
            print "Logging in as account '%s'." % account['user']
            page = self.log_into_site(account)
            # Is page requesting captcha.
            if self.check_for_captcha(page):
                print "Captcha was found. Please login to your account manually."
                print "account '%s'" % account['user']
                continue
            # Verify that login was successful.
            if not self.is_login_success(page):
                print "Account '%s' did not appear to login correctly." % account['user']
            # Find items to renew.
            listings = self.get_renewable_listings(page)
            # Renew each item.
            if not listings:
                print "No listings to renew."
            else:
                self.renew_listings(listings)
        
        # This variable is a flag to let the GUI know if backend is currently renewing.
        self.processing = False
    
    def get_login_accounts(self):
        """
        Extracts accounts and info from config and generates a list
        of dictionaries.
        """
        config = self.config
        accounts = []
        for section in config.sections():
            if section.lower().startswith("account"):
                d = { "user": config.get(section, "user"), 
                        "pass": config.get(section, "pass") }
                accounts.append(d)
        
        return accounts
    
    def log_into_site(self, account):
        """
        *account* is a Python dictionary containing login information
        for a single account. It will login using the information.
        Returns the page after attempting login.
        """
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
        logger.info("Captcha result: %s" % result)
        return result
    
    def is_login_success(self, page):
        return Soup(page).find('p', text='Showing all postings')
    
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
            # for subitem in Soup(item).findAll('input'):
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
                print "Update success: %s" % tmplisting.title
                logging.info("Update success: %s" % tmplisting.title)
            except:
                print "Update failed: %s" % tmplisting.title
                logging.warning("Update failed: %s" % tmplisting.title)
                raise

def main():
    renewhand = RenewHandler()
    
    if '--debug' in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    
    renewhand.begin_renew_process()
    Updater().check()
    exit()


if __name__ == '__main__':
    import signal
    # This allows the program to exit quickly when pressing ctrl+c.
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    main()
