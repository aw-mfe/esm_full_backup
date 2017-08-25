===========================================================
ESM_Full_Backup: Kicks off a full backup process on the ESM
===========================================================

This simple script initates a full backup on the McAfee ESM. Today a full backup cannot be scheduled and
must be performed manually. This script does not monitor the backup process nor validate that the backup 
occurred successfully, it only kicks off the process.

WARNING: The ESM is inaccessible during the backup process and the backup process could take considerable
time depending upon the volume of data. Status of the backup process can be found in /var/log/messages on 
the ESM.

If you do not want to run the Windows EXE then you will need to make sure Python 3 is installed.

Directions on how to install and create an environment to run the script on both Linux and Windows are available at:
https://community.mcafee.com/people/andy777/blog/2016/11/29/installing-python-3

The script requires a .mfe\_saw.ini file for the credentials. 

See installation notes to determine which directory it should be placed for your operating system.

----------
QuickStart
----------

**Windows**

1. Download the `latest release <https://github.com/andywalden/esm_full_backup/releases/latest>`__

2. Unzip it into a directory.

3. Create your .mfe_saw.ini configuration_ file.

4. Run esm_full_backup -f

**Linux**

1. pip3 install esm_full_backup

2. Create your .mfe_saw.ini configuration_ file.

3. esm_full_backup -f

-----
Usage
-----

::

        usage: esm_full_backup -f

-------------
Prerequisites
-------------

-  Python 3 if running as script
-  McAfee ESM running version 9.x or 10.x
-  Port 443 access to the ESM
-  NGCP credentials
- .mfe_ini file (covered below)

------------
Installation
------------

^^^^^^^
Windows:
^^^^^^^
Download, unzip and  at a CMD prompt.

`Windows EXE Package <https://github.com/andywalden/esm_full_backup/releases/latest>`__


^^^^^^
Linux:
^^^^^^

Install via PIP:

::

    $ pip3 install esm_full_backup


^^^^^^^^^^^^^^
Manual install 
^^^^^^^^^^^^^^
    
    
`Python project and source code <https://github.com/andywalden/esm_full_backup/releases/latest>`__

::

    $ unzip master.zip
    $ cd esm_full_backup
    $ python3 setup.py install
    
.. _configuration:
-------------
Configuration
-------------

This script requires a '.mfe\_saw.ini' file in your home directory. This
file contains sensitive clear text credentials for the McAfee ESM so it
is important it be protected. This is same ini file will be referenced
by all future ESM related projects also.

It looks like this:

::

    [esm]
    esmhost=10.0.0.1
    esmuser=NGCP
    esmpass=SuppaSecret

An example mfe-saw.ini is available in the download or at:
https://github.com/andywalden/esm_full_backup/blob/master/mfe\_saw.ini

^^^^^^^
Windows
^^^^^^^

Go to Start \| Run and type %APPDATA% into the box and press
enter. This will open your Windows home directory. Edit the Copy the
customized .mfe\_saw.ini (period in front) to the directory.

^^^^^^^^^^
Linux\*nix
^^^^^^^^^^

The '.mfe\_saw.ini' file will either live in: $HOME or:
$XDG\_CONFIG\_HOME. You can determine which by typing:

::

    echo $XDG_CONFIG_HOME
    echo $HOME

One or both should list your home directory. If both options are
available, $XDG\_CONFIG\_HOME is the more modern and recommended choice.

----------
Disclaimer
----------

*Note: This is an **UNOFFICIAL** project and is **NOT** sponsored or
supported by **McAfee, Inc**. If you accidentally delete all of your
datasources, don't call support (or me). Product access will always be
limited to 'safe' methods and with respect to McAfee's intellectual
property. This project is released under the `ISC
license <https://en.wikipedia.org/wiki/ISC_license>`__, which is a
permissive free software license published by the Internet Systems
Consortium (ISC) and without any warranty.*
