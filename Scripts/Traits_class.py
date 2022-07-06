#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 18 16:02:54 2022

@author: thibault
Class definition for morpholopgy analysis
Version 1
"""
import os, sys, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.measure import label, regionprops
from skimage.morphology import reconstruction

class segmented_image:
    
    def __init__(self, file_name):
        self.file = file_name
        self.image_name = os.path.split(file_name)[1]     # creates a new empty list for each dog
        self.trait_color_dict={'background': [0, 0, 0],'dorsal_fin': [254, 0, 0],'adipos_fin': [0, 254, 0],
                               'caudal_fin': [0, 0, 254],'anal_fin': [254, 254, 0],'pelvic_fin': [0, 254, 254],
                               'pectoral_fin': [254, 0, 254],'head': [254, 254, 254],'eye': [0, 254, 102],
                               'caudal_fin_ray': [254, 102, 102],'alt_fin_ray': [254, 102, 204],
                               'trunk': [0, 124, 124]}
        self.img_arr = self.import_image(file_name)
        self.get_channels_mask()
        self.presence_matrix = self.get_presence_matrix()
        self.landmark = self.all_landmark()
        self.measurement = self.all_measure()
        
    def import_image(self,file_name):
        '''
        import the image from "image_path" and convert to np.array astype uint8 (0-255)
        '''
        img = Image.open(file_name)
        img_arr = np.array(img, dtype=np.uint8)

        return img_arr

                
    def get_channels_mask(self):
        ''' Convert the png image (numpy.ndarray, np.uint8)  (320, 800, 3)
        to a mask_channel (320, 800, 12) Binary map

        input
        output
        img shape -> (320, 800, 3) if normal=True
        else: mask shape -> (11, 320, 800)
            we want to output a PIL image with rgb color value
            '''
        trait_color_dict = self. trait_color_dict
        img = self.img_arr
        mask = {}
        for i, (trait, color) in enumerate(trait_color_dict.items()):
            if trait != "background":
                
                trait_mask = (img[:, :, 0] == color[0]) &\
                            (img[:, :, 1] == color[1]) &\
                            (img[:, :, 2] == color[2])
                mask[trait]=trait_mask.astype("uint8")
                
        self.mask = mask
        
    def align_fish(self):
        '''
        development
        To align the fish horizontally
        in order to get landmark 5 and 6
        '''
        
        img_arr = self.img_arr
        traits_to_combine = list(self.trait_color_dict.keys())[1:]
        combine_mask  = self.combine_trait_mask(traits_to_combine)
        region = self.clean_trait_region(combine_mask)
        angle_rad = region.orientation
        angle_deg = (90-angle_rad*180/math.pi)
        image_align = Image.fromarray(img_arr).rotate(angle_deg)
        
        return image_align
    
    def visualize_trait(self, trait):
        
        mask = self.mask
        trait_color_dict = self. trait_color_dict
        
        if trait in list(trait_color_dict.keys()):
            return Image.fromarray(mask[trait]*255)
            
        else:
            print(f'trait {trait} is not reference')
    
    def remove_holes(self, image):
        
        seed = np.copy(image)
        seed[1:-1, 1:-1] = image.max()
        mask = image
        filled = reconstruction(seed, mask, method='erosion')
        return filled
   
    
    def clean_trait_region(self, trait_mask, percent_cut = 0.5):
        '''
        Clean the mask_trait (remove holes)
        Find the biggest region
        return region_trait
        '''
        
        # remove hole/fill empty area
        trait_filled = self.remove_holes(trait_mask)
        
        # total area of the trait
        total_area = np.count_nonzero(trait_filled == 1)
        trait_label = label(trait_filled)
        trait_region = regionprops(trait_label)
        
        if total_area>0:
        
            # Get the biggest instance(blob) of the trait
            biggest_region = sorted(trait_region, key=lambda r: r.area, reverse=True)[0]
            percent = biggest_region.area/total_area
            if percent >=percent_cut:
                trait_region = biggest_region                
            else:
                trait_region =[]
        return trait_region
    
    def get_presence_matrix(self):
        '''
        Create a matrix with presence, number of blob, percent of the biggest
        instance for each trait
        '''
        mask = self.mask
        presence_matrix = {}
        
        for i, (trait_name, trait_mask) in enumerate(mask.items()):

            temp_dict = {}
            total_area = np.count_nonzero(trait_mask == 1)
            label_trait = label(trait_mask)
            trait_regions = regionprops(label_trait)

            temp_dict["number"] = len(trait_regions)
        
            if len(trait_regions) > 0:
                biggest_region = sorted(trait_regions, key=lambda r: r.area, reverse=True)[0]
                temp_dict["percentage"] = biggest_region.area/total_area
            else: 
                    temp_dict["percentage"] = 0

            presence_matrix[trait_name] = temp_dict
            
        return presence_matrix
    
    
    def get_one_property_all_trait(self, property_='centroid'):
        '''
        Create a dictionnary with key = trait and value the property selected by property_
        example: {'dorsal_fin': (centroid[0], centroid[1]), 'trunk':(centroid[0], centroid[1])....}
        '''
        
        mask = self.mask
        dict_property={}
        # enumerate through the dictionary of mask to collect trait_name
        for i, (trait_name, trait_mask) in enumerate(mask.items()):
            
            trait_region = self.clean_trait_region(trait_mask)
            
            if trait_region:  
                dict_property[trait_name] = trait_region[property_]
            else:
                dict_property[trait_name]=None
                
        return dict_property
    
    def get_distance(self, a,b):
        '''
        measure distance between two points if they are not empty
        a and b : tuple (x,y)
    
        '''
        distance=0
        # a and b are not None calculate the distance
        if a and b:
            distance = ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5
        return distance
    

    def get_distance_table(self):
        '''
        Create a matrix with distance between centroid of traits
        '''
        centroid_dict = self.get_one_property_all_trait()
        distance_matrix = {}
        
        for i, (trait_name, centroid) in enumerate(centroid_dict.items()):
            
            distance_matrix[trait_name] = {k: self.get_distance(centroid,v)  
                             for i, (k,v) in enumerate(centroid_dict.items())}
            
        return distance_matrix
    
    def combine_trait_mask(self, list_trait=['head','trunk']):
        
        mask = self.mask
        combo = np.zeros_like(mask,dtype="uint8")
        
        for trait in list_trait:
            
            combo = combo + mask[trait]
            
        #combo_cleaned = self.remove_holes(combo)
        
        return combo
    
    def get_body_len(self):
        '''
        body length from snout to back to the trunk
        1- Combine head and trunk
        2- Create a clean trait region clean_trait_region
        3- Measure distance long axis, bbox
        '''
        head_trunk = self.combine_trait_mask()
        trait_region= self.clean_trait_region(head_trunk)
        orientation = trait_region.orientation
        xb0, yb0, xb1, yb1 = trait_region.bbox
        len1 =(yb1-yb0)/math.sin(orientation)
        bbox_len = yb1-yb0
        return len1, bbox_len
        
    def visualize_major_minor(self):
        
        trait_mask = self.combine_trait_mask()
        trait_region= self.clean_trait_region(trait_mask)
        x0, y0 = trait_region.centroid
        orientation = trait_region.orientation
        xb0, yb0, xb1, yb1 = trait_region.bbox
        
        # Drawing object
        # Create rgb image
        trait_mask_rgb = np.stack((trait_mask, trait_mask, trait_mask), axis=2)
        #R = np.repeat(mask_line[:,:,np.newaxis],3, axis=2)
        img = Image.fromarray(trait_mask_rgb*255)
        img1 = ImageDraw.Draw(img)
        
        # Long axis
        x2 = x0 - 0.5 * (yb1-yb0)/math.tan(orientation)
        x1 = x0 + 0.5 * (yb1-yb0)/math.tan(orientation)
        long_axis = [(yb0, x2), (yb1, x1)]
        img1.line(long_axis, fill ="red", width = 2)
 
        
        # Short axis
        x1t = x0 + math.sin(orientation) * 0.5 * trait_region.axis_minor_length
        y1t = y0 - math.cos(orientation) * 0.5 * trait_region.axis_minor_length
        short_axis = [(y0, x0), (y1t, x1t)]        #img1.line(shape1, fill ="red", width = 2)
        img1.line(short_axis, fill ="red", width = 2)
        
        # Display the image created
        img.show()
        
                
    def landmark_generic(self, trait_name):
        '''
        Identify landmark of a trait (trait_name)
        front, back, top, bottom of the trait and center
        this function works only if the fish is oriented head facing left
        '''
        
        mask = self.mask[trait_name]
        # remove the hole and take the biggest blob
        clean_mask = self.clean_trait_region(mask)
        # Create new mask with clean mask, remove hole and secondary blob
        # use clean_mask (region) to reconstruct a mask
        if clean_mask:
            bbox = clean_mask.bbox
            new_mask = np.zeros_like(mask)
            new_mask[bbox[0]:bbox[2],bbox[1]:bbox[3]]=clean_mask.image
            
            x,y = np.where(new_mask)
            # top
            x_top=x.min()
            y_top = round(np.mean(np.where(new_mask[x_top,:])))
            top_lm = (int(x_top),int(y_top))
    
            # bottom
            x_bottom=x.max()
            y_bottom = round(np.mean(np.where(new_mask[x_bottom,:])))
            bottom_lm = (int(x_bottom),int(y_bottom))
            
            #front 
            y_front = y.min()
            x_front = round(np.mean(np.where(new_mask[:, y_front,])))
            front_lm = (int(x_front),int(y_front))
            
            #back 
            y_back=y.max()
            x_back = round(np.mean(np.where(new_mask[:, y_back,])))
            back_lm = (int(x_back),int(y_back))
            centroid = clean_mask.centroid
        else:
            front_lm , back_lm, top_lm, bottom_lm, centroid, new_mask = [], [], [], [], [], []
        
        return front_lm, back_lm, top_lm, bottom_lm, centroid, new_mask
    
    def landmark_5_7(self):
        '''
        locate the landmark 5 and 7 of the caudal fin. 
        We split the caudal fin upper and lower part (horizontal line through the middle).
        Then, in each case get the mot left point in the half of the caudal fin
        '''
        _,_,_,_,center_caudal,new_mask_caudal= self.landmark_generic('caudal_fin')
        
        if np.any(new_mask_caudal):
            mask_caudal_5 = new_mask_caudal.copy()
            mask_caudal_7 = new_mask_caudal.copy()
            row_caudal = round(center_caudal[0])

            mask_caudal_5[row_caudal:,:] = 0
            mask_caudal_7[:row_caudal,:] = 0
        
            lm_5_7=[]
            for temp_mask in [mask_caudal_5,mask_caudal_7]:        
                x,y = np.where(temp_mask)
                y_front = y.min()
                x_front = round(np.mean(np.where(temp_mask[:, y_front,])))
                lm_5_7.append((int(x_front),int(y_front)))
                
            return lm_5_7[0], lm_5_7[1]   
        else: 
            return [],[]
        
    def all_landmark(self):
        '''
        Calculate of the landmark
        front, back, top, bottom, center, new_mask = self.landmark_generic(trait_name)
        '''
        landmark={}
        #eye
        landmark['14'], landmark['15'], landmark['16'], landmark['17'], center_eye, _ = self.landmark_generic('eye')     
        landmark['18'] = (round(center_eye[0]), round(center_eye[1]))
        # head
        landmark['1'], landmark['12'], landmark['2'] , landmark['13'], _, new_mask_head = self.landmark_generic('head')
        
        #landmark #5 and 7 caudal fin
        landmark['5'], landmark['7'] = self.landmark_5_7()
        
        #trunk
        _, landmark['6'],_ ,_ ,_ ,_ = self.landmark_generic('trunk')
        
        # Fins : ['dorsal_fin', 'anal_fin', 'pelvic_fin', 'pectoral_fin']
        landmark['3'],_ , _, landmark['4'], _,  _ = self.landmark_generic('dorsal_fin')
        landmark['11'],_ , _,_, _, _ = self.landmark_generic('pectoral_fin')
        landmark['10'],_ , _,_, _, _ = self.landmark_generic('pelvic_fin')
        landmark['9'], _, landmark['8'] , _, _, _ = self.landmark_generic('anal_fin')
        
        
        # reorder the key 
        new_landmark={}
        list_order = [str(i) for i in range(1,16)]
        for key in list_order:
            new_landmark[key] = landmark[key]                     
                                
        return new_landmark

    
    def measure_eye_area(self):
        '''
        Calculate eye area after cleaning and filing hole
        
        '''
        mask = self.mask
        eye_region = self.clean_trait_region(mask['eye'])
        if eye_region:
            return eye_region.area
        else:
            return 'None'
    
    def measure_head_area(self):
        '''
        Calculate head area  after cleaning and filing hole
        
        '''
        mask = self.mask
        head_region = self.clean_trait_region(mask['head'])
        
        if head_region:
            return head_region.area
        else:
            return 'None' 
    
    def measure_eye_head_ratio(self):
        '''
        Create eye head area ratio
        1- Area head after cleaning  and filling hole
        2- Area eye after cleaning and filing hole
        3- ratio
        '''
        eye_areaa = measure_eye_area()
        head_area = measure_head_area()
        
        eye_head_ratio = eye_area/head_area
        
        return eye_head_ratio    
    
    
    def measure_eye_diameter(self):        
        '''
        Calculate eye equivalent diameter : diameter of the disk of the same area
        (area/pi)^1/2
        '''
        mask = self.mask
        eye_region = self.clean_trait_region(mask['eye'])
            
        eq_diameter = eye_region.equivalent_diameter_area
            
        return eq_diameter    
     
    def measure_head_length(self):
        '''
        Measure vertical length of the head passing by the center of the eye
        '''
        landmark = self.landmark
        p_2 = landmark['2']
        p_15 = landmark['15']
        head_length = self.get_distance(p_2,p_15)
        
        return head_length
    
    def calculate_triangle_area(self, point_1, point_2, point_3):
        
        # calculate the semi-perimeter
        a = self.get_distance(point_1, point_2)
        b = self.get_distance(point_2, point_3)
        c = self.get_distance(point_3, point_1)
        
        s = (a + b + c) / 2

        # calculate the area
        area = (s*(s-a)*(s-b)*(s-c)) ** 0.5
        return area
    
    def measure_head_depth(self):
        '''
        Measure vertical length of the head passing by the center of the eye
        '''
        #eye
        _, _, _, _, center_eye, _ = self.landmark_generic('eye')     

        # head
        _, _, _, _, _, new_mask_head = self.landmark_generic('head')
        # landmark 15
        # head length, vertical line of the head passing by the center of the eye
        row_eye = round(center_eye[0])
        
        head_hori_line = new_mask_head[row_eye,:]
        head_depth = np.count_nonzero( head_hori_line)
    
        return head_depth
    
    
    def all_measure(self):        
        '''
        Collect all the measurment for the fish
        '''
        landmark = self.landmark
        measure={'SL':'None', 'EA':'None', 'HAt':'None', 'HAp':'None', 'HCL':'None', 'ED':'None', 'HL':'None', 'HD':'None','pOD':'None', }
        # Standard Length (body length)
        if landmark['1'] and landmark['6']:
            measure['SL'] = self.get_distance(landmark['1'],landmark['6'])
        # Eye Area
        measure['EA'] = int(self.measure_eye_area())
        # Head Area triangle
        if landmark['1'] and landmark['2'] and landmark['13']:
            measure['HAt'] = self.calculate_triangle_area(landmark['1'],landmark['2'],landmark['13'])
        # Head area
        measure['HAp'] = self.measure_head_area()
        # Head to caudal line
        measure['HCL'] = "WIP"
        # Eye Diameter
        measure['ED'] = self.measure_eye_diameter()
        # Head Length
        if landmark['1'] and landmark['12']:
            measure['HL'] = self.get_distance(landmark['1'],landmark['12'])
        # Head Depth
        if landmark['2'] and landmark['13']:
            measure['HD'] = self.get_distance(landmark['2'],landmark['13'])
        # preObital Depth
        if landmark['1']and landmark['14']:
            measure['pOD'] = self.get_distance(landmark['1'],landmark['14'])
        return measure
        
    def visualize_landmark(self):
            
        
            landmark = self.all_landmark()
            img_arr = self.img_arr
            img = Image.fromarray(img_arr)
            img1 = ImageDraw.Draw(img)
        
            #
            #fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 15)
            fnt = ImageFont.load_default()
            for i,(k,v) in enumerate(landmark.items()):
                if v:
                    x,y = v
                    xy = [(y-9,x-9),(y+9,x+9)]
                    img1.ellipse(xy, fill='gray', outline=None, width=1)
                
                    img1.text((y-6, x-6), k, font=fnt, fill='black')
            # Display the image created
            
            return img


