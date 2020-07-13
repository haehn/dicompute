import os,time
import multiprocessing
import pydra

import DICOMPUTE as D

@pydra.mark.task
def convertToNiiAndComputeSift(which):

  # #
  # # 1. download
  # #
  # series = D.GC.download(bucket, which, client=client, outdir='/mnt/data/ct-lymph-nodes/')

  #
  # 2. convert
  #
  dcm_dir = os.path.dirname(which)
  nii_dir = dcm_dir.replace('dicom', 'nii')
  nii_file = os.path.join(os.path.dirname(nii_dir), os.path.basename(dcm_dir))

  nii_path = D.Processing.dcm2nii(which, nii_file)
  
  feature_file = D.Processing.sift3d(nii_path)
  
  return feature_file

#
# connect to bucket and process a bunch of studies
#
outdir = '/mnt/data/ct-lymph-nodes/'

bucket = D.GC.get_bucket('ct-lymph-nodes')

patients = sorted(D.GC.lsdir(bucket, 'dicom/'))

selected_studies = []

#
# Download data (sequential) #TODO
#
for p in patients:

  studies = sorted(D.GC.lsdir(bucket, p))

  for s in studies:
    D.GC.download(bucket, s, outdir=outdir)
    selected_studies.append(os.path.join(outdir,s))


#
# Processing (parallel)
#
N = multiprocessing.cpu_count()
batches = [selected_studies[i:i + N] for i in range(0, len(selected_studies), N)]

print('*'*80)
print('Processing', len(selected_studies), 'studies with', N, 'CPU cores..')
print('*'*80)

for i,b in enumerate(batches):
  # now we pass the first few studies to pydra
  ex1 = convertToNiiAndComputeSift(which=b).split('which')
  # .. and fire it up
  t0 = time.time()
  ex1()
  print('Batch', i+1, '/', len(batches), 'done in', time.time()-t0, 'seconds')
  ex1.result()
