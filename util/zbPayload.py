
idx = fRewrite.rfind('.')
if idx != -1:
    fRewrite2 = fRewrite[:idx]+"2.pcap"
    os.system("> "+fRewrite2)
else:
    print ("invalid file name")

packets = rdpcap(fRewrite)
total_packets = len(packets)
for i in xrange(0, total_packets):
    if ('TCP' in packets[i]) and (packets[i]['TCP'].payload):
        payloadBefore = len(packets[i]['TCP'].payload)
        packets[i]['TCP'].payload = Raw("Zingbox Testing ")
        payloadAfter = len(packets[i]['TCP'].payload)
        payloadDif = payloadAfter - payloadBefore
        packets[i]['IP'].len = packets[i]['IP'].len + payloadDif
    wrpcap(fRewrite2, packets[i], append=True)

print (fRewrite2)