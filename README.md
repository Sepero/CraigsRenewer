Update
======
This code is currently not functional!!!
Craigslist made a modification to their website which prevents this software from accessing account login.


CraigsRenewer
=============

Automatically renew your craigslist ads with this script.

Commandline operation is simple. Place your account information into the configuration file ".craigsrenewer". Then run the program:

    python renewer.py --no-gui

It will renew the listings on your account.

Muliple account renewing is also supported. Simply put your accounts in the configuration file ".craigsrenewer", and place them each under a consecutive section 1, 2, 3:

    [account1]
    user: username
    pass: password
    
    [account2]
    user: username
    pass: password
    
    [account3]
    user: username
    pass: password


Dependencies
============

To run this program, you must have installed Python 2 http://www.python.org/ftp/python/2.7.6/python-2.7.6.msi  
http://www.python.org/ftp/python/2.7.6/

After installing Python, you will need to install 2 Python libraries: Beautifulsoup and requests.  
To install them, run:

    pip install requests beautifulsoup4

OR

    easy_install requests beautifulsoup4


Graphical Interface
===================

There is a graphical interface, but it is unfinished. To view it, you must have the library wxPython installed.

    pip install wxPython

After installing wxPython, the graphical interface is viewable by running:

    python gui.py


Any support in finishing the graphical interface in welcome.



About Me
========

This project was intended for commercial release, but due to legal changes on the craigslist website, I was not able to completely finish it.

Contact sepero 111 @ gmx . com
