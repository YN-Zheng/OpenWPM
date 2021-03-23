from pathlib import Path
import utils
from custom_command import LinkCountingCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager

har_path = "/home/yongnian/HttpArchive/Mar_1_2020"
wprgo_path = "/home/yongnian/Programs/catapult/web_page_replay_go"
wprgo = utils.Wprgo(wprgo_path, har_path)

# The list of sites that we wish to crawl
NUM_BROWSERS = 10


# Loads the default ManagerParams
# and NUM_BROWSERS copies of the default BrowserParams

manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
browser_params = [BrowserParams(display_mode="headless") for _ in range(NUM_BROWSERS)]

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
    # browser_params[i].prefs = utils.get_wprgo_prefs()
# Update TaskManager configuration (use this for crawl-wide settings)
manager_params.data_directory = Path("./datadir/")
manager_params.log_directory = Path("./datadir/")

# memory_watchdog and process_watchdog are useful for large scale cloud crawls.
# Please refer to docs/Configuration.md#platform-configuration-options for more information
manager_params.memory_watchdog = True
manager_params.process_watchdog = True


for n in range(wprgo.total_number):
    sites = wprgo.get_hostnames(n)
    with TaskManager(
        manager_params,
        browser_params,
        SQLiteStorageProvider(Path("./datadir/replay-crawl-data.sqlite")),
        None,
    ) as manager:
        # Visits the sites
        for index, site in enumerate(sites):

            def callback(success: bool, val: str = site) -> None:
                print(
                    f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
                )

            # Parallelize sites over all number of browsers set above.
            command_sequence = CommandSequence(
                site,
                site_rank=index,
                reset=True,
                callback=callback,
            )

            # Start by visiting the page
            command_sequence.append_command(GetCommand(url=site, sleep=3), timeout=60)
            # Have a look at custom_command.py to see how to implement your own command
            command_sequence.append_command(LinkCountingCommand())

            # Run commands across the three browsers (simple parallelization)
            manager.execute_command_sequence(command_sequence)
