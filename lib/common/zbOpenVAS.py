#!/usr/bin/python

from .zbSSH import Shell
import xml.etree.cElementTree as ET
import pdb, time
from datetime import datetime
from zbConfig import defaultEnv


configDict = {"Full and fast" : "daba56c8-73ec-11df-a475-002264764cea",
 "Full and fast ultimate" : "698f691e-7489-11df-9d8c-002264764cea",
 "Full and very deep" : "708f25c4-7489-11df-8094-002264764cea",
 "Full and very deep ultimate": "74db13d6-7489-11df-91b9-002264764cea"
}

REPORT_PDF_ID = "c402cc3e-b531-11e1-9163-406186ea4fc5"
REPORT_XML_ID = "a994b278-1f62-11e1-96ac-406186ea4fc5"

SPECIAL_SAUCE = "<alive_tests>Scan Config Default</alive_tests>"

homedir = "/mnt/efs/zbat/OpenVAS/"

class OpenVAS:

    def __init__(self):
        self.prefix = ""
        self.init_config = {}
        self.rcode = True

    def addThenRun(self,TargetDict): #Adds the specified targets and runs the scan on them
        TargetIDDict = {}
        TaskIDDict = {}
        try:
            entry = Shell(**self.init_config)
            # disabling update for now, since we are getting a lot of permission error AP-5064.  Kaiyi will fix.
            #output = entry.runCommand("greenbone-nvt-sync")
            #print output
            for Target in TargetDict:
                command = "".join([self.prefix, "omp --xml='\n<create_target>\n<name>",Target,"</name>\n<hosts>",TargetDict[Target],"</hosts>\n<alive_tests>Consider Alive</alive_tests></create_target>'"])
                output = entry.runCommand(command)
                if output[1] != '':
                    print(output[1])
                root = ET.fromstring(output[0])
                if "status" in root.attrib and root.attrib["status"] == "400":
                    print(root.attrib["status"])
                    outy_list = entry.runCommand(self.prefix + "omp -T \"" +TargetDict[Target]+ "\"")[0].split(" ")
                    TargetIDDict[Target] = outy_list[0]
                else:
                    TargetIDDict[Target] = root.attrib["id"]
                secondCommand = "".join([self.prefix, "omp --xml='\n<create_task>\n<name>", Target, " Scan</name>\n<comment>Deep scan on ",Target,"</comment>\n<config id=\"",configDict["Full and very deep ultimate"],"\"/>\n","<target id=\"", TargetIDDict[Target],"\"/>\n","</create_task>'"])
                output = entry.runCommand(secondCommand)
                if output[1] != '':
                    print(output[1])
                root = ET.fromstring(output[0])
                TaskIDDict[Target] = root.attrib["id"]

                thirdCommand = "".join([self.prefix, "omp --xml='<start_task task_id=\"",TaskIDDict[Target],"\"/>'"])
                output = entry.runCommand(thirdCommand)
                if output[1] != '':
                    print(output[1])
            entry.close()

            return TargetIDDict, TaskIDDict
        except Exception as e:
            print(e)
            return False


    def monitorTasks(self,TargetIDDict,TaskIDDict): # Monitor the running tasks specified by input and updates their status every 15 seconds.
        try:
            retry_count=0
            entry = Shell(**self.init_config)
            while TaskIDDict:
                time.sleep(15)
                for task in TaskIDDict:
                    command = "".join([self.prefix, "-G ", TaskIDDict[task]])
                    output_list = entry.runCommand(command)[0].split(" ")
                    if output_list[2] == 'Running':
                        print(task + " Progress " + output_list[3] + output_list[4] + " " + str(datetime.utcfromtimestamp(time.time())))
                        print("")
                    elif output_list[2] == 'Requested' or output_list[2] == 'New':
                        pass
                    elif output_list[2] == 'Done':
                        time.sleep(5)
                        self.exportThenClean(entry,task,TargetIDDict,TaskIDDict)
                        TaskIDDict.pop(task,None)
                        break
                    else:
                        retry_count+=1
                        print(output_list)
                        if retry_count > 9:
                            raise Exception('Task terminated unexpectedly')
                        continue
                    retry_count=0
            entry.close()
        except Exception as e:
            print(e)
            entry.close()
            self.rcode = False
            return False

    def exportThenClean(self,entry,Target, TargetIDDict,TaskIDDict):  #Extracts the resulting report of a terminated task from the server
        reportIDDict = {}
        try:
            command = "".join([self.prefix, "omp -iX '<get_tasks task_id=\"",TaskIDDict[Target],"\" details=\"1\"/>'"])
            output = entry.runCommand(command)
            entry.runCommand("admin")
            if output[1] != '':
                print(output[1])
            root = ET.fromstring(output[0])

            time.sleep(1)
            for taggy in root[1]:
                if taggy.tag == 'last_report' or taggy.tag == 'current_report' or taggy.tag == 'reports':
                    reportIDDict[Target] = taggy[0].attrib['id']
                    break
            if reportIDDict == {}:
                return False
            #secondCommand = "".join([self.prefix, "omp -iX '<get_reports report_id=\"",reportIDDict[Target],"\" format_id=\"",REPORT_XML_ID,"\"/>'"])
            # get reports with min_qod=0, meaning obtain all security report even with low qod scores
            secondCommand = "".join([self.prefix, "omp -iX '<get_reports report_id=\"",reportIDDict[Target], "\" filter=\"min_qod=0 autofp=0 apply_overrides=1 notes=1 overrides=1 result_hosts_only=1 first=1 rows=100 sort-reverse=severity levels=hml\" " ,"format_id=\"",REPORT_XML_ID,"\"/>'"])
            output = entry.runCommand(secondCommand)
            if output[1] != '':
                print(output[1])
            self.parseReport(Target,output[0])
        except Exception as e:
            print(e)
            entry.close()
            self.rcode = False
            return False


    def parseReport(self,Target,output): #Parses the report and checks
        try:
            low_c = 0 
            med_c = 0
            high_c = 0 
            root = ET.fromstring(output)
            for stuff in root.iter('result'):
                for thing in stuff.iter('threat'):
                    if thing.text.lower() == "low":
                        low_c = low_c + 1
                    elif thing.text.lower() == "medium":
                        med_c = med_c + 1
                    elif thing.text.lower() == "high":
                        high_c = high_c + 1
            print("-----------------------------")
            print("Summary of " + Target) 
            print("Low threats= " + str(low_c))
            print("Medium threats= " + str(med_c))
            print("High threats= " + str(high_c ))
            print("-----------------------------")
            if med_c > 0 or high_c > 0:
                self.rcode = False

            
            filetime = str(datetime.utcfromtimestamp(time.time()))
            reportfile  = open(homedir+"OpenVAS Report " +Target+ " short "+filetime, "w+")
            reportfile.write("Summary of " + Target + "\n")
            reportfile.write("Low threats= " + str(low_c) + "\n")
            reportfile.write("Medium threats= " + str(med_c) + "\n")
            reportfile.write("High threats= " + str(high_c) + "\n")
            reportfile.close()

            reportfile2 = open(homedir+"OpenVAS Report " +Target+ " long "+filetime, "w+")
            reportfile2.write(output)
            reportfile.close()

        except Exception as e:
            print(e)
            return False


    def run_main(self,device,init_stuff):
        self.init_config = init_stuff
        self.init_config["port"] = int(init_stuff["port"])
        self.prefix = "omp -u " + self.init_config["username"] + " -w " + self.init_config["password"] + " "
        print(self.prefix)
        try:
            testIDDict = device
            hold = self.addThenRun(testIDDict)
            if hold == False:
                return False
            else:
                temp1, temp2 = hold
            self.monitorTasks(temp1,temp2)
        except Exception as e:
            print(e)
            return False
        return self.rcode





















