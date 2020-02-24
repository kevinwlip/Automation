#!/usr/bin/python


import sys, os, time, re, netaddr, json, pdb
from .zbDatetime import is_similar_datetime
from ipaddress import ip_address
import regex, socket

REGEX_UI_DATA_PATTERN = re.compile(r'(\d+\.?\d*)\ (\w?B)')

def getHostname():
    return socket.gethostname()

# Regex with partial matching capabilties
def fuzzyRegexSearch(string, reg, maxdiff):
    modifier = "{e<=" + str(maxdiff) + "}"
    result = regex.search("(?:" +reg +")"+modifier, string)
    return result

# convert IP string to int
def convertIP(ipstring):
    try:
        return int(netaddr.IPAddress(ipstring))
    except:
        return False

# convert Byte string to byte integer.  Example "78.53 KB" to Bytes
def convertByte(bytestring):
    checkSize = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    match = re.search(REGEX_UI_DATA_PATTERN, bytestring)
    totalData = 0
    if match:
        number = float(match.group(1))
        index = checkSize.index(match.group(2)) 
        totalData = number * 1024 ** index
    return totalData


# make sure none of data are empty
def validateDataNotEmpty(data):
    if type(data) == dict:
        for key,val in data.items():
            if val == '': 
                print(("Key {} got empty value".format(key)))
                return False
    return True


# rerun a function if fail a number of times
def rerunIfFail(function, selenium=None, screenshot=False, testname="default.png", number=3, delay=5):
    if number == 0: 
        if function: 
            return True
        
    for i in range(0,int(number)):
        if function: 
            return True
        time.sleep(delay)

    # if never succeed, return false
    if screenshot:
        selenium.assertAction(screenshot=testname)
    return False


# compare diff between str or int
def compare(v1, v2, t):
    if type(v1) != type(v2):
        print(("Different types between "+str(v1)+" and "+str(v2)))
        return False

    if type(v1) is str:
        if v1 != v2:
            try:
                if is_similar_datetime(v1, v2):
                    return True
            except:
                print(("Values "+str(v1)+" and "+str(v2)+" are not in datetime format."))
            print(("Values "+str(v1)+" and "+str(v2)+" is different."))
            return False

    if type(v1) is int:
        try:
            if abs(v1 - v2)/max(v1,v2)*100 > t:

                print(("Values "+str(v1)+" and "+str(v2)+" exceed threshold "+str(t)+"%"))
                return False

        except ZeroDivisionError:
            return True

    return True


# compare diff between dict and list
def traverse(d1, d2, t):
    b = True

    if type(d1) != type(d2):
        print(("Different types between "+str(type(d1))+" and "+str(type(d2))))
        return False
    
    #for python3, unicode is automatically str so we can skip conversion to str
    if sys.version_info < (3,0):
        if isinstance(d1, str):
            try:
                d1 = json.loads(d1)
            except:
                #not really a dictionary
                try: 
                    d1 = str(d1)
                except:
                    d1 = d1.encode('utf-8')

        if isinstance(d2, str):
            try:
                d2 = json.loads(d2)
            except:
                #not really a dictionary
                try:
                    d2 = str(d2)
                except:
                    d2 = d2.encode('utf-8')

    else:
        #this is python3
        try:
            d1 = json.loads(d1)
        except:
            pass

        try:
            d2 = json.loads(d2)
        except:
            pass

    if type(d1) is dict: 
        pop_dict_keys(d1)
        pop_dict_keys(d2)

        if sorted(d1.keys()) == sorted(d2.keys()):
            for k in list(d1.keys()):
                b = b and traverse(d1[k],d2[k],t)
        else:
            diff = set(d1.keys()) - set(d2.keys())
            print(("Dict key diff at "+str(diff)))
            return False

    elif type(d1) is list:
        if len(d1) == len(d2):
            for i in range(0,len(d1)):
                b = b and traverse(d1[i],d2[i],t)
        else:
            diff = abs(len(d1) - len(d2))
            print(("List length diff "+str(diff)))
            return False
    else:
        if not compare(d1,d2,t):
            return False

    return b

# the list of dictionary keys we want to ignore in traverse() is getting out of hand so we moved to separate function
def pop_dict_keys(item):
    if 'messagedate' in item:
        item.pop('messagedate')
    if 'lasttime' in item:
        item.pop('lasttime')
    if 'jti' in item:
        item.pop('jti')

# return difference between dict and list
def difference(d1, d2):
    if type(d1) != type(d2):
        print(("Different types between "+str(type(d1))+" and "+str(type(d2))))
        return False

    if type(d1) is dict:
        return {k : d2[k] for k in set(d2) - set(d1)}

    elif type(d1) is list:
        try:
            return set(d2) - set(d1)
        except: # a list of JSONs
            d2_set = {json.dumps(obj) for obj in d2}
            d1_set = {json.dumps(obj) for obj in d1}
            return d2_set - d1_set

# iterate a list and yield each item
def iterItem(self, item):
    itemList = []
    if type(item) == list: 
        itemList = item
    else:
        itemList.append(item)   
    for i in itemList:
        yield i

# return equal if two lists contain same texts
def compareStringLists(a, b):
    if type(a) != list or type(b) != list:
        return False
    if len(a) != len(b):
        return False
    intersect = set(a) & set(b)
    return len(intersect) == len(a)

def test_compareStringLists():
    a = ['a', 'b', 'c']
    b = ['b', 'c', 'd']
    c = ['c', 'd']
    d = []
    a_copy = ['a', 'b', 'c']
    a_copy_shuffled = ['c', 'a', 'b']
    assert compareStringLists(True, a) == False
    assert compareStringLists(1, a) == False
    assert compareStringLists(b, a) == False
    assert compareStringLists(c, a) == False
    assert compareStringLists(d, a) == False
    assert compareStringLists(a_copy, a) == True
    assert compareStringLists(a_copy_shuffled, a) == True

def isValidIPv4Address(address):
    if type(address) != str and type(address) != str:
        print(('Address is not in str format, it is in type {}'.format(type(address))))
        return False
    try:
        address = str(address)
        address = ip_address(address)
    except:
        return False
    return True

def test_isValidIPv4Address():
    assert isValidIPv4Address(1) == False
    assert isValidIPv4Address(None) == False
    assert isValidIPv4Address('127.0.0') == False
    assert isValidIPv4Address('This is not an ip address') == False
    assert isValidIPv4Address('127.0.0.1:3000') == False
    assert isValidIPv4Address('127.0.0.1') == True
    assert isValidIPv4Address('192.168.10.189') == True
    assert isValidIPv4Address('192.168.10.189') == True

def isValidMACAddress(address):
    if type(address) != str and type(address) != str:
        return False
    address.encode('ascii','ignore')
    if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", address.lower()):
        return True
    return False

def test_isValidMACAddress():
    assert isValidMACAddress(1) == False
    assert isValidMACAddress(None) == False
    assert isValidMACAddress('64:76:ba:9c:19') == False
    assert isValidMACAddress('This is not a MAC address') == False
    assert isValidMACAddress('00-14-22-gg-23-45') == False
    assert isValidMACAddress('64:76:ba:9c:19:4a') == True
    assert isValidMACAddress('00:0a:95:9d:68:16') == True
    assert isValidMACAddress('00:0a:95:9d:68:16') == True
