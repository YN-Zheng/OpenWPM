# watch dog for replay_crawl.py
crawl_date=$1
# cd "${0%/*}" # cd folder of this script
while true
do
    DONE=$(tail crawl.log | grep "End of the crawl session. crawl_date:"$crawl_date)
    DONE2=$(tail crawl.log | grep "This crawl session is completed. crawl_date:"$crawl_date)
    if [[ "$DONE" || "$DONE2" ]]
    then
        echo "The crawl has end. Stop watchdog for it."
        exit
    fi
    now=$(date)
	if [ $(python zyn_watchdog.py) -gt 300 ];then
		printf "%s :: Run zyn_replay_crawl.py \n" "$now"
        pkill python
        pkill wpr
		python zyn_replay_crawl.py $crawl_date &
    else
        printf "%s :: Program running normally... \n" "$now"
	fi
	sleep 60
done