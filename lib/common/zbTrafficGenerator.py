#!/usr/bin/python

#######################################################################################
#  Author : Vinh Nguyen
#    Date : 6/18/17
#######################################################################################

import pdb, time, os, json
from simple_ostinato import Drone
from simple_ostinato.protocols import Mac, Ethernet, IPv4, Udp, Tcp, Payload
from .zbSSH import Shell, CLI
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

# global variable
ZBAT_HOME = os.environ['ZBAT_HOME']

def replayPcap(pcapPath, intf, IPs, MACs, TG_HOST, TG_PORT, TG_UNAME, TG_PWD):
    kwargs = {}
    kwargs['hostname'] = TG_HOST
    kwargs['username'] = TG_UNAME
    kwargs['password'] = TG_PWD
    kwargs['port'] = TG_PORT
    packets = Tcpreplay(**kwargs)
    return packets.tcpreplay(pcapPath, intf, IPs, MACs)

class Ostinato():
    """
    Example:

    Attributes:

    Todo:

    """

    def __init__(self, host):
        self.drone = Drone(host, connect=False)
        self.drone.connect()
        self.fetchPorts()


    def fetchPorts(self):
        self.portDict = {}
        self.drone.fetch_ports()
        for port in self.drone.ports:
            if port.is_enabled:  self.portDict[port.name] = port.port_id


    def configStream(self, **kwargs):
        self.txPort = self.drone.get_port_by_id(self.portDict[kwargs['txPort']])
        #if 'rxPort' in kwargs: rxPort = self.drone.get_port_by_id(self.portDict[kwargs['rxPort']])

        self.stream = self.txPort.add_stream()
        self.stream.layers = self.layers

        self.stream.name = 'ZingBox Stream'
        self.stream.unit = kwargs['unit'] if 'unit' in kwargs else 'PACKETS'
        self.stream.mode = kwargs['mode'] if 'mode' in kwargs else'FIXED'
        self.stream.next = kwargs['next'] if 'next' in kwargs else 'STOP'
        
        if self.stream.unit == 'PACKETS':
            self.stream.num_packets = kwargs['packets'] if 'packets' in kwargs else 1
            self.stream.packets_per_sec = kwargs['pps'] if 'pps' in kwargs else 1

        self.stream.is_enabled = True
        self.stream.save()


    def craftPacket(self, **kwargs):
        mac = self.MACLayer(**kwargs)
        eth = self.EthLayer(**kwargs)
        ip = self.IPLayer(**kwargs)
        #udp = self.UDPLayer(**kwargs)
        payload = self.PayloadLayer(**kwargs)
        self.layers = [mac, eth, ip, payload]



    def MACLayer(self, **kwargs):
        mac = Mac()
        mac.source = kwargs['srcMAC'] if 'srcMAC' in kwargs else 'ea:00:00:00:00:11'
        if 'macSrcMode' in kwargs: 
            mac.source_mode = kwargs['macSrcMode'] 
            mac.source_count = kwargs['macSrcCount'] if 'macSrcCount' in kwargs else 100
            mac.source_step = kwargs['macSrcStep'] if 'macSrcStep' in kwargs else 1
        mac.destination = kwargs['dstMAC'] if 'dstMAC' in kwargs else 'eb:00:00:00:00:22'
        if 'macDstMode' in kwargs: 
            mac.destination_mode = kwargs['macDstMode'] 
            mac.destination_count = kwargs['macDstCount'] if 'macDstCount' in kwargs else 100
            mac.destination_step = kwargs['macDstStep'] if 'macDstStep' in kwargs else 1
        return mac


    def EthLayer(self, **kwargs):
        eth = Ethernet()
        if 'ethtype' in kwargs: eth.ether_type = kwargs['ethType']
        return eth      


    def IPLayer(self, **kwargs):
        ip = IPv4()
        ip.source = kwargs['srcIP'] if 'srcIP' in kwargs else '1.2.3.4'
        if 'ipSrcMode' in kwargs: 
            ip.source_mode = kwargs['ipSrcMode'] 
            ip.source_count = kwargs['ipSrcCount'] if 'ipSrcCount' in kwargs else 100
            ip.source_step = kwargs['ipSrcStep'] if 'ipSrcStep' in kwargs else 1
        ip.destination = kwargs['dstIP'] if 'dstIP' in kwargs else '5.6.7.8'
        if 'ipDstMode' in kwargs: 
            ip.destination_mode = kwargs['ipDstMode'] 
            ip.destination_count = kwargs['ipDstCount'] if 'ipDstCount' in kwargs else 100
            ip.destination_step = kwargs['ipDstStep'] if 'ipDstStep' in kwargs else 1
        return ip       


    def UDPLayer(self, **kwargs):
        udp = Udp()
        if 'udpSrcPort' in kwargs:  udp.source = int(kwargs['udpSrcPort'])
        if 'udpDstPort' in kwargs:  udp.destination = int(kwargs['udpDstPort'])


    def TCPLayer(self, **kwargs):
        tcp = Tcp()
        if 'tcpSrcPort' in kwargs:  tcp.source = int(kwargs['tcpSrcPort'])
        if 'tcpDstPort' in kwargs:  tcp.destination = int(kwargs['tcpDstPort'])


    def PayloadLayer(self, **kwargs):
        payload = Payload()
        if 'payload' in kwargs:  payload.pattern = kwargs['payload'] 
        return payload


    def sendStream(self, **kwargs):
        self.craftPacket(**kwargs)
        self.configStream(**kwargs)
        self.txPort.clear_stats()
        self.txPort.start_send()
        stime = kwargs['sleep'] if 'sleep' in kwargs else 10
        time.sleep(stime)
        
        self.txPort.stop_send()


class Tcpreplay():
    
    def __init__(self, **kwargs):
        #self.ssh = Shell(**kwargs)
        self.ssh = CLI(**kwargs)


    # check if sudo is needed
    def checkSudo(self):
        output, err = self.ssh.runCommand('sudo ls')
        if err or re.search('command not found', output, re.IGNORECASE):
            return False
        else:
            return True


    def tcpreplay(self, f, intf, IPs, MACs):
        idx = f.rfind('.')
        if idx != -1:
            fRewrite = f[:idx]+"_r.pcap"
        else:
            print ("invalid file name")
            return False
        
        rewrite = (IPs is not None) and (MACs is not None)
        if rewrite:
            modifiedFile = self.tcprewrite(f, fRewrite, IPs, MACs)
        else: 
            modifiedFile = f

        if not modifiedFile: 
            print ("tcprewrite unsuccessful")
            return False
        else:
            # check if this is docker container
            output, err = self.ssh.runCommand('env')
            docker = True if output.find('DOCKER_MACHINE=true') >= 0 else False

            # replay the newly generated pcap with tcpreplay
            if not intf['server-client']:
                if docker or not self.checkSudo:
                    cmd = "tcpreplay --mbps=5 --intf1="+intf['intf1']+" "+modifiedFile
                else:
                    cmd = "echo " + self.ssh.password + " | sudo -S tcpreplay --mbps=5 --intf1="+intf['intf1']+" "+modifiedFile
                output, err = self.ssh.runCommand(cmd)
                if err:
                    print (err)
            else:
                # prepare a cache file to split the traffic
                idx = modifiedFile.rfind('.')
                if idx != -1:
                    cachefile = modifiedFile[:idx]+".prep"
                else:
                    print ("invalid file name")
                    return False

                cmd = "tcpprep --auto=bridge --pcap=" + modifiedFile+" --cachefile=" + cachefile
                output, err = self.ssh.runCommand(cmd)
                # tcpreplay
                if docker or not self.checkSudo:
                    cmd = "tcpreplay --mbps=5 --cachefile=" + cachefile + " --intf1=" + intf['intf1'] + " --intf2=" + intf['intf2'] + " " + modifiedFile
                else:
                    cmd = "echo " + self.ssh.password + " | sudo -S tcpreplay --mbps=5 --cachefile=" + cachefile + " --intf1=" + intf['intf1'] + " --intf2=" + intf['intf2'] + " " + modifiedFile
                output, err = self.ssh.runCommand(cmd)
                print (output)
                if err:
                    print (err)
            
                # remove prep file
                cmd = "rm " + cachefile
                output, err = self.ssh.runCommand(cmd)
                if err:
                    print (err)

            if rewrite:
                # remove modified pcap
                cmd = "rm " + modifiedFile
                output, err = self.ssh.runCommand(cmd)

            if (output.find("Traceback (most recent call last):") != -1) or (output.find("Error") != -1) or (output.find("invalid") != -1):
                print ("tcpreplay error")
                print (output)
                return False
    
        self.ssh.close()    
        return True

    # parameters:
    # f: input file path
    # fRewrite: output file path
    # IPs: the old/new mapping of IPs
    # MACs: the old/new mapping of MACs
    def tcprewrite(self, f, fRewrite, IPs, MACs):
        modifiedFile = fRewrite

        # change MACs using scapy
        oldMAC = []
        newMAC = []
        for m in MACs:
            oldMAC.append(m[0])
            newMAC.append(m[1])
        fRewriteMAC = self.changeMAC(f, oldMAC, newMAC).rstrip()
        modifiedFile = fRewriteMAC
        if not modifiedFile:
            print ("change mac unsuccessful")
            return False

        # change IPs using tcprewrite
        cmd = " --infile="+modifiedFile+" --outfile="+fRewrite+" --skipbroadcast"
        IPcmd = " --pnat="
        for i in range(len(IPs)):
            if i != 0:
                IPcmd += ","
            IPcmd += IPs[i][0]+":"+IPs[i][1]
        cmd = IPcmd + cmd

        cmd = "tcprewrite" + cmd
        output, err = self.ssh.runCommand(cmd)
        modifiedFile = fRewrite
        
        if err:
            print (err)
            return False

        cmd = "rm " + fRewriteMAC
        output, err = self.ssh.runCommand(cmd)

        return modifiedFile

    def changeMAC(self, fRewrite, oldMAC, newMAC):
        print ("changing MAC address...")
        if len(oldMAC) != len(newMAC):
            print ("number of old MAC and number of new MAC don't match")
            return False
        MAC = ZBAT_HOME + "util/zbMAC.py"
        MACVar = ZBAT_HOME + "util/zbMAC2.py"

        with open(MACVar, "w") as fileV:
            fileV.write('import logging\nlogging.getLogger("scapy.runtime").setLevel(logging.ERROR)\nfrom scapy.all import *\n')
            fileV.write("fRewrite = '"+fRewrite+"'\n")
            
            fileV.write("old = ")
            json.dump(oldMAC, fileV)
            fileV.write("\n")
            
            fileV.write("new = ")
            json.dump(newMAC, fileV)
            fileV.write("\n")
            
            with open(MAC, "r") as file:
                for line in file:
                    fileV.write(line) 
        fRewrite2 = os.popen("cat "+MACVar+" | sshpass -p '"+self.ssh.password+"' ssh -p "+str(self.ssh.port)+" "+self.ssh.username+"@"+self.ssh.hostname+" python -").read()
        os.system("rm "+MACVar)

        if fRewrite2 != "invalid file name":
            return fRewrite2
        else:
            return False

    def changePayload(self, fRewrite):
        print ("changing payload...")
        payload = ZBAT_HOME + "util/zbPayload.py"
        payloadVar = ZBAT_HOME + "util/zbPayload2.py"

        with open(payloadVar, "w") as fV:
            fV.write('import logging\nlogging.getLogger("scapy.runtime").setLevel(logging.ERROR)\nfrom scapy.all import *\n')
            fV.write('fRewrite = "'+fRewrite+'"\n')
            with open(payload, "r") as f:
                for line in f:
                    fV.write(line) 

        fRewrite2 = os.popen("cat "+payloadVar+" | sshpass -p '"+self.ssh.password+"' ssh -p "+str(self.ssh.port)+" "+self.ssh.username+"@"+self.ssh.hostname+" python -").read()
        os.system("rm "+payloadVar)

        if fRewrite2 != "invalid file name":
            return fRewrite2
        else:
            return False


            

# test 
'''
HOST = 'XX.XX.XX.XX'
USERNAME = 'XXXXX'
PASSWORD = 'XXXXX'
'''
'''
portid = 'ens160'
kwargs = {}
kwargs['txPort'] = portid
kwargs['rxPort'] = portid
kwargs['srcMAC'] = '00:11:22:aa:bb:cc'
kwargs['dstMAC'] = '00:01:02:03:04:05'
kwargs['srcIP'] = '1.2.3.4'
kwargs['dstIP'] = '5.6.7.8'
kwargs['pps'] = 10
kwargs['packets'] = 100
kwargs['pcap'] = 'capture.pcap'

#kwargs['ipSrcMode'] = 'INCREMENT'
#kwargs['ipSrcCount'] = 50
#kwargs['macSrcMode'] = 'INCREMENT'
#kwargs['macSrcCount'] = 50
kwargs['ipDstMode'] = 'INCREMENT'
kwargs['ipDstCount'] = 50
kwargs['macDstMode'] = 'INCREMENT'
kwargs['macDstCount'] = 50

traffic = Ostinato(HOST)
traffic.sendStream(**kwargs)
'''
'''
kwargs = {}
kwargs['hostname'] = HOST
kwargs['username'] = USERNAME
kwargs['password'] = PASSWORD
packets = Tcpreplay(**kwargs)
# config = {'sIP': '1.1.1.1', 'sport': '1', 'dIP': '2.2.2.2', 'dport': '2', 
# 'dMAC': 'aa:bb:cc:dd:02:02', 'sMAC': 'aa:bb:cc:dd:01:01','payload': "Zingbox Testing "}
# config = {'sIP': '1.1.1.1', 'sMAC': 'aa:bb:cc:dd:01:01'}
intf = {'intf1': 'ens160', 'intf2':'ens192', 'server-client': False}
# packets.tcpreplay("./pcaps/malware/WannaCry-05-17.pcap", config, intf)
# packets.tcprewrite("./pcaps/normal/ESPN.pcap", "./pcaps/normal/ESPN_r.pcap", config, None)

IPs = ['192.168.0.1', '192.168.0.3', '192.168.0.6']
configs = []
for i in range(1, len(IPs)+1):
    config = {'IP': '1.1.1.'+str(i), 'MAC': 'aa:bb:cc:dd:01:'+str(i).zfill(2)}
    configs.append(config)

packets.tcprewrite("./pcaps/malware/WannaCry-cleaned.pcap", "./pcaps/malware/WannaCry-cleaned_r.pcap", configs, IPs)
'''
