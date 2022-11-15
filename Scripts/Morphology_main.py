#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 24 09:21:33 2022

@author: thibault
"""
import Traits_class as tc
import json, sys, math
import numpy as np
import argparse

def get_scale(metadata_file):

    '''
    extract the scale value from metadata file
    '''
    
    f = open(metadata_file)
    metadata_dict = json.load(f)
    scale = "None"
    unit = "None"

    if 'ruler' in metadata_dict  :
        scale = round(metadata_dict['ruler']['scale'],3)
        unit = metadata_dict['ruler']['unit']
        
    return scale , unit


# this class is used by json.dump to control that every value as the right format
# particular problem encounter with np.int64 value type
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            print(obj)
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def argument_parser():
    parser = argparse.ArgumentParser(description='Extract information from segmented image, presence absence\
                                     landmarks, measures.')
    parser.add_argument('input_image', help='Path of segmented fish image. Format PNG image file.')
    parser.add_argument('output_presence', help='Path of output presence absence table. Format JSON file.')
    
    
    parser.add_argument('--metadata', help='Path of input drexel_metadata_formatter. Format JSON metadata file.')
    parser.add_argument('--morphology', 
                        help='Save the dictionnary of morphology measurements with the provided filename.')
    parser.add_argument('--landmark', 
                        help='Save the dictionnary of landmarks with the provided filename.')
    parser.add_argument('--lm_image', 
                        help='Save the visualisation of landmarks with the provided filename.')
    return parser

def main():
    
    
    parser = argument_parser()
    args = parser.parse_args()
    
    
    # Create the image segmentation object
    img_seg = tc.Segmented_image(args.input_image, align=True)
    base_name = img_seg.base_name
    # Create object measure_morphology
    measure_morph = tc.Measure_morphology(args.input_image, align=True)
    # Calcualte the mesaurements and landmarks
    
    # Assign variables from img_seg
    presence_matrix = {'base_name' : base_name, **img_seg.presence_matrix}
    # Assign variable from measure_morph
    measurements_bbox = measure_morph.measurement_with_bbox
    measurements_lm = measure_morph.measurement_with_lm
    measurements_area = measure_morph.measurement_with_area
    landmark = measure_morph.landmark
    
    
    
    # Combine the 3 types of measurements (lm, bbox, area) and reorder the keys
    measurement = {'base_name': base_name, **measurements_bbox, **measurements_lm, **measurements_area }
    list_measure= ['base_name', 'SL_bbox', 'SL_lm', 'HL_bbox', 'HL_lm', 'pOD_bbox', 'pOD_lm', 'ED_bbox', 'ED_lm', 'HH_lm', 'EA_m','HA_m','FA_pca','FA_lm']
    measurement = {k:measurement[k] for k in list_measure}
    
    
    with open(args.output_presence, 'w') as f:
        json.dump(presence_matrix, f) 
    
    # Extract the scale from metadata file
    # and add it to measurement dict
    if args.metadata:
        
        scale , unit = get_scale(args.metadata)
        measurement['scale'] = scale
        measurement['unit'] = unit                   
      
        
    # Save the dictionnaries in json file
    # use NpEncoder to convert the value to correct type (np.int64 -> int)
    if args.morphology:
        
        with open(args.morphology, 'w') as f:
            json.dump(measurement, f, cls=NpEncoder)    
    
    if args.landmark:
        with open(args.landmark, 'w') as f:
            json.dump(landmark, f)
           
    
    if args.lm_image:
        
        # create landmark visualization image and save it
        img_landmark = measure_morph.visualize_landmark()
        img_landmark.save(args.lm_image)
    
    
if __name__ == '__main__':

    main()
