from __future__ import print_function

"""
A script to analyze performance by comparing images 
using different metrics. To be used in conjuction 
with Jeri in-browser visualization tool.
"""

import glob
import os
import sys
import argparse
import pyexr
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import json
import csv
import math
import fnmatch
import numpy as np
from metric import compute_metric, falsecolor, falsecolor_np

NP_INT_TYPES = [np.int8, np.int16, np.int32, np.int64,
                np.uint8, np.uint16, np.uint32, np.uint64]


def generate_thumbnail(path_dir, ref):
    """Generate thumbnail image for index."""

    thumb_w, thumb_h = 640, 360
    img = Image.fromarray((pyexr.tonemap(ref) * 255).astype(np.uint8))
    w, h = img.size
    resized_h = [w, h].index(max([w, h]))
    ratio = thumb_h / h if resized_h else thumb_w / w

    w, h = int(w * ratio), int(h * ratio)
    thumb = img.resize((w, h), resample=Image.BICUBIC)

    bg = Image.new('RGBA', (thumb_w, thumb_h), (0, 0, 0, 255))
    if resized_h:
        bg.paste(thumb, (int((thumb_w - w) / 2), 0))
    else:
        bg.paste(thumb, (0, int((thumb_h - h) / 2)))

    bg.save(os.path.join(path_dir, 'thumb.png'))


def write_data(path_dir, data):
    """Update JS dictionary files."""

    with open(os.path.join(path_dir, 'data.json'), 'w') as fp:
        json.dump(data, fp, indent=4)

    data_js = 'const data =\n' + json.dumps(data, indent=4)
    with open(os.path.join(path_dir, 'data.js'), 'w') as fp:
        fp.write(data_js)


def hdr_to_ldr(path_dir, img):
    """HDR to LDR conversion for web display."""

    # Image already in ldr
    if (img['data'].dtype in NP_INT_TYPES):
        ldr = Image.fromarray(img['data'].astype(np.uint8))
    else:
        ldr = Image.fromarray(
            (pyexr.tonemap(img['data']) * 255).astype(np.uint8))
    ldr_fname = '{}.jpg'.format(img['name'])
    ldr_fname = os.path.basename(ldr_fname)
    ldr_fname = ldr_fname.replace(" ", "_")
    ldr_fname = ldr_fname.replace("+", "_")
    ldr_path = os.path.join(path_dir, ldr_fname)
    ldr.save(ldr_path,quality=95)
    ldr_entry = {'title': img['name'], 'version': '-', 'image': ldr_fname}
    return ldr_entry


def parse_stats(test_dirs, test_names):
    """Parse Mitsuba statistics file.
    Ugly but it does the job; could use regex.
    TODO: Incorporate this into data dictionary.
    """

    stat_dicts = {}
    for t, test_dir in enumerate(test_dirs):
        stat_file = '{}_stats.txt'.format('_'.join(test_dir.split('_')[:-1]))
        with open(os.path.join(test_dir, stat_file), 'r') as fp:
            stat_txt = fp.read()

        stat_dict = {}
        stats = stat_txt.split('*')[2:]
        stats = [s.replace('\n', '').split(' - ') for s in stats]
        for i, stat in enumerate(stats):
            stats[i] = [s.strip().replace('--', '') for s in stat]
        stats[0][0] = 'Algorithm'
        for stat in stats:
            entry = {}
            for s in stat[1:]:
                l = s.split(' : ')
                entry[l[0]] = l[1]
            stat_dict[stat[0].replace(' :', '')] = entry

        stat_dicts[test_names[t]] = stat_dict['Algorithm']

    return stat_dicts


def track_convergence(data, ref, test_dirs, metrics, time, eps=1e-2, exposure=1, sametime=False):
    """Track error convergence over partial renders."""

    def num_order(x): return int(x.split('_')[-1].split('.')[0])
    def round_10(x): return int(round(x))

    # All partial directories (one per algorithm)
    all_stats = []
    for partial_dir in test_dirs:
        # Determine extension by checking first partial file
        name = partial_dir.split(os.path.sep)[-1].replace('_partial', '')
        ext = detect_extension(os.path.join(partial_dir, '{}_1'.format(name)))

        # List all partial files
        glob_expr = os.path.join(partial_dir, '{}_[0-9]*.{}'.format(name, ext))
        partial_files = glob.glob(glob_expr)
        partial_files = sorted(partial_files, key=num_order)

        # All partial images within a directory
        dir_stat = []
        for partial_f in partial_files:
            test = load_img(partial_f) * exposure

            # Compute all metrics on (ref, test) pair
            metric_dict = {}
            for metric in metrics:
                err_img = compute_metric(ref, test, metric.lower(), eps)
                err_mean = '{:.6f}'.format(np.mean(err_img))
                metric_dict[metric] = err_mean
            dir_stat.append(metric_dict)

        all_stats.append(dir_stat)

    # Not sure if there's a better way to do this, maybe using itertools.chain?
    all_metrics = {}
    for metric in metrics:
        all_metrics[metric] = []
    for p, partial_dir in enumerate(test_dirs):
        for metric in metrics:
            seq = [float(stat[metric]) for stat in all_stats[p]]
            all_metrics[metric].append(seq)

    if time:
            time_entry = {'label' : "time", 'data': [], 'track' : {"x" : [], "y" : []}}
            data['stats'][0]['series'].append(time_entry)

    # Insert into dictionary (the ugliness of this is an artefact of using JSON...)
    for t, test_dir in enumerate(test_dirs):
        time_file = os.path.basename('{}_time.csv'.format(test_dir))
        with open(os.path.join(test_dir, time_file)) as fp:
            timesteps = [item for sublist in list(
                csv.reader(fp)) for item in sublist]
        if sametime:
            timesteps = [float(i) for i in range(len(timesteps))]
        else:
            timesteps = list(map(float, list(filter(None, timesteps))))

        for metric in metrics:
            for entry in data['stats'][0]['series']:
                if entry['label'] == metric.upper():
                    entry['track']['x'].append(timesteps)
                    entry['track']['y'].append(all_metrics[metric][t])
        
        # Write the time per iteration 
        if time:
            def time_conv(i):
                if i == 0:
                    return timesteps[0]
                else:
                    return timesteps[i] - timesteps[i-1]
            time_entry['track']['x']
            time_entry['track']['x'].append([i for i in range(len(timesteps))])
            time_entry['track']['y'].append([time_conv(i) for i in range(len(timesteps))])
            time_entry['data'].append('{:.6f}'.format(np.mean([time_conv(i) for i in range(len(timesteps))])))
         


def update_stats(path_dir, data, ref, tests, metrics, clip, eps=1e-2):
    """Update some entries of data.js; assumes it was already created."""

    def find_idx(t, d): return list(d['stats'][0]['labels']).index(t['name'])

    for test in tests:
        # Check if entry exists
        is_new = test['name'] not in data['stats'][0]['labels']

        # Update dictionary
        if is_new:
            data['imageBoxes'][0]['elements'].append(
                hdr_to_ldr(path_dir, test))
            data['stats'][0]['labels'].append(os.path.basename(test['name']))
        else:
            t = find_idx(test, data)
            hdr_to_ldr(path_dir, test)

        # Compute desired metrics
        for m, metric in enumerate(metrics):
            # Recompute error
            err_img = compute_metric(ref, test['data'], metric.lower(), eps)
            err_mean = '{:.6f}'.format(np.mean(err_img))
            if is_new:
                data['stats'][0]['series'][m]['data'].append(err_mean)
            else:
                data['stats'][0]['series'][m]['data'][t] = err_mean

            # Recompute false color heatmap and save to files
            fc = falsecolor(err_img, clip, eps)
            fc_fname = '{}-{}.jpg'.format(test['name'], metric.upper())
            fc_fname = fc_fname.replace(" ", "_")
            fc_fname = fc_fname.replace("+", "_")
            plt.imsave(os.path.join(path_dir, fc_fname), fc)

            if is_new:
                fc_entry = {'title': os.path.basename(test['name']),
                            'version': '-', 'image': fc_fname}
                data['imageBoxes'][m+1]['elements'].append(fc_entry)

    # TODO: Update stats.json
    return data


def compute_stats(path_dir, ref, tests, metrics, clip, negpos, eps=1e-2):
    """Generate all false color LDR maps and dictionary for JS.
       Assumes tests = {'name': 'my_alg', 'data': ...}
    """

    data = {}
    data['imageBoxes'] = [{'title': 'Images', 'elements': []}]
    data['stats'] = [{'title': 'Stats', 'labels': [], 'series': []}]
    ref_entry = hdr_to_ldr(path_dir, {'name': 'Reference', 'data': ref})
    data['imageBoxes'][0]['elements'].append(ref_entry)

    # Generate images and compute stats
    # Couldn't find a way to do it all in only two loops
    stats = []
    for t, test in enumerate(tests):
        # Update dictionary
        data['imageBoxes'][0]['elements'].append(hdr_to_ldr(path_dir, test))
        data['stats'][0]['labels'].append(os.path.basename(test['name']))

        # Compute all metrics
        stat_entry = {test['name']: {}}
        stats.append(stat_entry)
        for metric in metrics:
            # Compute error
            err_img = compute_metric(ref, test['data'], metric, eps)
            err_mean = '{:.6f}'.format(np.mean(err_img))

            # Compute false color heatmap and save to files
            fc = falsecolor(err_img, clip, eps)
            fc_fname = '{}-{}.jpg'.format(test['name'], metric.upper())
            fc_fname = os.path.basename(fc_fname)
            fc_fname = fc_fname.replace(" ", "_")
            fc_fname = fc_fname.replace("+", "_")
            plt.imsave(os.path.join(path_dir, fc_fname), fc)

            # Save stats, if necessary
            stats[t][test['name']][metric.upper()] = {
                'val': err_mean, 'fc': fc_fname}

    # Write dictionary
    for metric in metrics:
        fc_entry = {'title': metric.upper(), 'elements': []}
        metric_entry = {'label': metric.upper(), 'data': [], 'track': {
            'x': [], 'y': []}}

        for t, test in enumerate(tests):
            # Add false color filenames to dict
            fc_fname = stats[t][test['name']][metric.upper()]['fc']
            entry = {'title': os.path.basename(test['name']), 'version': '-', 'image': fc_fname}
            fc_entry['elements'].append(entry)

            # Add metric value to dict
            err_mean = stats[t][test['name']][metric.upper()]['val']
            metric_entry['data'].append(err_mean)

        # Update dictionary with false color filenames and metrics
        data['imageBoxes'].append(fc_entry)
        data['stats'][0]['series'].append(metric_entry)

    # Write negative/positive image if requested
    if negpos:
        fc_entry = {'title': 'NP SMAPE', 'elements': []}
        for t, test in enumerate(tests):
            # Compute the N/P false color image
            fc = falsecolor_np(ref, test['data'], eps)
            fc_fname = '{}-NP.jpg'.format(test['name'])
            fc_fname = os.path.basename(fc_fname)
            fc_fname = fc_fname.replace(" ", "_")
            fc_fname = fc_fname.replace("+", "_")
            plt.imsave(os.path.join(path_dir, fc_fname), fc)

            # Save the fcname inside JSON
            entry = {'title': os.path.basename(test['name']), 'version': '-', 'image': fc_fname}
            fc_entry['elements'].append(entry)

        # Update dictionary with false color filenames
        data['imageBoxes'].append(fc_entry)

    generate_thumbnail(path_dir, ref)
    return data


def detect_extension(filepath):
    """Check if file (with supported extension) exists and return its extension."""
    if os.path.exists(filepath + '.exr'):
        return 'exr'
    elif os.path.exists(filepath + '.hdr'):
        return 'hdr'
    elif os.path.exists(filepath + '.jpg'):
        return 'jpg'
    else:
        raise Exception("Unsupported file extension for: {}".format(filepath))


def load_img(filepath):
    """Load HDR or LDR image (either .hdr or .exr for HDR or .jpg for LDR)."""

    if filepath.endswith('.exr'):
        fp = pyexr.open(filepath)
        img = np.array(fp.get(), dtype=np.float64)
    elif filepath.endswith('.hdr'):
        fp = cv2.imread(filepath, cv2.IMREAD_ANYDEPTH)
        fp = cv2.cvtColor(fp, cv2.COLOR_BGR2RGB)
        img = np.array(fp, dtype=np.float64)
    elif filepath.endswith('.jpg'):
        fp = cv2.imread(filepath)
        fp = cv2.cvtColor(fp, cv2.COLOR_BGR2RGB)
        # important to be signed, because some metrics' calculations can have intermediate negative values.
        img = np.array(fp, dtype=np.int32)
    else:
        raise Exception('Only HDR and OpenEXR and jpg images are supported')

    return img


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Batch analysis of rendered images.')

    parser.add_argument('-r',   '--ref',
                        help='reference image filename', type=str, required=True)
    parser.add_argument('-t',   '--tests',
                        help='test images filename', nargs='+', type=str)
    parser.add_argument('-n',   '--names',
                        help='algorithms names', nargs='+', type=str)
    parser.add_argument('-m',   '--metrics',   help='difference metrics', nargs='+',
                        choices=['l1', 'l2', 'mrse', 'mape', 'smape', 'dssim'], type=str, required=True)
    parser.add_argument('-s',   '--select',   help='select run with name pattern', nargs='+',
                        type=str)
    parser.add_argument('-np',  '--negpos',
                        help='shows negative/positive SMAPE', action='store_true')
    parser.add_argument('-time',  '--time',
                        help='shows time per iteration', action='store_true')
    parser.add_argument('-p',   '--partials',
                        help='partial renders to track convergence', nargs='+', type=str)
    parser.add_argument('-eps', '--epsilon',
                        help='epsilon value', type=float, default=1e-2)
    parser.add_argument('-exp', '--exposure',
                        help='exposure value', type=float, default=0.0)                      
    parser.add_argument('-c',   '--clip',      help='clipping values for min/max',
                        nargs=2, type=float, default=[0, 1])
    parser.add_argument('-d',   '--dir',       
                        help='corresponding viewer scene directory', type=str, required=True)
    parser.add_argument('-A',   '--automatic',
                        help='scene directory for automatic mode', type=str, action="append", default=[])
    parser.add_argument('-x',   '--rename',
                        help='Rename technique ["previous_name:new_name"]', action="append", default=[])

    # DEBUG flag
    parser.add_argument('--sametime', 
                        help='make all technique have the same rendering time per iteration', action='store_true')

    args = parser.parse_args()

    # In automatic mode, check if conflicts with other arguments
    # Automatic mode can be used to save time during experiments
    # Proper command arguments needed to be generated
    tests = args.tests
    names = args.names
    exposure = math.pow(2, args.exposure)
    reference = args.ref
    partials = [] if args.partials is None else args.partials
    rename = {}
    for r in args.rename:
        v = r.split(":")
        rename[v[0]] = v[1]

    if (not os.path.exists(reference)):
        raise Exception(
            'Could not load reference image: {}'.format(reference))

    if args.automatic != []:
        # Arguments needs to be empty for automatic mode
        if (tests != None):
            raise Exception(
                'Tests (--tests) cannot be used with automatic mode (-A)')
        if (names != None):
            raise Exception(
                'Names (--names) cannot be used with automatic mode (-A)')
        if (len(partials) != 0):
            raise Exception(
                'Partials (--partials) cannot be used with automatic mode (-A)')
        tests, names, partials = [], [], []
    else:
        # Check if everything needed is provided
        if (tests == None):
            raise Exception(
                'Tests (--tests) is required when not in automatic mode')


    for auto_dir in args.automatic:
        # Extract all the techniques names
        print(f'[GLOB] {os.path.join(auto_dir, "*")}')
        for t in glob.glob(os.path.join(auto_dir, '*')):
            if not os.path.isdir(t):
                # We are only interested about the directory
                # Normally, each directory contain a run...
                continue 

            name = t.split(os.path.sep)[-1] #.replace('_partial', '')
            match = False
            if args.select:
                for s in args.select:
                    match = match or fnmatch.fnmatch(name, s)
            else:
                match = True
            if not match:
                print(f'[IGNORE] {name}')
                continue
            
            # Rename if necessary
            t_name = os.path.basename(t)
            if t_name in rename:
                print(f'[RENAME] {t_name} -> {rename[t_name]}')
                t_name = rename[t_name]
            names += [t_name]
            
            # Partial does not change name
            partials += [t]

            # Determine extension by checking first partial file
            ext = detect_extension(os.path.join(t, '{}_1'.format(name)))

            # Representative image is last updated file
            glob_expr = os.path.join(t, '{}_[0-9]*.{}'.format(name, ext))
            img = glob.glob(glob_expr)
            if (len(img) == 0):
                raise Exception(
                    'Could not find files matching {}'.format(glob_expr))
            img = max(img, key=os.path.getctime)

            tests += [img]
        print(f'Names founds: {names}')

    # Clean partial path by removing os.path.sep
    for i in range(len(partials)):
        partials[i] = partials[i][:-
                                  len(os.path.sep)] if partials[i].endswith(os.path.sep) else partials[i]

    # Print informations
    print('Arguments info')
    print('- Tests: ')
    for t in tests:
        print('  * {}'.format(t))
    print('- Partials: ')
    for t in partials:
        print('  * {}'.format(t))

    # Load images
    ref = load_img(reference) * exposure
    test_configs, test_names = [], []
    for i, t in enumerate(tests):
        img = load_img(t) * exposure
        if names:
            test_name = names[i]
        else:
            test_name = t#os.path.splitext(t)[0].replace('-', ' ')

        # For e.g. handling greek symbols
        test_name = test_name.encode('utf8').decode('unicode_escape')
        test_names.append(test_name)
        test_configs.append({'name': os.path.basename(test_name), 'data': img})

    # Compute stats
    sys.stdout.write('Computing stats... ')
    sys.stdout.flush()
    data = compute_stats(args.dir, ref, test_configs,
                         args.metrics, args.clip, args.negpos, args.epsilon)
    if (partials):
        track_convergence(data, ref, partials, args.metrics, args.time, args.epsilon, exposure, args.sametime)
    write_data(args.dir, data)
    print('done.')
