if [ $(find zyn_data/Mar_1_2017/crawl.log -mmin +60) ];then
        echo "Something wrong, watchdog not working. Exit."
fi