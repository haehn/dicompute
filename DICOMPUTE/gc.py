import os, time, tempfile

from google.cloud import storage
import google.oauth2.credentials

class GC:


  @staticmethod
  def connect(project='chc-tcia', verbose=True):
    '''
    '''
    t0 = time.time()
    token = os.popen('gcloud auth print-access-token').read().strip('\n') # TODO: better way?
    credentials = google.oauth2.credentials.Credentials(token)

    client = storage.Client(project, credentials=credentials)

    if verbose:
      print('Connected after', time.time()-t0, 'seconds.')

    return client


  @staticmethod
  def get_bucket(needle, user_project='idc-lnq-000', verbose=True):
    '''
    Returns None if bucket is not found.
    '''
    t0 = time.time()

    client = GC.connect(verbose=False)

    bucket = None
    selected_dataset = None

    for d in client.list_buckets():
        if needle in d.name:
            selected_dataset = d.name
            break

    if verbose:
      print('Search completed after', time.time()-t0, 'seconds.')

    if selected_dataset:
      bucket = client.bucket(selected_dataset, user_project=user_project)

    return bucket


  @staticmethod
  def get_bucket_size(bucket, verbose=True):
    '''
    Returns the bucket size in bytes based on all blobs.
    '''
    t0 = time.time()

    size = 0
    for b in bucket.list_blobs():
      size += b.size

    if verbose:
      print('Getting size completed after', time.time()-t0, 'seconds.')

    return size

  @staticmethod
  def lsdir(bucket, prefix, verbose=True):
    '''
    Returns a list of all "directories" in a bucket using a prefix.
    '''
    t0 = time.time()

    client = GC.connect(verbose=False)

    # from https://github.com/GoogleCloudPlatform/google-cloud-python/issues/920
    iterator = client.list_blobs(bucket, prefix=prefix, delimiter='/')
    prefixes = set()

    for page in iterator.pages:
      # print (page, page.prefixes)
      prefixes.update(page.prefixes)
    
    if verbose:
      print('Listing directory completed after', time.time()-t0, 'seconds.')

    return list(prefixes)

  @staticmethod
  def download(bucket, dir, outdir=None, verbose=True):
    '''
    Downloads all files from a "directory".

    Skips previously downloaded files based on filename and size.
    '''
    t0 = time.time()

    client = GC.connect(verbose=True)
    # return client

    if not outdir:
      outdir = tempfile.mkdtemp()

    downloaded_files = []

    for blob in client.list_blobs(bucket, prefix=dir):

      outfile = os.path.join(outdir, blob.name)

      if os.path.exists(outfile):
        if os.path.getsize(outfile) == blob.size:
          # if verbose:
            # print('Skipping', blob.name)
          downloaded_files.append(outfile)
          continue

      os.makedirs(os.path.dirname(outfile), exist_ok=True)

      blob.download_to_filename(outfile)
      downloaded_files.append(outfile)

    if verbose:
      print('Download completed after', time.time()-t0, 'seconds.')

    return downloaded_files
