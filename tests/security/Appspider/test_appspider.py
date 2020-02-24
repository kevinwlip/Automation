import json
import subprocess
import pdb
import time
from datetime import datetime as datetime
import os
import os.path
import pytest
import xml.etree.ElementTree as ET


@pytest.mark.parametrize("date_out", [1,2,3,4,5,6,7,8,9,10,11,12,9999])
@pytest.mark.parametrize("minimum", ["low","medium","high"])
def test_AppSpider(minimum, date_out):
    mount_dir = "/mnt/efs/zbat/AppSpider/"
    dir_list = os.listdir(mount_dir)
    date_list = []

    for dire in dir_list:
        if dire[0] == "2":
            date_list.append(dire)

    con_date_list = []

    for date in date_list:
        temp = datetime.strptime(date,"%Y_%m_%d_%H_%M_%S")
        con_date_list.append(temp)


    con_date_list = sorted(con_date_list)


    while len(con_date_list) > 0:    
        date_diff = datetime.now() - con_date_list[-1]
        if abs(date_diff.days) > date_out:
            print "ERROR: Report too old"
            assert False
        recent_dir = con_date_list[-1].strftime("%Y_%m_%d_%H_%M_%S")

        xml_path = mount_dir + recent_dir +  "/report/VulnerabilitiesSummary.xml"
        if os.path.isfile(xml_path):
            break
        else:
            con_date_list.pop()

        if len(con_date_list) == 0:
            print ("Error: No complete reports found")
            assert False

    tree = ET.parse(xml_path)
    root = tree.getroot()
    list_of_stuff = []
    list_of_vulns = root.findall(".//Vuln")
    for vuln in list_of_vulns:
        score = vuln.findall("AttackScore")
        attack_type = vuln.findall("AttackClass")
        name = vuln.findall("VulnType")
        ID = vuln.findall("DbId")
        list_of_stuff.append((score, attack_type, name, ID))

    inform_count = 0
    low_count = 0
    medium_count = 0
    high_count = 0
    bp_inform_count = 0
    bp_low_count = 0
    bp_medium_count = 0
    bp_high_count = 0
    pr_inform_count = 0
    pr_low_count = 0
    pr_medium_count = 0
    pr_high_count = 0

    for thing in list_of_stuff:
        if thing[0][0].text == "1-Informational":
            if thing[1][0].text == "Best Practice":
                bp_inform_count += 1
            elif thing[1][0].text == "Privacy":
                pr_inform_count += 1
            else:
                inform_count += 1
        elif thing[0][0].text == "2-Low":
            if thing[1][0].text == "Best Practice":
                bp_low_count += 1
            elif thing[1][0].text == "Privacy":
                pr_low_count += 1
            else:
                low_count += 1
        elif thing[0][0].text == "3-Medium":
            if thing[1][0] == "Best Practice":
                bp_medium_count += 1
            elif thing[1][0].text == "Privacy":
                pr_low_count += 1
            else:
                medium_count += 1
        elif thing[0][0].text == "4-High":
            if thing[1][0] == "Best Practice":
                bp_high_count += 1
            elif thing[1][0].text == "Privacy":
                pr_low_count += 1
            else:
                high_count += 1


    print ("Directory of report: " + xml_path)
    print ("")
    print ("VULNERABILITIES:")
    print ("Informational Vuln: " + str(inform_count))
    print ("Low Vuln: " + str(low_count))
    print ("Medium Vuln: " + str(medium_count))
    print ("High Vuln: " + str(high_count))
    print ("")
    print ("BEST PRACTICES:")
    print ("Informational: " + str(bp_inform_count))
    print ("Low: " + str(bp_low_count))
    print ("Medium: " + str(bp_medium_count))
    print ("High: " + str(bp_high_count))
    print ("")
    print ("PRIVACY:")
    print ("Informational: " + str(pr_inform_count))
    print ("Low: " + str(pr_low_count))
    print ("Medium: " + str(pr_medium_count))
    print ("High: " + str(pr_high_count))

    if minimum == "informational":
        assert inform_count==0 and low_count == 0 and medium_count == 0 and high_count == 0 and pr_inform_count==0 and pr_low_count == 0 and pr_medium_count == 0 and pr_high_count == 0 and bp_inform_count==0 and bp_low_count == 0 and bp_medium_count == 0 and bp_high_count == 0
    elif minimum == "low":
        assert low_count == 0 and medium_count == 0 and high_count == 0 and pr_low_count == 0 and pr_medium_count == 0 and pr_high_count == 0 and bp_low_count == 0 and bp_medium_count == 0 and bp_high_count == 0
    elif minimum == "medium":
        assert medium_count == 0 and high_count == 0 and pr_medium_count == 0 and pr_high_count == 0 and bp_medium_count == 0 and bp_high_count == 0
    elif minimum == "high":
        assert high_count == 0 and pr_high_count == 0 and bp_high_count == 0


