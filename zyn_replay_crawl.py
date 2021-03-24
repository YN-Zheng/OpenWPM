from logging import info
from pathlib import Path
import sys
import os
import utils
from custom_command import LinkCountingCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager


def main(crawl_date):
    archive_path = "/home/yongnian/HttpArchive"
    har_path = os.path.join(archive_path, crawl_date)
    wprgo_path = "/home/yongnian/Programs/catapult/web_page_replay_go"
    wprgo = utils.Wprgo(wprgo_path, har_path)

    # The list of sites that we wish to crawl
    NUM_BROWSERS = 8
    logger = utils.init_logger("crawl")
    sites_completed = utils.continue_from_log(wprgo.crawl_date)
    if len(sites_completed) == 0:
        logger.info("Start a new crawl session. crawl_date:%s" % wprgo.crawl_date)
    elif len(sites_completed) == 10000:
        logger.info("This crawl session is completed. crawl_date:%s" % wprgo.crawl_date)
    else:
        logger.info(
            "Continue from uncompleted crawl-------%s. %d sites completed"
            % (wprgo.crawl_date, len(sites_completed))
        )
    # Loads the default ManagerParams
    # and NUM_BROWSERS copies of the default BrowserParams

    manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
    browser_params = [
        BrowserParams(display_mode="headless") for _ in range(NUM_BROWSERS)
    ]

    # Update browser configuration (use this for per-browser settings)
    for i in range(NUM_BROWSERS):
        # Record HTTP Requests and Responses
        browser_params[i].http_instrument = True
        # Record cookie changes
        browser_params[i].cookie_instrument = True
        # Record Navigations
        browser_params[i].navigation_instrument = True
        # Record JS Web API calls
        browser_params[i].js_instrument = True
        # Record the callstack of all WebRequests made
        browser_params[i].callstack_instrument = True
        # Record DNS resolution
        browser_params[i].dns_instrument = True
        browser_params[i].prefs = utils.get_wprgo_prefs()
    # Update TaskManager configuration (use this for crawl-wide settings)
    manager_params.data_directory = Path("./datadir/")
    manager_params.log_directory = Path("./datadir/")

    # memory_watchdog and process_watchdog are useful for large scale cloud crawls.
    # Please refer to docs/Configuration.md#platform-configuration-options for more information
    manager_params.memory_watchdog = True
    manager_params.process_watchdog = True

    with TaskManager(
        manager_params,
        browser_params,
        SQLiteStorageProvider(Path("./datadir/replay-crawl-data.sqlite")),
        None,
    ) as manager:
        count = -1
        for n in range(0, wprgo.total_number):
            sites = wprgo.replay(n)
            # logger.info("Start crawl: %s:%d" % (wprgo.crawl_date, wprgo.number))
            # Visits the sites
            for index, site in enumerate(sites):
                count += 1
                if count in sites_completed:
                    continue

                def callback(
                    success: bool, val=site, total_index=count, index=index, group=n
                ) -> None:
                    # print(
                    #     f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
                    # )
                    logger.info(
                        "index%5d - group%2d:%3d - [%-30s] - success:%s"
                        % (total_index, group, index, val, success)
                    )

                # Parallelize sites over all number of browsers set above.

                command_sequence = CommandSequence(
                    site,
                    site_rank=count,
                    reset=True,
                    callback=callback,
                )

                # Start by visiting the page
                command_sequence.append_command(
                    GetCommand(url=site, sleep=3), timeout=60
                )
                # Have a look at custom_command.py to see how to implement your own command
                command_sequence.append_command(LinkCountingCommand())

                # Run commands across the three browsers (simple parallelization)
                manager.execute_command_sequence(command_sequence)

    logger.info("End of the crawl session. crawl_date:%s" % wprgo.crawl_date)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # print("Must provide a crawl date!")
        main("Mar_1_2020")
    else:
        main(sys.argv[1])
