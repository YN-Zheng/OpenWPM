# watchdog for replay_crawl.py

crawl_date=$1
crawl_log="zyn_data/"$crawl_date"/crawl.log"
# cd folder of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $DIR 
source ~/miniconda3/etc/profile.d/conda.sh
conda activate openwpm
# if crawl file does not exist, start crawl
if [ ! -f crawl_log ]; then
    echo $crawl_log" does not exists."
    python zyn_replay_crawl.py $crawl_date &
fi

# check crawl.log file utill the crawl has finished
while true
do
    DONE=$(tail $crawl_log | grep "End of the crawl session. crawl_date:"$crawl_date)
    DONE2=$(tail $crawl_log | grep "This crawl session is completed. crawl_date:"$crawl_date)
    if [[ "$DONE" || "$DONE2" ]]
    then
        echo "watchdog.sh: The crawl has end. Stop watchdog for it."
        exit
    fi
    # if the log file hasn't been updated for 5 min, kill and re-run it.
	if [ $(find $crawl_log -mmin +5) ];then
		echo "watchdog.sh: Run zyn_replay_crawl.py \n" 
        pkill python
        pkill wpr
		python zyn_replay_crawl.py $crawl_date &
    elif [ $(find $crawl_log -mmin +60) ];then
        echo "watchdog.sh: Something wrong, watchdog not working. Exit."
        pkill python
        pkill wpr
        exit
    else
        echo "watchdog.sh: Program running normally... \n" 
	fi
	sleep 180
done