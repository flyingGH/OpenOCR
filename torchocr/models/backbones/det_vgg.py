# coding=utf-8  
# @Time   : 2020/12/23 18:37
# @Auto   : zzf-jeff


import torch
import torch.nn as nn

from ..builder import BACKBONES
from .base import BaseBackbone

# M: pooling 层
# O: endpoint ,设计用来输出指定层feature map
# C: 自定义的层

cfg = {
    'D': [64, 64, 'M', 128, 128, 'O', 'M', 256, 256, 256, 'O',
          'M', 512, 512, 512, 'O', 'M', 512, 512, 512, 'O', 'C', 1024, 1024, 'O'],  # VGG_feature_pyramid
}

# 原作者
def make_layers(cfg_list, in_channel, custom_layer, is_bn=True):
    layers = []
    endpoint_index = []
    for v in cfg_list:
        if v == 'M':
            layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
        elif v == 'O':
            endpoint_index.append(len(layers) - 1)
        elif v == 'C':
            # 用pop保证按照顺序使用custom layer
            layers += custom_layer.pop(0)
        else:
            conv = nn.Conv2d(in_channel, v, kernel_size=3, padding=1)
            if is_bn:
                layers += [conv, nn.BatchNorm2d(v), nn.ReLU(inplace=True)]
            else:
                layers += [conv, nn.ReLU(inplace=True)]
            in_channel = v
    # return nn.Sequential(*layers), endpoint_index
    return layers, endpoint_index


@BACKBONES.register_module()
class PixelVGG(BaseBackbone):
    def __init__(self, in_channels):
        super(PixelVGG, self).__init__()
        # maxpool
        custom_layers = [[nn.MaxPool2d(kernel_size=3, stride=1, padding=1)]]
        self.layers, self.endpoint_index = make_layers(cfg['D'], in_channels, custom_layers)
        self.features = nn.ModuleList(self.layers)

    def forward(self, x):
        out = []
        for idx in range(len(self.features)):
            x = self.features[idx](x)
            if idx in self.endpoint_index:
                out.append(x)
        return out
