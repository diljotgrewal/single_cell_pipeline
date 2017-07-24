'''
Created on Jul 24, 2017

@author: dgrewal
'''
import pandas as pd



def concatenate_csv(in_filenames, out_filename, nan_val = 'NA'):
    data = []
    for _, in_filename in in_filenames.iteritems():
        with open(in_filename) as f:
            first_line = f.readline()
            if len(first_line) == 0:
                continue
        data.append(pd.read_csv(in_filename, dtype=str))
    data = pd.concat(data, ignore_index=True)
    data = data.fillna(nan_val)
    data.to_csv(out_filename, index=False)


def merge_csv(in_filenames, out_filename, how, on, nan_val = 'NA'):
    data = []
    for _, in_filename in in_filenames.iteritems():
        with open(in_filename) as f:
            first_line = f.readline()
            if len(first_line) == 0:
                continue
        print in_filename
        data.append(pd.read_csv(in_filename, dtype=str))

    data = merge_frames(data, how, on)
    data = data.fillna(nan_val)
    data.to_csv(out_filename, index=False)


def merge_frames(frames, how, on):
    '''
    annotates input_df using ref_df
    '''

    if ',' in on:
        on = on.split(',')

    if len(frames) == 1:
        return frames[0]
    else:
        left = frames[0]
        right = frames[1]
        merged_frame = pd.merge(left, right,
                                    how=how,
                                    on=on)
        for frame in frames[2:]:
            merged_frame = pd.merge(merged_frame, frame,
                                        how=how,
                                        on=on)
        return merged_frame
