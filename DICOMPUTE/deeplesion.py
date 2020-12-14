import load_ct_img
import pandas
import numpy as np
import matplotlib.pyplot as plt

class DeepLesion:

  @staticmethod
  def show(WHICH, datadir='/mnt/data/deeplesion/Images_png/'):
    '''
    '''
    data = pandas.read_csv('DL_info.csv')
    imgfile = data.iloc[WHICH]['File_name']
    bbox = np.array([float(v) for v in data.iloc[WHICH]['Bounding_boxes'].split(',')])
    im_small, box, scale = DeepLesion.get_lesion(imgfile, bbox, datadir=datadir)

    print(box, scale)
    plt.figure()
    plt.imshow(im_small)


  @staticmethod
  def showType(WHICH, datadir='/mnt/data/deeplesion/Images_png/', show=True):
    '''
    '''
    data = pandas.read_csv('DL_info.csv')

    relevant = data['Coarse_lesion_type']==WHICH
    data = data[relevant]

    row = data.sample()
    imgfile = row.iloc[0]['File_name']
    bbox = np.array([float(v) for v in row.iloc[0]['Bounding_boxes'].split(',')])
    im_small, box, scale = DeepLesion.get_lesion(imgfile, bbox, datadir=datadir, show=show)

    if show:
      plt.imshow(im_small)
    else:
      return im_small, box, scale

  @staticmethod
  def get_lesion_image(imgfile, bbox):
    im_small, box, scale = DeepLesion.get_lesion(imgfile, bbox, show=False)
    return im_small



  @staticmethod
  def get_lesion(filename, bbox, do_clip=False, num_slice=1, datadir='/mnt/data/deeplesion/Images_png/', show=True):

    png = filename.split('_')[-1]
    folder = filename.replace('_'+png, '')

    slice_idx = 1337
    spacing = 1
    slice_intv = -1
    # do_clip = 
    # num_slice = 1
    do_windowing = True

    img, scale, c = load_ct_img.load_prep_img(datadir+'/'+folder+'/'+png,
                      slice_idx, # never used!
                      spacing,
                      slice_intv,
                      do_clip,
                      num_slice,
                      do_windowing
                      )
    # print(bbox)
    if show:
      lw = 1
      img[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[0])+lw] = 255
      img[int(bbox[1]):int(bbox[3]),int(bbox[2]):int(bbox[2])+lw] = 255

      img[int(bbox[1]):int(bbox[1])+lw,int(bbox[0]):int(bbox[2])] = 255
      img[int(bbox[3]):int(bbox[3])+lw,int(bbox[0]):int(bbox[2])] = 255

    if show:
      plt.figure()
      plt.imshow(img)

    im_small, box, scale = load_ct_img.get_patch(img, bbox)


    return im_small, box, scale

