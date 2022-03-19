##-----------------------------------------------##
# MAC Lookup basic functions
# @author Mike https://github.com/terrarasa
# Based on work by Johann Bauer https://github.com/bauerj
# Based on @project https://github.com/bauerj/mac_vendor_lookup
##-----------------------------------------------##

import os, logging, sys, urllib.request, urllib.error
from datetime import datetime

OUI_URL = "https://standards-oui.ieee.org/oui.txt"


class InvalidMacError(Exception):
    pass


class VendorNotFoundError(KeyError):
    def __init__(self, mac):
        self.mac = mac

    def __str__(self):
        return f"The vendor for MAC {self.mac} could not be found. " \
               f"Either it's not registered or the local list is out of date. Try MacLookup().update_vendors()"

class BaseMacLookup(object):
    cache_path = f"{os.path.curdir}{os.path.sep}mac-vendors.txt"

    @staticmethod
    def sanitise(_mac):
        mac = _mac.replace(":", "").replace("-", "").replace(".", "").upper()
        try:
            int(mac, 16)
        except ValueError:
            raise InvalidMacError("{} contains unexpected character".format(_mac))
        if len(mac) > 12:
            raise InvalidMacError("{} is not a valid MAC address (too long)".format(_mac))
        return mac

    def get_last_updated(self):
        vendors_location = self.find_vendors_list()
        if vendors_location:
            return datetime.fromtimestamp(os.path.getmtime(vendors_location))

    def find_vendors_list(self):
        possible_locations = [
            self.cache_path,
            sys.prefix + os.path.sep + "cache" + os.path.sep + "mac-vendors.txt"
        ]

        for location in possible_locations:
            if os.path.exists(location):
                return location


class MacLookup(BaseMacLookup):
    def __init__(self):
        self.prefixes = {}       

    #Download Function
    def download_vendors(self):
        logging.log(logging.DEBUG, "Downloading MAC vendor list")
        # Connect to the IEEE server and obtain MAC vendor list
        # Try/except here to handle errors (context manager looks ugly)
        try:
            response = urllib.request.urlopen(OUI_URL)
        #Handle HTTP errors first as it's a subclass of URL error (and otherwise causes everything to be handled as URL errors)
        except urllib.error.HTTPError as e:
            sys.exit(f"IEEE server returned an error\nUnable to obtain updated MAC vendor list\n{e.code}: {e.reason}")
        except urllib.error.URLError as e:
            sys.exit("Unable to connect to the server\nCheck your internet connection, firewall, or proxy")
        
        file = response.read().decode("utf-8")
        split_request = file.splitlines(False)

        with open(self.cache_path, mode='w', encoding="utf-8") as out_file:
            """ The OUI file is very long
                it contains the Hex and Base16 variants of the MAC identifier along with full addresses of manufacturers
                to save on cache space, we cut out the data we need and discard the remainder
                Cache file is saved as list of base16:vendor separated by \n
            """
            
            for i in range(len(split_request)):
                #Does the line relate to the base16 version of the MAC identifier?
                if not split_request[i]:
                    continue
                if split_request[i].find("(base 16)") == 11:
                    #Split the line into the identifier and vendor
                    prefix, vendor = split_request[i].split("(base 16)", 1)
                    #Strip out white space and write to cache file
                    out_file.write(f"{prefix.strip()}:{vendor.strip()}\n")
                else:
                    continue
  
       
    #Load prefixes into memory
    def load_prefixes(self):
        logging.log(logging.DEBUG, "Loading prefixes into memory")

        #Does the cache already exist or does it need to be downloaded?
        if os.path.isfile(self.cache_path) == False:
            self.download_vendors
        
        with open(self.cache_path, mode='r', encoding="utf-8") as f:
            split_file = f.read().splitlines(False)
            for i in range(len(split_file)):
                prefix, vendor = split_file[i].split(":", 1)
                self.prefixes[prefix] = vendor
    
    #Lookup a MAC
    def lookup(self, mac):
        mac = BaseMacLookup.sanitise(mac)
        self.load_prefixes()
        
        try:
            return self.prefixes[mac[:6]]
        except KeyError:
            raise VendorNotFoundError(mac)