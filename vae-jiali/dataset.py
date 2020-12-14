import sys
sys.path.append('..')
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

import DICOMPUTE as D 

def force_reproducibility(seed):
    r"""Set random seed for numpy and torch"""
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def train_test_split(valid_ratio=0.1, test_ratio=0.1, lesion_type=None, seed=0, 
                     dl_info='/home/haehn/Projects/dicompute/DL_info.csv'):
    r"""Split the data into train/valid/test"""
    force_reproducibility(seed)
    
    data = pd.read_csv(dl_info)
    
    # Skip non-accessible images
    skip = ['001064_01_01_200.png','001096_04_02_170.png', '002084_01_02_259.png']
    data = data[~data.File_name.isin(skip)]
    
    if lesion_type is not None:
        data = data[data.Coarse_lesion_type==lesion_type]
    valid_size = int(valid_ratio * data.shape[0])
    test_size = int(test_ratio * data.shape[0])
    
    test_mask = np.random.rand(data.shape[0]) < test_ratio
    test_data = data[test_mask]
    train_data = data[~test_mask]
    train_data = train_data.reset_index(drop=True)
    valid_mask = np.random.rand(train_data.shape[0]) < valid_ratio
    valid_data = train_data[valid_mask]
    train_data = train_data[~valid_mask]
    
    return train_data, valid_data, test_data
    
    
class LesionDataset(Dataset):
    r"""Dataset of Lesion images & bounding boxes, need pandas.DataFrame about the data"""
    
    def __init__(self, dl_info_dataframe, root='/home/haehn/Data/Images_png'):
        self.root = root
        self.data_df = dl_info_dataframe
        
    def __len__(self):
        return self.data_df.shape[0]

    def __getitem__(self, idx):
        imgfile = self.data_df.iloc[idx]['File_name']
        # add filter for type 5 (lung)
        bbox = np.array([float(v) for v in self.data_df.iloc[idx]['Bounding_boxes'].split(',')])
        im_small, box, scale = D.DeepLesion.get_lesion(imgfile, bbox, datadir=self.root, show=False)
        img_3d = np.expand_dims(im_small, axis=0)
        return torch.from_numpy(img_3d).float(), box, scale