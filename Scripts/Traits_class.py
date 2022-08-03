#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 18 16:02:54 2022

@author: thibault
Class definition for morpholopgy analysis
Version 1
"""
import os, sys, math, json
from operator import sub
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.measure import label, regionprops
from skimage.morphology import reconstruction


class Segmented_image:
    
    def __init__(self, file_name, align = True, cutoff = 0.6):
        self.file = file_name
        self.image_name = os.path.split(file_name)[1]
        self.base_name = self.image_name.rsplit('_',1)[0]
        self.cutoff = cutoff
        self.align = align
        
        self.trait_color_dict={'background': [0, 0, 0],'dorsal_fin': [254, 0, 0],'adipos_fin': [0, 254, 0],
                               'caudal_fin': [0, 0, 254],'anal_fin': [254, 254, 0],'pelvic_fin': [0, 254, 254],
                               'pectoral_fin': [254, 0, 254],'head': [254, 254, 254],'eye': [0, 254, 102],
                               'caudal_fin_ray': [254, 102, 102],'alt_fin_ray': [254, 102, 204],
                               'trunk': [0, 124, 124]}
        
        self.img_arr = self.import_image(file_name)
        self.fish_angle = self.get_fish_angle_pca()
        if align:
            self.img_arr = self.align_fish()
            self.old_fish_angle = self.fish_angle
            self.fish_angle = self.get_fish_angle_pca()
                    
        self.get_channels_mask()
        self.presence_matrix = self.get_presence_matrix()
                        
    def import_image(self,file_name):
        '''
        Import the image from "image_path" and convert to np.array astype uint8 (0-255)
        '''
        img = Image.open(file_name)
        img_arr = np.array(img, dtype=np.uint8)

        return img_arr

    def get_fish_angle_pca(self):
        '''
        Calculate orientation (PCA) of the mask of whole fish
        We choose to combine whole fish part and calculate orientation.
        return value in degree
        '''
        
        # create a mask with all the fish traits 
        img_arr = self.img_arr
        whole_fish = np.sum(img_arr,axis=2).astype(bool)      

        # Clean holes and remove isolated blobs and create a regionprop
        trait_region = self.clean_trait_region(whole_fish)   
        angle_rad = trait_region.orientation
        #fish_angle = (90-angle_rad*180/math.pi)
        fish_angle = np.sign(angle_rad) * (90-abs(angle_rad*180/math.pi))
        
        # + 0.0 remove negative sign on rounded 0.0 value
        return round(fish_angle,2) + 0.0 
    

    def align_fish(self):
        '''
        Development
        To align the fish horizontally
        in order to get landmark 5 and 6
        '''
        
        img_arr = self.img_arr
        angle_deg = self.fish_angle
        
        image_align = Image.fromarray(img_arr).rotate(angle_deg)
        
        return  np.array(image_align, dtype=np.uint8)    
        
    
    def get_channels_mask(self):
        ''' 
        Convert the png image (numpy.ndarray, np.uint8)  (320, 800, 3)
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
    
    def remove_holes(self, image):
        
        seed = np.copy(image)
        seed[1:-1, 1:-1] = image.max()
        mask = image
        filled = reconstruction(seed, mask, method='erosion')
        return filled
   
    
    def clean_trait_region(self, trait_mask):
        '''
        Clean the mask_trait (remove holes)
        Find the biggest region
        return region_trait
        '''
        percent_cutoff = self.cutoff
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
            if percent >=percent_cutoff:
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

        
class Measure_morphology(Segmented_image):
    
    def __init__(self, file_name, align=True):
        
        super().__init__(file_name, align=True)
        self.get_all_measures_landmarks()
    
    def get_all_measures_landmarks(self):
        '''
        Execute the multiple functions that calculate landmarks and measurements
        '''
        self.landmark = self.all_landmark()
        self.measurement_with_bbox = self.all_measure_using_bbox()
        self.measurement_with_lm = self.all_measure_using_lm()
        self.measurement_with_area = self.all_measure_area()
    
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
            if np.any(mask[trait]):
                combo = combo + mask[trait]
            else:
                return None
            
        #combo_cleaned = self.remove_holes(combo)
        
        return combo
        
#######################
# Measure the landamrks    
#######################
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
        cutoff =  self.cutoff
        presence_matrix = self.presence_matrix
        
        # initialize a dictionnary with keys and empty lists as value
        landmark={str(k):[] for k in range(1,19)}

        #eye
        if presence_matrix['eye']['percentage']>=cutoff:
            
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
        
        # reorder the keys of the dictionnary 
        new_landmark={}
        list_order = [str(i) for i in range(1,19)]
        for key in list_order:
            new_landmark[key] = landmark[key]                     
                                
        return new_landmark
    
####################################
# Calculate measurements using landmarks
####################################

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
        eye_area = measure_eye_area()
        head_area = measure_head_area()
        
        if eye_area>0 and head_area>0:
            eye_head_ratio = eye_area/head_area
        
        return round(eye_head_ratio,2)    
        
    def measure_eye_diameter(self):        
        '''
        Calculate eye equivalent diameter : diameter of the disk of the same area
        (area/pi)^1/2
        '''
        mask = self.mask
        eq_diameter = 0
        eye_region = self.clean_trait_region(mask['eye'])
        if  eye_region:   
            eq_diameter = eye_region.equivalent_diameter_area
            
        return round(eq_diameter,2)    
     
    def measure_head_length(self):
        '''
        Measure vertical length of the head passing by the center of the eye
        '''
        
        landmark = self.landmark
        p_2 = landmark['2']
        p_15 = landmark['15']
        # IF p_2 or p_15 get_distance will return 0
        head_length = self.get_distance(p_2,p_15)
        
        return round(head_length,2)
    
    def calculate_triangle_area(self, point_1, point_2, point_3):
        
        # calculate the semi-perimeter
        a = self.get_distance(point_1, point_2)
        b = self.get_distance(point_2, point_3)
        c = self.get_distance(point_3, point_1)
        
        s = (a + b + c) / 2

        # calculate the area
        area = (s*(s-a)*(s-b)*(s-c)) ** 0.5
        return round(area,2)
    
    def measure_head_length(self):
        '''
        Measure horizontal length of the head passing by the center of the eye
        '''
        #eye
        _, _, _, _, center_eye, _ = self.landmark_generic('eye')     

        # head
        _, _, _, _, _, new_mask_head = self.landmark_generic('head')
        # head length, vertical line of the head passing by the center of the eye
        
        if center_eye and np.any(new_mask_head):
            row_eye = round(center_eye[0])
        
            head_hori_line = new_mask_head[row_eye,:]
            index_hori = np.where(head_hori_line == 1)[0]
        
            # Get start and end of the horizontal line to check
            start_h = (row_eye,np.max(index_hori))
            end_h = (row_eye,np.min(index_hori))
        
            head_length = np.count_nonzero( head_hori_line)
        
        return head_length, start_h, end_h
   
    def measure_head_depth(self):
        '''
        Measure vertical length of the head passing through the center of the eye
        '''
        head_depth = 'None'
        start_v = 'None'
        end_v = 'None'
        
        #eye
        _, _, _, _, center_eye, _ = self.landmark_generic('eye')     
        # head
        _, _, _, _, _, new_mask_head = self.landmark_generic('head')
        
        if center_eye and np.any(new_mask_head):
        
            # head depth, horizontal line of the head passing by the center of the eye
            col_eye = round(center_eye[1])
        
            head_vert_line = new_mask_head[:,col_eye]
        
            # Calculate the start and end of the vertical line, for sanity check
            index_verti = np.where(head_vert_line == 1)[0]
            start_v = (np.max(index_verti),col_eye)
            end_v = (np.min(index_verti),col_eye)
        
            head_depth = np.count_nonzero(head_vert_line)
    
        return head_depth, start_v, end_v
    
    def measure_body_length(self):
        '''
        Measure length of head, trunk, caudal_fin.
        Combine head, trunk, caudal_fin masks
        clean the mask
        get bbox and get length of bbox
        '''
        body_length = 'None'
        head_trunk_caudal = self.combine_trait_mask(['head','trunk','caudal_fin'])
        if np.any(head_trunk_caudal):
            
            trait_region= self.clean_trait_region(head_trunk_caudal)
            xb0, yb0, xb1, yb1 = trait_region.bbox
            body_length = yb1-yb0
    
        return body_length

    def measure_fish_angle_lm(self):
        '''
        measure fish angle using orientation of the line define by landmark#1 and landmark #6
        '''
        landmark = self.landmark
        fish_angle_lm = 'None'
        if landmark['1'] and landmark['6']:
            
            # translation to origin
            trans_to_origin = list(map(sub, landmark['6'], landmark['1']))
            fish_angle_lm = math.atan2(trans_to_origin[0], trans_to_origin[1])*(180/math.pi)
            fish_angle_lm = round(fish_angle_lm,2)
            
        return fish_angle_lm
    
    def all_measure_using_lm(self):        
        '''
        Collect all the measurment for the fish that are only using landmarks
        '''
        landmark = self.landmark
        measures_lm={'SL_lm':'None', 'HL_lm':'None','ED_lm':'None', 'HH_lm':'None', 'HH_lm_v2':'None', 'pOD_lm':'None' }
        # Standard Length (body length), landmark
        if landmark['1'] and landmark['6']:
            measures_lm['SL_lm'] = round(self.get_distance(landmark['1'],landmark['6']),2)

        # Head Length, landmark
        if landmark['1'] and landmark['12']:
            measures_lm['HL_lm'] = round(self.get_distance(landmark['1'],landmark['12']),2)
            
        #Eye Diamter, landmark
        if landmark['14'] and landmark['15']:
            measures_lm['ED_lm'] = round(self.get_distance(landmark['14'],landmark['15']),2)
        
        if landmark['18']:
            # Head Height, height of the line going through the middle of the eye landmark #18
            measures_lm['HH_lm'], start, end = self.measure_head_depth()
            # Sanity check for the measure of HH_lm using start and end of the vertical line through the eye
            measures_lm['HH_lm_v2'] = round(self.get_distance(start,end),2)
            
        # preObital Depth, landamrk
        if landmark['1'] and landmark['14']:
            measures_lm['pOD_lm'] = round(self.get_distance(landmark['1'],landmark['14']),2)
        
        # Head Depth, landmark
        if landmark['2'] and landmark['13']:
            measures_lm['HD_lm'] = round(self.get_distance(landmark['2'],landmark['13']),2)
        
        measures_lm['FA_lm'] = self.measure_fish_angle_lm()
        
        return measures_lm    

    def all_measure_area(self):
        '''
        Collect measuerements calculate using the area (measure from the skimage.measure.regionprops)
        '''
        measure_area = {'EA_m':'None', 'HA_m':'None'}
        # Eye Area
        measure_area['EA_m'] = self.measure_eye_area()
        # Head area
        measure_area['HA_m'] = self.measure_head_area()
        
        return measure_area
                
########################
# Measurement using bbox
########################

    def measure_SL_bbox(self):
        '''
        Measure SL (Standard Length), length of the bounding box of head + trunk
        Combine head and trunk and measure bbox length
        '''
        standard_length = 'None'
        head_trunk = self.combine_trait_mask(['head','trunk'])
        if np.any(head_trunk):
            
            trait_region= self.clean_trait_region(head_trunk)
            min_row, min_col, max_row, max_col = trait_region.bbox # (up, left, bottom, right) <=> (min_row, min_col, max_row, max_col)
            standard_length = max_col-min_col
            
        return standard_length         
           
    def measure_length_bbox(self, trait_name):
        '''
        Measure the length of bbox of the trait_name
        '''
        mask = self.mask[trait_name]
        # remove the hole and take the biggest blob
        trait_region = self.clean_trait_region(mask)
        trait_length_bbox = 'None'
        
        if trait_region:
            minrow, mincol, maxrow, maxcol = trait_region.bbox
            
            trait_length_bbox = maxcol-mincol
        
        return trait_length_bbox

    def measure_pOD_bbox(self):
        '''
        Measure preorbital Depth using left boubdary of bbox of head and eye
        '''
        pOD_bbox = 'None'
        mask_head = self.mask['head']
        mask_eye = self.mask['eye']
        head_region = self.clean_trait_region(mask_head)
        eye_region = self.clean_trait_region(mask_eye)
        
        if head_region and eye_region: 
            
            up_h, left_h, bot_h, right_h = head_region.bbox
            up_e, left_e, bot_e, right_e = eye_region.bbox
        
            pOD_bbox = int(left_e - left_h)
            
        return pOD_bbox
    
    def all_measure_using_bbox(self):
        '''
        Collect the measurment for the fish for Meghan paper
        '''
        measures_bbox={'SL_bbox':'None', 'HL_bbox':'None', 'ED_bbox':'None','pOD_bbox':'None', 'FA_pca':'None' }
        
        # SL standart length, length bbox of head+trunk
        
        measures_bbox['SL_bbox'] =  self.measure_SL_bbox()
        
        # HL Head Length, length of bbox of the head
        measures_bbox['HL_bbox'] = self.measure_length_bbox('head')
        # ED Eye Diameter
        measures_bbox['ED_bbox'] = self.measure_length_bbox('eye')

        # preorbital Depth
        measures_bbox['pOD_bbox'] = self.measure_pOD_bbox()
        
        # fish angle in case of connection
        measures_bbox['FA_pca'] = self.fish_angle
         
        return measures_bbox
    
    def visualize_landmark(self):
            
        landmark = self.all_landmark()
        img_arr = self.img_arr
        img = Image.fromarray(img_arr)
        img1 = ImageDraw.Draw(img)
        
        #
        #fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 15)
        fnt = ImageFont.load_default()
        for i,(k,v) in enumerate(landmark.items()):
            
            # landmark exist draw it on the image
            if v:
                row,col = v
                xy = [(col-9,row-9),(col+9,row+9)]
                img1.ellipse(xy, fill='gray', outline=None, width=1)
                
                img1.text((col-6, row-6), k, font=fnt, fill='black')
            # Display the image created
        return img    
    
class Visualization_morphology(Measure_morphology):     
############################
# Visualization function
############################
    def __init__(self, file_name, align=True):
        
        super().__init__(file_name, align=True)

    def visualize_trait(self, trait):
        
        mask = self.mask
        trait_color_dict = self. trait_color_dict
        
        if trait in list(trait_color_dict.keys()):
            return Image.fromarray(mask[trait]*255)
            
        else:
            print(f'trait {trait} is not reference')
            
    def visualize_landmark(self):
            
        landmark = self.all_landmark()
        img_arr = self.img_arr
        img = Image.fromarray(img_arr)
        img1 = ImageDraw.Draw(img)
        
        #
        #fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 15)
        fnt = ImageFont.load_default()
        for i,(k,v) in enumerate(landmark.items()):
            
            # landmark exist draw it on the image
            if v:
                row,col = v
                xy = [(col-9,row-9),(col+9,row+9)]
                img1.ellipse(xy, fill='gray', outline=None, width=1)
                
                img1.text((col-6, row-6), k, font=fnt, fill='black')
            # Display the image created
        return img
        
    def visualize_a_bbox(self, trait_name):

        # creating new Image object
        img_arr = self.img_arr
        img = Image.fromarray(img_arr)
        img1 = ImageDraw.Draw(img)
        
        # prepare the bbox for the "trait_name"
        trait_prop = self.clean_trait_region(self.mask[trait_name])
        top, left, bottom, right = trait_prop.bbox

        shape = [(left, top), (right,bottom)]
        
        # create rectangle image 
        img1.rectangle(shape, outline ="red")
        
        # Display the image created
        return img
    
    def visualize_multi_bbox(self, list_trait_name):

        # creating new Image object
        img_arr = self.img_arr
        img = Image.fromarray(img_arr)
        img1 = ImageDraw.Draw(img)
        
        for trait_name in list_trait_name:
            
            # prepare the bbox for the "trait_name"
            trait_prop = self.clean_trait_region(self.mask[trait_name])
            top, left, bottom, right = trait_prop.bbox

            shape = [(left, top), (right,bottom)]
        
            # create rectangle image 
            img1.rectangle(shape, outline ="red")
        
        # Display the image created
        return img

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
        return img

