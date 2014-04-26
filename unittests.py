#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
import logging
import os
import sys
import unittest
import renewer

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_page(name='page.html', string=""):
    with open(name, 'w') as page:
        page.write(string)

def load_page(name='page.html'):
    with open(name) as page:
        data = page.read()
    return data

class RenewTests(unittest.TestCase):
    def setUp(self):
        renewer.logger = logger
        self.rh = renewer.RenewHandler()
        #self.creds = self.rh.get_login_credentials()
    
    def test_failed_login(self):
        account = { 'user': 'fakeuser', 'pass': 'fakepass' }
        rh = renewer.RenewHandler()
        rh.web = renewer.WebHandler("")
        page = rh.log_into_site(account)
        self.assertFalse(rh.is_login_success(page))
    
    def test1_get_login_page(self):
        # Get first login account available from config file.
        account0 = self.rh.get_login_accounts()[0]
        self.rh.web = renewer.WebHandler(self.rh.config.get("useragent", "name"))
        page = self.rh.log_into_site(account0)
        
        # Save management page to a file.
        # We may need to review/validate the html if testing fails.
        save_page('listing.html', page)
    
    def test2_find_listings(self):
        page = load_page('listing.html')
        
        # Verify the page looks correct (user logged in).
        assert("posting title" in page)
        
        try:
            # Get first renewable listing if available.
            l = self.rh.get_renewable_listings(page)[0]
            logger.debug("l.data is: %s" % l.data)
            
            # Validate listing html form input elements.
            for key, value in {'go': 'renew', 'action': 'renew'}.items():
                assert(l.data[key] == value)
            assert(l.data.has_key('crypt'))
        except IndexError:
            print "===NO RENEWABLE LISTINGS FOUND==="
    
    def test3_get_renewable_listings(self):
        page = load_page('listing.html')
        self.rh.get_renewable_listings(page)
    
    def tearDown(self):
        pass

if __name__ == '__main__':
	unittest.main()
