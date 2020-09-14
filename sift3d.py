import os, sys, time

import DICOMPUTE as D

nii_path = sys.argv[1]

feature_file = D.Processing.sift3d(nii_path)
