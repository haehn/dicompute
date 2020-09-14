import os,time
import multiprocessing
import pydra

import DICOMPUTE as D

@pydra.mark.task
def get_bucket(bucketname):

  bucket = D.GC.get_bucket('ct-lymph-nodes')

  return bucket


@pydra.mark.task
def get_studies(bucket, outdir):

  patients = sorted(D.GC.lsdir(bucket, 'dicom/'))

  selected_studies = []

  for p in patients:

    studies = sorted(D.GC.lsdir(bucket, p))

    for s in studies:
      selected_studies.append(os.path.join(outdir,s))

  return selected_studies



outdir = '/mnt/data/ct-lymph-nodes/'




workflow = pydra.Workflow(name='gcloud_sift3d', 
                          input_spec=["bucket", "outdir"],
                          bucket = bucket,
                          outdir = outdir)

#
# Download
#
cmd = 'python download.py'
args = study
downloader = pydra.ShellCommandTask(name="downloader", 
                                    executable=cmd, args=args)

workflow.add(downloader)

#
# 
#

