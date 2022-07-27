#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 24 09:21:33 2022

@author: thibault
"""
import Traits_class as tc
import json, sys, math
import numpy as np

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


def get_angle(metadata_file):

    '''
    Calculate fish orientation from metadata file using major axis
    return value in degree
    
    '''
    f = open(metadata_file)
    data = json.load(f)
    metadata_fish = list(data.values())[0]['fish'][0]
    fish_angle = None
    major = []
    length = []
    
    if 'primary_axis' in metadata_fish  :
        
        major = metadata_fish['primary_axis']
        fish_angle = math.atan2(major[1], -major[0])*(180/math.pi)
        
    return round(fish_angle,2)

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

def main(input_file, metadata_file, output_measure, output_landmark, output_presence, 
         output_lm_image=None):
    
    # Create the image segmentation object
    img_seg = tc.segmented_image(input_file)
    base_name = img_seg.base_name
    # Calcualte the mesaurements and landmarks
    img_seg.get_all_measures_landmarks()
    
    # Assign variables
    measurements_bbox = img_seg.measurement_with_bbox
    measurements_lm = img_seg.measurement_with_lm
    measurements_area = img_seg.measurement_with_area
    landmark = img_seg.landmark
    presence_matrix = img_seg.presence_matrix
    
    # Combine the 3 types of measurements (lm, bbox, area) and reorder the keys
    measurement = {'base_name': base_name, **measurements_bbox, **measurements_lm, **measurements_area }
    list_measure= ['base_name', 'SL_bbox', 'SL_lm', 'HL_bbox', 'HL_lm', 'pOD_bbox', 'pOD_lm', 'ED_bbox', 'ED_lm', 'HH_lm', 'EA_m','HA_m','FA_pca','FA_lm']
    measurement = {k:measurement[k] for k in list_measure}
    
    # Extract the scale from metadata file
    # and add it to measurement dict
    scale , unit = get_scale(metadata_file)
    measurement['scale'] = scale
    measurement['unit'] = unit                   
    
    # Extract the fish angle from metadata file
    # and add it to measurement dict
    fish_angle = get_angle(metadata_file)
    measurement['FA_pca_meta'] = fish_angle    
        
    # Save the dictionnaries in json file
    # use NpEncoder to convert the value to correct type (np.int64 -> int)
    with open(output_measure, 'w') as f:
        json.dump(measurement, f, cls=NpEncoder)    
        
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
