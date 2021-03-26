import atexit
import logging
from openwpm.task_manager import TaskManager
import os
import signal
import subprocess
import sys
import threading
from os import path


def wait_tasks(manager: TaskManager):
    for browser in manager.browsers:
        if browser.command_thread and browser.command_thread.is_alive():
            # Waiting for the command_sequence to be finished
            browser.command_thread.join()


def init_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("%s.log" % name)
    formatter = logging.Formatter("%(asctime)s - %(levelname)-8s: %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


class Wprgo:
    def __init__(self, wprgo_path, har_path) -> None:
        if (
            not path.isdir(har_path)
            or not path.isdir(path.join(har_path, "hostnames"))
            or not path.isdir(path.join(har_path, "wprgo"))
        ):
            raise ValueError("Must provide a valid har path")
        if not path.isfile(path.join(wprgo_path, "src", "wpr.go")):
            raise ValueError("Must provide a valid WprGo path")
        self.__wprgo_path = wprgo_path
        self.__har_path = har_path
        self.__logpipe = self.__LogPipe("replay")
        self.__process = None
        self.__wprgo_path = wprgo_path
        self.number = None
        self.crawl_date = har_path[har_path.rfind("/") + 1 :]
        self.total_number = len(os.listdir(path.join(self.__har_path, "hostnames")))
        atexit.register(self.stop_replay)

    def is_running(self) -> int:
        if self.__process != None:
            return self.number
        return -1

    # number: number of wprgo archive to be replayed
    def replay(self, number):
        # skip if already running
        if self.is_running() == number:
            return self.get_hostnames(number)
        # stop running replay(if there is) for other number
        if self.__process != None:
            self.stop_replay()
        if number > self.total_number or number < 0:
            raise ValueError(
                "Number should be non-negative and should not exceed total archive number: %d"
                % self.total_number
            )
        archive_path = path.join(self.__har_path, "wprgo", "%d.wprgo" % number)
        # kill process on ports
        # let wprgo replay
        cli = (
            "go run src/wpr.go replay --http_port=8080 --https_port=8081 %s"
            % archive_path
        )
        self.number = number
        self.__process = subprocess.Popen(
            cli.split(),
            cwd=self.__wprgo_path,
            stdout=self.__logpipe,
            stderr=self.__logpipe,
            preexec_fn=os.setsid,
        )
        ## TODO: check popen
        # Wait till wprgo replay server starts successfully(or fails)
        self.__logpipe.running.wait()
        if self.__process.poll() is not None:
            raise subprocess.CalledProcessError("Wprgo replay unsuccessful")
        print("Start replay session %s:%d" % (self.crawl_date, self.number))
        return self.get_hostnames(number)

    def get_hostnames(self, number) -> list:
        hostnames_path = path.join(self.__har_path, "hostnames", "%d.txt" % number)
        with open(hostnames_path) as f:
            content = f.readlines()
            hostnames = list()
            for x in content:
                x = x.strip()
                i = x.rfind(",")
                hostnames.append(x[:i])
        return hostnames

    def stop_replay(self):
        # Send the signal to all the process groups
        if self.__process != None:
            print("Stop replay session %s:%d" % (self.crawl_date, self.number))
            os.killpg(os.getpgid(self.__process.pid), signal.SIGKILL)
            self.__process = None
            self.__logpipe.running.clear()

    # https://codereview.stackexchange.com/questions/6567/redirecting-subprocesses-output-stdout-and-stderr-to-the-logging-module
    class __LogPipe(threading.Thread):
        def __init__(self, name):
            """Setup the object with a logger and start the thread"""
            threading.Thread.__init__(self)
            self.logger = init_logger(name)
            self.fdRead, self.fdWrite = os.pipe()
            self.pipeReader = os.fdopen(self.fdRead)
            self.running = threading.Event()
            self.setDaemon(True)
            self.start()

        def fileno(self):
            """Return the write file descriptor of the pipe"""
            return self.fdWrite

        def run(self):
            """Run the thread, logging everything."""
            for line in iter(self.pipeReader.readline, ""):
                line = line[20:]
                if not self.running.is_set():
                    if "Starting server" in line:
                        self.running.set()
                    elif "Error opening archive" in line:
                        self.logger.error(line.strip("\n"))
                        self.running.set()
                        raise ValueError(line)
                    elif "Failed to start server on" in line:
                        self.logger.error(line.strip("\n"))
                        self.running.set()
                        raise subprocess.CalledProcessError(line)
                    self.logger.info(line.strip("\n"))

                elif "http: TLS handshake error" in line:
                    if "remote error: tls: bad certificate" not in line:
                        self.logger.warning(line.strip("\n"))
                else:
                    self.logger.info(line.strip("\n"))

            self.pipeReader.close()

        # def close(self):
        #     """Close the write end of the pipe."""
        #     os.close(self.fdWrite)


def continue_from_log(wprgo: Wprgo):
    crawl_date = wprgo.crawl_date
    completed_index = set()
    continue_point_exist = False
    with open("crawl.log", "r") as log:
        for l in log:
            if l.find("Start a new crawl session. crawl_date:%s" % crawl_date) != -1:
                continue_point_exist = True
            if l.find("End of the crawl session. crawl_date:%s" % crawl_date) != -1:
                break
            if continue_point_exist:
                i = l.find("index")
                if i != -1:
                    completed_index.add(int(l[i + 5 : i + 10]))
    return completed_index
    # count = 0
    # for group_index in range(wprgo.total_number):
    #     num_per_group = len(wprgo.get_hostnames(group_index))
    #     for i in range(count, count + num_per_group):
    #         if i not in completed_index:
    #             return count, group_index, completed_index
    #     count += num_per_group
    # return count, group_index, completed_index


def get_wprgo_prefs() -> dict:
    custom_prefs = dict()
    custom_prefs["network.dns.forceResolve"] = "127.0.0.1"
    custom_prefs["network.socket.forcePort"] = "443=8081;80=8080"
    # custom_prefs["signon.management.page.breach-alerts.enabled"] = False
    # custom_prefs["geo.enabled"] = False
    # custom_prefs["services.settings.server"] = ""
    # custom_prefs["browser.region.network.url"] = ""
    return custom_prefs
