log = list()
with open("datadir/openwpm.log", "r") as f:
    for line in f:
        if line.find("OpenWPMStackDumpChild.jsm, line 119: ") == -1:
            log.append(line)

with open("datadir/filtered.log", "w") as f:
    for l in log:
        f.write(l)
