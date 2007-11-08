#!/usr/bin/python

import hotshot
prof = hotshot.Profile("hotshot_edi_stats")

from pc	import run
prof.runcall(run)
prof.close()


