# watch dog for process wpr. Why needed? OOM may occur and kill process
crawl_date=$1
# cd "${0%/*}" # cd folder of this script
while true
do
    DONE=$(tail crawl.log | grep "End of the crawl session. crawl_date:"$crawl_date)
	if [ "$DONE" ]
    then
        echo "The crawl has end. Stop watchdog for it."
        exit
    fi
	if [ $(python zyn_watchdog.py) -gt 100 ];then
		now=$(date)
		printf "%s :: Run zyn_replay_crawl.py \n" "$now"
        pkill python
        pkill wpr
		python zyn_replay_crawl.py $crawl_date
	fi
	sleep 10
done