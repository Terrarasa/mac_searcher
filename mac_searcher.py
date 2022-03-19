#!/usr/bin/python

##-----------------------------------------------##
## @author Mike
## @description Wrapper for mac_vendor_lookup with CSV support
##-----------------------------------------------##

import argparse, sys, mac_vendor_lookup, csv, os.path
from dataclasses import replace

def main():
    #MacLookup opject
    mac = mac_vendor_lookup.MacLookup()

    #Set up CLI arguments
    #Comms with built in help -h --help
    parser = argparse.ArgumentParser(description="Provides a wrapper for MacLookup. Lookup Media Access Control addresses against a list of vendors.")
    group = parser.add_mutually_exclusive_group()

    #Group exclusive options
    group.add_argument("-m", "--mac", help="Media Access Control Address to query", type=str, default=False)
    group.add_argument("-i", "--infile", help="Comma Seperated Value file of MAC addresses to parse. Each MAC should be on a newline", type=str, default=False)

    parser.add_argument("-o", "--outfile", help="Specify an output file for results", type=str, default=False)
    parser.add_argument("-u", "--update", help=f"Download an updated vendor's file\nWill be stored in {mac.cache_path}", action="store_true")
    
    args = parser.parse_args()

    # Is this the first run (check cache existance)
    if os.path.isfile(mac.cache_path) == False:
        print("Cache file not detected\nAttempting to download cache file")
        mac.download_vendors()
        print("Cache file downloaded\nTo update the cache file in future, use the --update argument")


    if args.update != False:
        print("Updating vendor list\nThis might take some time")
        mac.download_vendors()
        
        # Error handling dealt with upstream
        print("Updated vendor file")

    elif args.mac != False:
        #Single MAC address
        #Catch errors from library
        try:
            vendor = mac.lookup(args.mac)
        except mac_vendor_lookup.VendorNotFoundError:
            sys.exit("MAC Address vendor not found.\nConsider updating the vendor list with mac_searcher.py -u")
        except mac_vendor_lookup.InvalidMacError:
            sys.exit("Invalid MAC address submitted, please review and try again")
        
        #Combine MAC and Vendor
        result = f"{args.mac} : {vendor}"

        #Outfile or stdout?
        if args.outfile != False:
            with open(args.outfile, "w") as outfile:
                outfile.write(result)
                print(f"Output file {args.outfile} written to successfully!")
        else:
            print(result)

    elif args.infile != False:
        #Multiple MAC addresses from CSV
        with open(args.infile, "r", newline='', encoding="utf-8-sig") as csvfile:
            mac_file = csv.reader(csvfile, dialect=csv.excel)
            if args.outfile != False:
                #Save to file
                with open(args.outfile, "w", newline='', encoding="utf-8") as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=["MAC Address", "Vendor"])
                    writer.writeheader()

                    for row in mac_file:
                        try:
                            _mac = str(row)
                            #Strip out brackets and single quotes from imported rows
                            mac_string = _mac.replace("['","").replace("']","")
                            writer.writerow({"MAC Address":mac_string, "Vendor":mac.lookup(mac_string)})
                        except mac_vendor_lookup.VendorNotFoundError:
                            writer.writerow({"MAC Address":mac_string, "Vendor": "Not Found"})
                        except mac_vendor_lookup.InvalidMacError:
                            writer.writerow({"MAC Address":mac_string, "Vendor": "Invalid MAC"})


                    print(f"Output file {args.outfile} written to successfully!")
            else:
                #Print to stdout
                for row in mac_file:
                    try:
                        _mac = str(row)
                        mac_string = _mac.replace("['","").replace("']","")
                        print(f"{mac_string} : {mac.lookup(mac_string)}")
                    except mac_vendor_lookup.VendorNotFoundError:
                        print(f"{mac_string} has not been found in the vendor list")
                    except mac_vendor_lookup.InvalidMacError:
                        print(f"{mac_string} is not a valid MAC address")
                
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
else:
    sys.exit("This is only meant to be run from the command line!")

