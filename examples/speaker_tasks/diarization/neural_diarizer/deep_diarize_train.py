# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytorch_lightning as pl
import torch
from omegaconf import OmegaConf
from torch import set_float32_matmul_precision

from nemo.collections.asr.models.deep_diarize_model import DeepDiarizeModel
from nemo.core.config import hydra_runner
from nemo.utils import logging
from nemo.utils.exp_manager import exp_manager


"""
Example training session (single GPU training)

python ./deep_diarize_train.py --config-path='../conf/neural_diarizer' --config-name='deep_diarize.yaml' \
    trainer.devices=1 \
    model.train_ds.manifest_filepath="/ws/manifests/fisher_mixed/fisher_train_manifest.json" \
    model.validation_ds.manifest_filepath="/ws/manifests/fisher_mixed/fisher_dev_manifest.json" \
    exp_manager.name='sample_train' \
    exp_manager.exp_dir='./deep_diarize_exp'
    
    
python ./deep_diarize_train.py --config-path='../conf/neural_diarizer' --config-name='deep_diarize.yaml' \
    trainer.devices=1 \
    model.train_ds.manifest_filepath="/data/fisher_tarred/audio__OP_0..18_CL_.tar" \
    model.validation_ds.manifest_filepath="/ws/manifests/fisher_mixed/fisher_10_train_manifest.json" \
    exp_manager.name='sample_train' \
    exp_manager.exp_dir='./deep_diarize_exp' \
    exp_manager.wandb_logger_kwargs.name='new_exp' \
    exp_manager.wandb_logger_kwargs.project='diar-transformer-xl' \
    exp_manager.create_wandb_logger=True
"""


@hydra_runner(config_path="../conf/neural_diarizer", config_name="deep_diarize.yaml")
def main(cfg):
    set_float32_matmul_precision('medium')
    logging.info(f'Hydra config: {OmegaConf.to_yaml(cfg)}')
    trainer = pl.Trainer(**cfg.trainer)
    exp_manager(trainer, cfg.get("exp_manager", None))
    deep_diarize = DeepDiarizeModel(cfg=cfg.model, trainer=trainer)

    if cfg.model.pretrained_weights:
        print("Loading pre-trained model weights")
        weights = torch.load(cfg.model.pretrained_weights, map_location=torch.device('cpu'))['state_dict']
        deep_diarize.load_state_dict(weights)

    trainer.fit(deep_diarize)


if __name__ == '__main__':
    main()