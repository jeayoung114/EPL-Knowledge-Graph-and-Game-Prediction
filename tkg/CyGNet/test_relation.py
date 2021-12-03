from utils import *
from torch import optim
import torch
from config import args
from link_prediction import link_prediction
from evolution import calc_raw_mrr, calc_filtered_test_mrr
import warnings
warnings.filterwarnings(action='ignore')

torch.set_num_threads(2)

use_cuda = args.gpu >= 0 and torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")

if args.dataset == 'ICEWS14':
	train_data, train_times = load_quadruples('./data/{}'.format(args.dataset), 'train.txt')
	test_data, test_times = load_quadruples('./data/{}'.format(args.dataset), 'test.txt')
	dev_data, dev_times = load_quadruples('./data/{}'.format(args.dataset), 'test.txt')
else:
	train_data, train_times = load_quadruples('./data/{}'.format(args.dataset), 'train.txt')
	test_data, test_times = load_quadruples('./data/{}'.format(args.dataset), 'test.txt')
	dev_data, dev_times = load_quadruples('./data/{}'.format(args.dataset), 'valid.txt')

all_times = np.concatenate([train_times, dev_times, test_times])

num_e, num_r = get_total_number('./data/{}'.format(args.dataset), 'stat.txt')
num_times = int(max(all_times) / args.time_stamp) + 1
print('num_times', num_times)

model = link_prediction(num_e, args.hidden_dim, num_r, num_times, use_cuda)
model.to(device)

all_tail_seq_obj = sp.csr_matrix(([], ([], [])), shape=(num_e * num_r, num_e))
all_tail_seq_sub = sp.csr_matrix(([], ([], [])), shape=(num_e * num_r, num_e))
for i in range(len(train_times)):
    tim_tail_seq_obj = sp.load_npz(
        './data/{}/copy_seq/train_h_r_copy_seq_{}.npz'.format(args.dataset, train_times[i]))
    tim_tail_seq_sub = sp.load_npz(
        './data/{}/copy_seq_sub/train_h_r_copy_seq_{}.npz'.format(args.dataset, train_times[i]))
    all_tail_seq_obj = all_tail_seq_obj + tim_tail_seq_obj
    all_tail_seq_sub = all_tail_seq_sub + tim_tail_seq_sub

model_state_file_obj = './results/bestmodel/{}/model_state.pth'.format(args.dataset)
model_state_file_sub = './results/bestmodel/{}_sub/model_state.pth'.format(args.dataset)
batch_size = args.batch_size

print("\nstart relation testing:")
# use best model checkpoint
checkpoint_obj = torch.load(model_state_file_obj)
# if use_cuda:
# model.cpu()  # test on CPU
model.train()
model.load_state_dict(checkpoint_obj['state_dict'])
print("Using best epoch: {}".format(checkpoint_obj['epoch']))

obj_test_mrr, obj_test_hits1, obj_test_hits3, obj_test_hits5 = 0, 0, 0, 0
n_batch = (test_data.shape[0] + batch_size - 1) // batch_size

for idx in range(n_batch):
    batch_start = idx * batch_size
    batch_end = min(test_data.shape[0], (idx + 1) * batch_size)
    test_batch_data = test_data[batch_start: batch_end]

    test_label = torch.LongTensor(test_batch_data[:, 2])
    seq_idx = test_batch_data[:, 0] * num_r + test_batch_data[:, 1]

    tail_seq = torch.Tensor(all_tail_seq_obj[seq_idx].todense())
    one_hot_tail_seq_obj = tail_seq.masked_fill(tail_seq != 0, 1)

    if use_cuda:
        test_label, one_hot_tail_seq_obj = test_label.to(device), one_hot_tail_seq_obj.to(device)
    test_score = model(test_batch_data, one_hot_tail_seq_obj, entity='object')

    if args.raw:
        tim_mrr, tim_hits1, tim_hits3, tim_hits5 = calc_raw_mrr(test_score, test_label, hits=[1, 3, 5])
    else:
        tim_mrr, tim_hits1, tim_hits3, tim_hits5 = calc_filtered_test_mrr(num_e, test_score,
                                                                           torch.LongTensor(
                                                                               train_data),
                                                                           torch.LongTensor(
                                                                               dev_data),
                                                                           torch.LongTensor(
                                                                               test_data),
                                                                           torch.LongTensor(
                                                                               test_batch_data),
                                                                           entity='object',
                                                                           hits=[1, 3, 5])

    obj_test_mrr += tim_mrr * len(test_batch_data)
    obj_test_hits1 += tim_hits1 * len(test_batch_data)
    obj_test_hits3 += tim_hits3 * len(test_batch_data)
    obj_test_hits5 += tim_hits5 * len(test_batch_data)

obj_test_mrr = obj_test_mrr / test_data.shape[0]
obj_test_hits1 = obj_test_hits1 / test_data.shape[0]
obj_test_hits3 = obj_test_hits3 / test_data.shape[0]
obj_test_hits5 = obj_test_hits5 / test_data.shape[0]

print("test object-- Epoch {:04d} | Best MRR {:.4f} | Hits@1 {:.4f} | Hits@3 {:.4f} | Hits@5 {:.4f}".
      format(checkpoint_obj['epoch'], obj_test_mrr, obj_test_hits1, obj_test_hits3, obj_test_hits5))
