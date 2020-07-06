import os, time

class Processing:

  @staticmethod
  def dcm2nii(input, output, verbose=True, dcm2niix_executable='dcm2niix'):
    '''
    Uses dcm2niix to convert a DICOM series to .NII file.
    '''
    t0 = time.time()

    dcm_dir = input
    nii_dir = os.path.dirname(output)
    nii_file = os.path.basename(output).replace('.nii','') # strip .nii

    os.makedirs(nii_dir, exist_ok=True)

    cmd = dcm2niix_executable + ' -f ' + nii_file + ' -o '+ nii_dir + ' ' + dcm_dir + '/*.dcm'
    nii_path = os.path.join(nii_dir,nii_file+'.nii')
    if not os.path.exists(nii_path):
        stdout = os.popen(cmd).read()

    if verbose:
      print('NII Conversion completed after ', time.time()-t0, 'seconds.')

    return nii_path


  @staticmethod
  def sift3d(nii_path, verbose=True, featExtract_executable='/home/d/Projects/dicompute/featExtract1.6/featExtract.ubu'):
    '''
    Calculate 3D Sift features for a nii file.
    '''
    t0 = time.time()

    feature_file = nii_path.replace('.nii', '.sift')
    cmd = featExtract_executable + ' ' + nii_path + ' ' + feature_file
    if not os.path.exists(feature_file):
      stdout = os.popen(cmd).read()

    if verbose:
      print('SIFT Calculation completed after', time.time()-t0, 'seconds.')

    return feature_file
