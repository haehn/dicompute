import os, sys, time

import DICOMPUTE as D

study = sys.argv[1]
outdir = sys.argv[2]

D.GC.download(study, outdir=outdir)

