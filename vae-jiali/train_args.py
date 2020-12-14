import argparse

def train_args():
    parser = argparse.ArgumentParser()

    # model
    parser.add_argument('--in_dim', type=int, default=100, 
                        help='frequency of showing training results on screen')
    parser.add_argument('--out_dim', type=int, default=100, 
                        help='frequency of showing training results on console')
    parser.add_argument('--hidden_dim', type=int, default=1000, 
                        help='frequency of saving the latest results')
    parser.add_argument('--num_rel', type=int, default=5, 
                        help='frequency of saving checkpoints at the end of epochs')

    # data
    parser.add_argument('--data_dir', type=str, default='input',
                        help='input node vector')
    parser.add_argument('--node_vec', type=str, default='data/node_vector',
                        help='input node vector') 
    parser.add_argument('--edge_attr', type=str, default='data/edge_attribute',
                        help='input edge attribute')
    parser.add_argument('--random_seed', type=int, default=0,
                        help='for re-produce purpose (split, etc.)')
    
    # data loader
    parser.add_argument('--batch_size', type=int, default=128, help='batch size')
    parser.add_argument('--walk_length=, =', type=int, default=16,
                        help='for re-produce purpose (split, etc.)')
    parser.add_argument('--num_steps', type=int, default=32,
                        help='for re-produce purpose (split, etc.)')
    parser.add_argument('--neg_sample_size', type=int, default=64, help='negative sample size')       

    # training
    parser.add_argument('--lr', type=float, default=0.001, help='initial learning rate')
    parser.add_argument('--weight_decay', type=float, default=0.0005, help='initial learning rate')
    parser.add_argument('--optimizer', type=str, default='Adam', help='optimizer')
    parser.add_argument('--epoch', type=int, default=500, 
                        help='continue training: load the latest model')
    parser.add_argument('--niter', type=int, default=10000, 
                        help='load the pretrained model from the specified location')
    parser.add_argument('--init_checkpoint', type=str, default='checkpoint', 
                        help='path to initial checkpoint')
    parser.add_argument('--save_freq', type=int, default=50, 
                        help='# of iter to save model')        
    parser.add_argument('--valid_freq', type=int, default=50, 
                        help='# of iter to do validation')    
    parser.add_argument('--log_freq', type=int, default=50, help='# of iter to log metric')

    return parser.parse_args()
