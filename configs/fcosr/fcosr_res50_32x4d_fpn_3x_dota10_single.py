_base_ = [
    '../_base_/datasets/dotav1_fcosr.py', '../_base_/schedules/schedule_3x.py',
    '../_base_/default_runtime.py'
]

num_gpus = 1
image_size = (1024, 1024)

model = dict(
    type='FCOSR',
    backbone=dict(
        type='ResNeXt',
        groups=32,
        base_width=4,
        depth=50,
        num_stages=4,
        out_indices=(1, 2, 3),
        frozen_stages=1,
        style='pytorch',
        init_cfg=dict(
            type='Pretrained', checkpoint='torchvision://resnext50_32x4d')),
    neck=dict(
        type='FPN',
        in_channels=[512, 1024, 2048],
        out_channels=256,
        start_level=0,
        num_outs=5,
        add_extra_convs='on_output',
        relu_before_extra_convs=True),
    bbox_head=dict(
        type='FCOSRHead',
        num_classes=15,
        in_channels=256,
        feat_channels=256,
        stacked_convs=4,
        strides=(8, 16, 32, 64, 128),
        regress_ranges=((-1, 64), (64, 128), (128, 256), (256, 512),
                        (512, 100000000)),
        conv_cfg=dict(type='Conv2d'),
        norm_cfg=dict(type='GN', num_groups=32, requires_grad=True),
        assigner=dict(type='GaussianAssigner',
                      gauss_factor=12.0,
                      inside_ellipsis_thresh=0.23,
                      epsilon=1e-6),
        cls_loss=dict(type='QualityFocalLoss', use_sigmoid=True,
                      beta=2.0, reduction='mean', loss_weight=1.0),
        cls_scores='iou',
        reg_loss=dict(type='ProbiouLoss', mode='l1', loss_weight=1.0),
        reg_weights='iou',
        init_cfg=dict(
            type='Normal',
            layer='Conv2d',
            std=0.01,
            override=dict(
                type='Normal', name='cls_logits_conv', std=0.01, bias_prob=0.01))),
    train_cfg=dict(gamma=2.0, alpha=0.25),
    test_cfg=dict(
        nms_pre=2000,
        min_bbox_size=8,
        score_thr=0.1,
        nms=0.1,
        max_per_img=2000,
        extra_nms=0.85,
        rotations=[]))

optimizer = dict(type='SGD', lr=0.01/num_gpus, momentum=0.9, weight_decay=0.0001)
checkpoint_config = dict(interval=1)
log_config = dict(interval=50, hooks=[dict(type='TextLoggerHook')])
custom_hooks = [dict(type='NumClassCheckHook')]#, dict(type='GradientCumulativeOptimizerHook', cumulative_iters=2)]
dist_params = dict(backend='nccl')
log_level = 'INFO'
work_dir = 'work_dirs/DOTA10/FCOSR-M/FCOSR_rx50_32x4d_fpn_3x_dota10_single'
find_unused_parameters = True
load_from = None
resume_from = None
workflow = [('train', 1)]
gpu_ids = range(0, num_gpus)