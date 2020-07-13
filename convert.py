import os, sys, time

import DICOMPUTE as D

which = sys.argv[1]

dcm_dir = os.path.dirname(which)
nii_dir = dcm_dir.replace('dicom', 'nii')
nii_file = os.path.join(os.path.dirname(nii_dir), os.path.basename(dcm_dir))

nii_path = D.Processing.dcm2nii(which, nii_file)
