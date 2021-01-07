# coding=utf-8  
# @Time   : 2021/1/6 10:45
# @Auto   : zzf-jeff

import torch
from tqdm import tqdm
import time


def eval(model, valid_dataloader, post_process_class, metric_class):
    model.eval()
    with torch.no_grad():
        total_frame = 0.0
        total_time = 0.0
        pbar = tqdm(total=len(valid_dataloader), desc='eval model:')
        for idx, data_batch in enumerate(valid_dataloader):
            if idx >= len(valid_dataloader):
                break
            imgs = data_batch['image'].to(model.device)
            start = time.time()
            preds = model(imgs)
            # data_batch = [item.numpy() for item in data_batch]
            # Obtain usable results from post-processing methods
            post_result = post_process_class(preds, data_batch['label'])
            total_time += time.time() - start
            # Evaluate the results of the current batch
            metric_class(post_result)
            pbar.update(1)
            total_frame += len(imgs)

        metirc = metric_class.get_metric()
        pbar.close()
        model.train()
        metirc['fps'] = total_frame / total_time
        return metirc
