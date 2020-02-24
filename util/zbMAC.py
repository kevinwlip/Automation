
idx = fRewrite.rfind('.')
if idx != -1:
    fRewrite2 = fRewrite[:idx]+"MAC.pcap"
    os.system("> "+fRewrite2)
else:
    print ("invalid file name")

packets = rdpcap(fRewrite)
total_packets = len(packets)
for i in xrange(0,total_packets):
    if 'IP' in packets[i] and packets[i]['Ether'].src in old:
        idx = old.index(packets[i]['Ether'].src)
        packets[i]['Ether'].src = new[idx]

    if 'IP' in packets[i] and packets[i]['Ether'].dst in old:
        idx = old.index(packets[i]['Ether'].dst)
        packets[i]['Ether'].dst = new[idx]

    wrpcap(fRewrite2, packets[i], append=True)

print (fRewrite2)