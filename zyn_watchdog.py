from datetime import datetime

# Check the last log time. If log has been silence too long, it means the crawl has been frozen.
# return True if the program needs a restart.
def check_restart() -> bool:
    # Log time formate
    # 2021-03-23 23:18:58,767
    with open("crawl.log", "r") as f:
        for l in f:
            continue
    if l == None:
        return False
    log_time = l[0:19]
    last_time = datetime.strptime(log_time, "%Y-%m-%d %H:%M:%S")
    silence_time = (datetime.now() - last_time).total_seconds()
    print(int(silence_time))
    if silence_time > 180:
        return True
    return False


if __name__ == "__main__":
    check_restart()
