from utils import get_data_path

crawl_date = "Jan_1_2018"
log = list()
with open(get_data_path(crawl_date, "datadir/openwpm.log"), "r") as f:
    for line in f:
        if line.find("OpenWPMStackDumpChild.jsm, line 119: ") == -1:
            log.append(line)

with open(get_data_path(crawl_date, "datadir/filtered.log"), "w") as f:
    for l in log:
        f.write(l)
