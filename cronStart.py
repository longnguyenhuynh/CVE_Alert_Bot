from crontab import CronTab
 
cron = CronTab(user='')
job = cron.new(command='python3 ./main.py')
job.every(1).hours()

cron.write()