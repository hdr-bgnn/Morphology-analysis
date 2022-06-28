#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 24 09:21:33 2022

@author: thibault
"""
import Traits_class as tc
import json, sys

def get_scale(metadata_file):

    '''
    extract the scale value from metadata file
    '''
    
    f = open(metadata_file)
    data = json.load(f)
    metadata_dict = list(data.values())[0]

    if 'scale' in metadata_dict  :

        scale = round(metadata_dict['scale'],3)
        unit = metadata_dict['unit']
    else:
        scale =[None]
        unit =[None]
    return scale , unit


def main(input_file, metadata_file, output_measure, output_landmark, output_presence, 
         output_lm_image=None):
    
    img_seg = tc.segmented_image(input_file)
    measurement = img_seg.measurement
    landmark = img_seg.landmark
    presence_matrix = img_seg.presence_matrix
    
    # Extract the scale from metadata file
    # and add it to measurement dict
    scale , unit = get_scale(metadata_file)
    measurement['scale'] = scale
    measurement['unit'] = unit                   
    
    # Save the dictionnaries in json file
    with open(output_measure, 'w') as f:
        json.dump(measurement, f)    
        
    with open(output_landmark, 'w') as f:
        json.dump(landmark, f)
        
    with open(output_presence, 'w') as f:
        json.dump(presence_matrix, f)    
    
    if output_lm_image:
        
        img_landmark = img_seg.visualize_landmark()
        img_landmark.save(output_lm_image)
    
    
if __name__ == '__main__':

    input_file = sys.argv[1]
    metadata_file = sys.argv[2]
    output_measure = sys.argv[3]
    output_landmark = sys.argv[4]
    output_presence = sys.argv[5]
    output_lm_image = None
    
    
    if len(sys.argv)==7:
        output_lm_image = sys.argv[6]
        
    main(input_file, metadata_file, output_measure, output_landmark, output_presence, 
         output_lm_image=output_lm_image)
