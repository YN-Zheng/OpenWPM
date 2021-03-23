import logging
import os
import signal
import subprocess
import sys
import threading
import atexit
from os import path


def init_logger() -> logging.Logger:
    logger = logging.getLogger("replay")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("replay.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)-8s: %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


def kill_on_port(port):
    subprocess.run(
        ("kill -9 $(lsof -t -i:%d)" % port).split(),
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


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
        self.__logpipe = self.__LogPipe(init_logger)
        self.__process = None
        self.__wprgo_path = wprgo_path
        self.number = None
        self.crawl_date = har_path[har_path.rfind("/") + 1 :]
        self.total_number = len(os.listdir(path.join(self.__har_path, "hostnames")))
        atexit.register(self.stop_replay)

    # number: number of wprgo archive to be replayed
    def replay(self, number):
        # stop running replay if there is
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
        def __init__(self, func):
            """Setup the object with a logger and start the thread"""
            threading.Thread.__init__(self)
            self.logger = func()
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


def get_wprgo_prefs() -> dict:
    custom_prefs = dict()
    # custom_prefs["network.proxy.http"] = "127.0.0.1"
    # custom_prefs["network.proxy.http_port"] = 8080
    # custom_prefs["network.proxy.ssl"] = "127.0.0.1"
    # custom_prefs["network.proxy.ssl_port"] = 8081
    # custom_prefs["network.proxy.type"] = 1
    # network.dns.forceResolve	127.0.0.1
    # network.socket.forcePort	443=8081;80=8080
    custom_prefs["network.dns.forceResolve"] = "127.0.0.1"
    custom_prefs["network.socket.forcePort"] = "443=8081;80=8080"
    # custom_prefs["signon.management.page.breach-alerts.enabled"] = False
    # custom_prefs["geo.enabled"] = False
    # custom_prefs["services.settings.server"] = ""
    # custom_prefs["browser.region.network.url"] = ""
    return custom_prefs
