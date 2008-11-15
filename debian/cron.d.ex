#
# Regular cron jobs for the pc package
#
0 4	* * *	root	[ -x /usr/bin/pc_maintenance ] && /usr/bin/pc_maintenance
