import logging
from .constants import *


def resolve_data_config(args, default_cfg={}, model=None, verbose=True):
    new_config = {}
    default_cfg = default_cfg
    if not default_cfg and model is not None and hasattr(model, 'default_cfg'):
        default_cfg = model.default_cfg

    # Resolve input/image size
    in_chans = 3
    if 'chans' in args and args['chans'] is not None:
        in_chans = args['chans']

    input_size = (in_chans, 224, 224)
    if 'input_size_v2' in args and args['input_size_v2'] is not None:
        assert isinstance(args['input_size_v2'], str)
        input_size = tuple([int(i) for i in args['input_size_v2'].split(',')])
        assert len(input_size) == 3
        in_chans = input_size[0]
    elif 'input_size' in args and args['input_size'] is not None:
        assert isinstance(args['input_size'], (tuple, list))
        assert len(args['input_size']) == 3
        input_size = tuple(args['input_size'])
        in_chans = input_size[0]  # input_size overrides in_chans
    elif 'img_size' in args and args['img_size'] is not None:
        assert isinstance(args['img_size'], int)
        input_size = (in_chans, args['img_size'], args['img_size'])
    elif 'input_size' in default_cfg:
        input_size = default_cfg['input_size']
    new_config['input_size'] = input_size

    # resolve interpolation method
    new_config['interpolation'] = 'bicubic'
    if 'interpolation' in args and args['interpolation']:
        new_config['interpolation'] = args['interpolation']
    elif 'interpolation' in default_cfg:
        new_config['interpolation'] = default_cfg['interpolation']

    # resolve dataset + model mean for normalization
    new_config['mean'] = IMAGENET_DEFAULT_MEAN
    if 'model' in args:
        new_config['mean'] = get_mean_by_model(args['model'])
    if 'mean' in args and args['mean'] is not None:
        mean = tuple(args['mean'])
        if len(mean) == 1:
            mean = tuple(list(mean) * in_chans)
        else:
            assert len(mean) == in_chans
        new_config['mean'] = mean
    elif 'mean' in default_cfg:
        new_config['mean'] = default_cfg['mean']

    # resolve dataset + model std deviation for normalization
    new_config['std'] = IMAGENET_DEFAULT_STD
    if 'model' in args:
        new_config['std'] = get_std_by_model(args['model'])
    if 'std' in args and args['std'] is not None:
        std = tuple(args['std'])
        if len(std) == 1:
            std = tuple(list(std) * in_chans)
        else:
            assert len(std) == in_chans
        new_config['std'] = std
    elif 'std' in default_cfg:
        new_config['std'] = default_cfg['std']

    # resolve default crop percentage
    new_config['crop_pct'] = DEFAULT_CROP_PCT
    if 'crop_pct' in args and args['crop_pct'] is not None:
        new_config['crop_pct'] = args['crop_pct']
    elif 'crop_pct' in default_cfg:
        new_config['crop_pct'] = default_cfg['crop_pct']

    if verbose:
        logging.info('Data processing configuration for current model + dataset:')
        for n, v in new_config.items():
            logging.info('\t%s: %s' % (n, str(v)))

    return new_config


def get_mean_by_model(model_name):
    model_name = model_name.lower()
    if 'dpn' in model_name:
        return IMAGENET_DPN_STD
    elif 'ception' in model_name or ('nasnet' in model_name and 'mnasnet' not in model_name):
        return IMAGENET_INCEPTION_MEAN
    else:
        return IMAGENET_DEFAULT_MEAN


def get_std_by_model(model_name):
    model_name = model_name.lower()
    if 'dpn' in model_name:
        return IMAGENET_DEFAULT_STD
    elif 'ception' in model_name or ('nasnet' in model_name and 'mnasnet' not in model_name):
        return IMAGENET_INCEPTION_STD
    else:
        return IMAGENET_DEFAULT_STD
