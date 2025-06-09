from __future__ import print_function

"""
A simple script to compute error metrics on images
and generate false color heatmap visualizations.
"""

import argparse
import pyexr
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from mpl_toolkits.axes_grid1 import make_axes_locatable
#from skimage.measure import compare_ssim, compare_psnr
COLOR_MAP = 'viridis'

NP_INT_TYPES = [np.int8, np.int16, np.int32, np.int64,
                np.uint8, np.uint16, np.uint32, np.uint64]


def compute_metric(ref, test, metric, eps=1e-2):
    """Compute desired metric."""

    diff = np.array(ref - test)
    eps = 1e-2

    if (metric == 'l1'):      # Absolute error
        error = np.abs(diff)
    elif (metric == 'l2'):    # Squared error
        error = diff * diff
    elif (metric == 'mrse'):  # Relative squared error
        error = diff * diff / (ref * ref + eps)
    elif (metric == 'relMSE'):  # Relative squared error
        error = diff * diff / (ref * ref + eps)
    elif (metric == 'mape'):  # Relative absolute error
        error = np.abs(diff) / (ref + eps)
    elif (metric == 'smape'):  # Symmetric absolute error
        error = 2 * np.abs(diff) / (ref + test + eps)
    # elif (metric == 'dssim'):
    #     # Tonemap the images before SSIM
    #     ref_tonemap = np.array(pyexr.tonemap(ref) * 255, dtype=np.uint8)
    #     test_tonemap = np.array(pyexr.tonemap(test) * 255, dtype=np.uint8)
    #     error = 1.0 - compare_ssim(ref_tonemap,
    #                                test_tonemap,
    #                                multichannel=True,
    #                                full=True)[1]
    else:
        raise ValueError('Invalid metric')

    return error


def falsecolor(error, clip, eps=1e-2):
    """Compute false color heatmap."""

    cmap = plt.get_cmap(COLOR_MAP)
    mean = np.mean(error, axis=2)
    min_val, max_val = clip
    val = np.clip((mean - min_val) / (max_val - min_val + eps), 0, 1)
    return cmap(val)


def falsecolor_np(ref, test, eps=1e-2):
    """Compute negative / positive relative error."""
    diff = 2 * np.array(test - ref) / (ref + test + eps)
    diff = np.mean(diff, axis=2)
    diff = np.clip(diff, -1, 1)

    img = np.zeros((diff.shape[0], diff.shape[1], 3))
    img[diff > 0, 0] = diff[diff > 0]
    img[diff < 0, 1] = -diff[diff < 0]
    return img


def plot(img, clip, fname):
    """Plot false color heatmap with colorbar legend."""

    plt.rcParams.update({'font.size': 18})
    plt.rcParams.update({'font.family': 'linux biolinum'})

    err_min, err_max = clip
    dpi_scale = 60.0
    figsize = img.shape[0] / dpi_scale, img.shape[1] / dpi_scale
    fig = plt.figure(frameon=False, figsize=figsize)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.xaxis.set_major_locator(plt.NullLocator())
    ax.yaxis.set_major_locator(plt.NullLocator())

    plt.imshow(img, cmap=COLOR_MAP, interpolation='nearest')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='3%', pad=0.1)
    cb = plt.colorbar(cax=cax)
    plt.clim(err_min, err_max)

    fig.savefig(fname, bbox_inches='tight', pad_inches=0.1)


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Compute metric between two OpenEXR images.')
    parser.add_argument('-r',   '--ref',
                        help='reference image filename', type=str, required=True)
    parser.add_argument('-t',   '--test',
                        help='test image filename', type=str, required=True)
    parser.add_argument('-m',   '--metric', help='difference metric',
                        choices=['l1', 'l2', 'rse', 'mape', 'smape', 'dssim'], type=str)
    parser.add_argument('-eps', '--epsilon',
                        help='epsilon value', type=float, default=1e-2)
    parser.add_argument('-c',   '--clip', 
                        help='clipping values for min/max', nargs=2, type=float, default=[0, 1])
    parser.add_argument('-fc',  '--falsecolor',
                        help='false color heatmap output file', type=str)
    parser.add_argument('-cb',  '--colorbar',
                        help='display colorbar on false error heatmap', action='store_true')
    parser.add_argument('-p',   '--plain',
                        help='output error as plain text', action='store_true')
    parser.add_argument('-np', '--negpos', type=str,
                        help='positive negative smape output image')

    args = parser.parse_args()

    # Check image formats
    if not args.ref.lower().endswith('.exr') and not args.test.lower().endswith('.exr'):
        raise ValueError('Images must be in OpenEXR format.')

    # Load images and convert to NumPy array
    try:
        ref_fp = pyexr.open(args.ref)
        test_fp = pyexr.open(args.test)
    except FileNotFoundError:
        print('Could not open files')
    ref = np.array(ref_fp.get())
    test = np.array(test_fp.get())

    # Compute metric
    if args.metric:
        err_img = compute_metric(ref, test, args.metric, args.epsilon)
        err_mean = np.mean(err_img)
        if args.plain:
            print('{:.6f}'.format(err_mean))
        else:
            err_min, err_max, err_var = np.amin(
                err_img), np.amax(err_img), np.var(err_img)
            print('{} = {:.4f} (Min = {:.4f}, Max = {:.4f}, Var = {:.4f})'.format(
                args.metric.upper(), err_mean, err_min, err_max, err_var))

        # Compute false color heatmap
        if (args.falsecolor):
            if not args.falsecolor.lower().endswith('.png'):
                raise ValueError(
                    'False color output file must be in PNG format.')
            if args.clip != [0, 1]:
                print('Clipping values in range: [{:.2f}, {:.2f}]'.format(
                    args.clip[0], args.clip[1]))
            fc = falsecolor(err_img, args.clip, args.epsilon)
            plt.imsave(args.falsecolor, fc)
            print('False color heatmap written to: {}'.format(args.falsecolor))
            if args.colorbar:
                fname = args.falsecolor.replace('.png', '.pdf')
                plot(fc, args.clip, fname)
                print('False color heatmap (with colorbar) written to: {}'.format(fname))

    # Compute negative positie SMAPE heatmap
    if (args.negpos):
        if not args.negpos.lower().endswith('.png'):
            raise ValueError('False color output file must be in PNG format.')
        fc = falsecolor_np(ref, test, args.epsilon)
        plt.imsave(args.negpos, fc)
        print('False N/P color heatmap written to: {}'.format(args.negpos))
