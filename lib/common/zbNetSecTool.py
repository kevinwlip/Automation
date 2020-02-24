#!/usr/bin/python

import nmap


# function to scan host/port and return True if port is open, and false if not
def nmapScanHostPort(host, port):
    portStatus = False
    nm = nmap.PortScanner()
    result = nm.scan(str(host), str(port))
    for proto in ['tcp', 'udp']:
        try:
            if result['scan'][host]['tcp'][int(port)]['state'] == 'open':
                portStatus = True
                break
        except KeyError:
            pass
    return portStatus