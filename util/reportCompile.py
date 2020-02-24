import pdb,time, re, os
import xml.etree.cElementTree as ET
import datetime
from glob import glob
from shutil import copyfile
from distutils.dir_util import copy_tree
import time;
ts = time.time()

homedir = "/mnt/efs/zbat/" #"/mnt/efs/zbat/"
shareddir = "userContent/"
openvasdir = homedir + "OpenVAS/" #Change Openvas to this  
lintdir = homedir + "TSLint/"
artifact_dir = "/job/ZBAT_Cron_Tests/job/Report Compile Proto/lastSuccessfulBuild/artifact/"

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

b = sorted(os.listdir(openvasdir))
delist = []
for element in b:
    if element.find("ZingCloud") == -1:
        print "removed"
        delist.append(element)

for dell in delist:
    b.remove(dell)
print b

reportfile  = open(openvasdir + b[-1], "r")
print (openvasdir + b[-1])
fcontent = reportfile.readlines()
vasLines = []
vasLines.append(fcontent[0])
for line in fcontent[1:]:
    vasLines.append(line.split(" "))
reportfile.close()  
if fcontent[1][0] == 'Low' and int(fcontent[1][-1]) > 0:  
    pass 
elif fcontent[2][0] == 'Medium' and int(fcontent[2][-1]) > 0: 
    pass
elif fcontent[3][0] == 'High' and int(fcontent[3][-1]) > 0:   
    pass

htmlfile = open(homedir + "summary/myreport.html", "w+")

htmlfile.write("<!DOCTYPE html>\n<html>\n<body>\n")


a = sorted(os.listdir(openvasdir))
for element in a:
    if element.find("Inspector") == False:
        a.remove(element)
if ts - os.path.getmtime(openvasdir + b[len(b)/2 -1]) > 604800:
    print ("ERROR: OpenVAS ZingCloud Scan report too old")
    htmlfile.write("<h2>ERROR: OpenVAS ZingCloud Scan report too old</h2>\n")
else:
    htmlfile.write("<h1>OpenVAS</h1>\n")
    htmlfile.write("<h2>OpenVAS ZingCloud Scan</h2>\n")
    htmlfile.write("<h2>Report Date:" + str(modification_date(openvasdir + b[-1])) + "</h2>")
    htmlfile.write("<p>"+vasLines[0]+"</p>\n")
    for line in vasLines[1:]:
        htmlfile.write("<p>"+line[0]+" Threats: "+line[-1]+"</p>\n")
    #Port things
    #open(shareddir + "currentZingCloud.xml", 'w+').close()
    copyfile(openvasdir + str(b[len(b)/2 -1]), "currentZingCloud.txt")
    htmlfile.write("<h3><a href=\""+artifact_dir+ "currentZingCloud.txt"+ "\">Click here to go to full XML results</a></h3>\n")

delist = []
a = sorted(os.listdir(openvasdir))
for element in a:
    if element.find("Inspector") == -1:
        delist.append(element)
for dell in delist:
    a.remove(dell)

reportfile  = open(openvasdir + a[-1], "r")
print (openvasdir + a[-1])
fcontent = reportfile.readlines()
vasLines = []
vasLines.append(fcontent[0])
for line in fcontent[1:]:
    vasLines.append(line.split(" "))
reportfile.close() 

if fcontent[1][0] == 'Low' and int(fcontent[1][-1]) > 0:  
    pass 
elif fcontent[2][0] == 'Medium' and int(fcontent[2][-1]) > 0: 
    pass
elif fcontent[3][0] == 'High' and int(fcontent[3][-1]) > 0:   
    pass
if ts - os.path.getmtime(openvasdir + a[-1]) > 604800:
    print ("ERROR: OpenVAS Inspector Scan report too old")
    htmlfile.write("<h2>ERROR: OpenVAS Inspector Scan report too old</h2>\n")
else:
    htmlfile.write("<p>------------------------</p>\n")
    htmlfile.write("<h1>OpenVAS</h1>\n")
    htmlfile.write("<h2>OpenVAS Inspector Scan</h2>\n")
    htmlfile.write("<h2>Report Date:" + str(modification_date(openvasdir + a[-1])) + "</h2>")
    htmlfile.write("<p>"+vasLines[0]+"</p>\n")
    for line in vasLines[1:]:
        htmlfile.write("<p>"+line[0]+" Threats: "+line[-1]+"</p>\n")

    #open(shareddir + "currentInspector.xml", 'w+').close()
    copyfile(openvasdir + str(a[len(a)/2 - 1]), "currentInspector.txt")
    htmlfile.write("<h3><a href=\"" + artifact_dir+ "currentInspector.txt"+ "\">Click here to go to full XML results</a></h3>\n")


htmlfile.write("<p>-----------------------------------------------------------------<p>\n")
htmlfile.write("<h1>Rapid 7</h1>\n")

spiderdir = homedir + "AppSpider/"
dirlist = sorted(glob(spiderdir+"*/"))

if ts - os.path.getmtime(dirlist[-1]+"report/VulnerabilitiesSummary.xml") > 604800:
    print ("ERROR: Appspider report too old")
    htmlfile.write("<h2>ERROR: Appspider report too old</h2>\n")
else:
    spiderfile = open(dirlist[-1]+"report/VulnerabilitiesSummary.xml")


    htmlfile.write("<h2>Report Date:" + str(modification_date(dirlist[-1]+"report/VulnerabilitiesSummary.xml")) + "</h2>")
    tree = ET.parse(dirlist[-1]+"report/VulnerabilitiesSummary.xml")

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

    htmlfile.write ("<p></p>\n")
    htmlfile.write ("<h3>VULNERABILITIES:"  + "</h3>\n")
    htmlfile.write ("<h4>Informational Vuln: " + str(inform_count)  + "</h4>\n")
    htmlfile.write ("<p>Low Vuln: " + str(low_count)  + "</p>\n")
    htmlfile.write ("<p>Medium Vuln: " + str(medium_count)  + "</p>\n")
    htmlfile.write ("<p>High Vuln: " + str(high_count)  + "</p>\n")
    htmlfile.write ("<p></p>\n")
    htmlfile.write ("<h3>BEST PRACTICES:"  + "</h3>\n")
    htmlfile.write ("<h4>Informational: " + str(bp_inform_count)  + "</h4>\n")
    htmlfile.write ("<p>Low: " + str(bp_low_count)  + "</p>\n")
    htmlfile.write ("<p>Medium: " + str(bp_medium_count)  + "</p>\n")
    htmlfile.write ("<p>High: " + str(bp_high_count)  + "</p>\n")
    htmlfile.write ("<p></p>\n")
    htmlfile.write ("<h3>PRIVACY:" + "</h3>\n")
    htmlfile.write ("<h4>Informational: " + str(pr_inform_count)  + "</h4>\n")
    htmlfile.write ("<p>Low: " + str(pr_low_count)  + "</p>\n")
    htmlfile.write ("<p>Medium: " + str(pr_medium_count)  + "</p>\n")
    htmlfile.write ("<p>High: " + str(pr_high_count) + "</p>\n")

    #open(shareddir + "currentAppspider.html" , 'w+').close()
    copy_tree(dirlist[-1], "AppSpider/")
    htmlfile.write("<h3><a href=\"" + artifact_dir+ "AppSpider/report/index.html" +"\">Click here to go to full report</a></h3>\n")

htmlfile.write ("<p>\n</p>\n")
htmlfile.write("<p>-----------------------------------------------------------------</p>\n")
htmlfile.write("<h1>TSLint</h1>\n")


if ts - os.path.getmtime(lintdir + "sample") > 604800:
    print ("ERROR: TSLint report too old")
    htmlfile.write("<h2>ERROR: TSLin report too old</h2>\n")
else:
    lint_count = 0
    lintList = {}
    lintFile= open(lintdir + "sample", 'r')
    htmlfile.write("<h2>Report Date:" + str(modification_date(lintdir + "sample")) + "</h2>")
    content = lintFile.readlines()
    for con in content:
        if con == "\n":
            continue
        splity = con.split(": ")
        splity2 = splity[1].split(" - ")
        filename = splity2[0].split(":")[0]
        filename = re.sub("[\(\[].*?[\)\]]", "", filename)
        error = splity2[1]
        if filename in lintList:
            if error in lintList[filename]:
                lintList[filename][error] += 1
            else:
                lintList[filename][error] = 0
                lint_count+=1
        else:
            lintList[filename] = {}

    htmlfile.write("<h2>Total unique Errors:" + str(lint_count) + "</h2>" +"\n")
    htmlfile.write ("<p>\n</p>\n")

    for file in lintList:
        for error in lintList[file]:
            htmlfile.write("<p>" + file + ": " + error + ": " + str(lintList[file][error]) + " errors</p>\n")
    copyfile(lintdir+"sample", "currentLINT.txt")
    htmlfile.write("<h3><a href=\"" + artifact_dir+ "currentLINT.txt" +"\">Click here to go to full report</a></h3>\n")

htmlfile.write("</body>\n</html>\n") #This always goes in end

htmlfile.close()


# Add report date
# Report must be within last 7 days
#TSLint summary count for total unique errors
