# Morphology-analysis
Extract morphological characteristics from image of fish trait segmentation.


The goals of the tool is to extract presence-absence table, measurements and landmarks of fish from the segmented fish image produced by M. Maruf.
It provides a framework for creating modularized tools by using classes and jupyter notebook to visualize and test functionalities. 
The tool is automatically containerized when a new release is published. It provides a validated version for easy integration into the [BGNN_Snakemake](https://github.com/hdr-bgnn/BGNN_Snakemake).
This tool can me made more generalizable but it has been developped for the [Minnows Project](https://github.com/hdr-bgnn/minnowTraits).


## 1- Segmented image .png description

The segmented image input looks like image below, with traits color coded and identified by "blobs". The segmentation model uses [M. Maruf's segmentation code](https://github.com/hdr-bgnn/BGNN-trait-segmentation/blob/main/Segment_mini/scripts/segmentation_main.py), and is based on a Convolutional Neural Network (CNN; more specifically unet). You can find more information on the [BGNN-trait-segmentation repository](https://github.com/hdr-bgnn/BGNN-trait-segmentation).  The output is 11 classes (traits) that are color coded. We are only using 9 of them, and are excluding alt_fin_ray and caudal_fin_ray.


![segmented fish image](Test_Data/INHS_FISH_000742_segmented.png)
![Color legend](Traits_description/trait_legend.png)

When you export this image in python using pillow library (PIL.Image.open(file_name)), the corresponding color coding in RGB is:
* 'background': [0, 0, 0],
* 'dorsal_fin': [254, 0, 0],
* 'adipos_fin': [0, 254, 0],
* 'caudal_fin': [0, 0, 254],
* 'anal_fin': [254, 254, 0],
* 'pelvic_fin': [0, 254, 254],
* 'pectoral_fin': [254, 0, 254],
* 'head': [254, 254, 254],
* 'eye': [0, 254, 102],
* 'caudal_fin_ray': [254, 102, 102],
* 'alt_fin_ray': [254, 102, 204],
* 'trunk': [0, 124, 124]

The approach that we use for extracting traits is the following:


  1. Isolate indivual traits (e.g., isolate the dorsal_fin)
  2. Remove small blobs and fill in gaps within each trait
  3. Identify landmarks (defined in section 2)
  4. Use landmarks and morphological tools (centroid, area, etc.) to extract the measurements (**external characters**)



## 2- Landmarks and measurements

We use the following descriptions and labels for landmarks and measurements. If you had more features in the class and codes to extract landmarks or measurement, please create an issue or make a pull request to update the image description and corresponding table.


![Fish landmarks](Traits_description/Minnow_Landmarks_v1.png)

![Fish measurment](Traits_description/Minnow_Measurements_v1.png)

**[Landmarks Table](Traits_description/Minnow_Landmarks_v1.csv)**

  Landmark_Number  |  Definition  |  codeDefinition  
----------|------------------|----------------------------------------------
  1 |  Tip of snout, which is the anterior-most part of head  |  Left-most point of the head mask defined by left boundary of the bbox  
  2 |  Beginning of the scales at the dorsal side, where the head meets the trunk  |  Top-most point of the head mask defined by top boundary of the bbox  
  3 |  Anterior insertion of the dorsal fin  |  Left-most point of the dorsal fin mask defined by left boundary of the bbox  
  4 |  Posterior insertion of dorsal fin  |  Furthest bottom point of the dorsal fin defined by bottom boundary of the bbox  
  5 |  Dorsal insertion of the caudal fin  |  Left-most point of the upper half of the caudal fin mask (split through the midline) using the bbox  
  6 |  End of vertebral column, at the midline of the caudal fin  |  Right-most part of the trunk mask defined by the right boundary of the bbox  
  7 |  Ventral insertion of the caudal fin  |  Left-most point of the lower half of the caudal fin mask (split through the midline) using the bbox  
  8 |  Posterior insertion of the anal fin  |  Top-most point of the anal fin mask defined by top boundary of the bbox  
  9 |  Anterior insertion of the anal fin  |  Left-most point of the anal fin mask defined by left boundary of the bbox  
  10 |  Anterior insertion of the pelvic fin  |  Left-most point of the pelvic fin mask defined by left boundary of the bbox  
  11 |  Anterior insertion of the pectoral fin  |  Left-most point of the pectoral fin mask defined by left boundary of the bbox  
  12 |  Most dorsal point of operculum, which is the posterior-most part of the head  |  Right-most part of the head mask defined by the right boundary of the bbox  
  13 |  Most ventral point of operculum, where the head meets the trunk  |  Furthest bottom point of the head mask defined by bottom boundary of the bbox  
  14 |  Anterior-most (left-most) part of eye  |  Left-most point of the eye mask defined by left boundary of the bbox  
  15 |  Posterior-most (right-most) part of eye  |  Right-most part of the eye mask defined by the right boundary of the bbox  
  16 |  Dorsal-most (upper) part of eye)  |  Top-most point of the eye mask defined by top boundary of the bbox  
  17 |  Ventral-most (lower) part of eye  |  Furthest bottom point of the eye mask defined by bottom boundary of the bbox  
  18 |  Center (centroid) of eye  |  Center of the eye mask  
  
**[Measurement Table](Traits_description/Minnow_Measurements_v1.csv)**  

  Type  |  Measurement  |  Abbreviation  |  Definition  
--------------------|----------------|------------|-----------------------------------------------
  distance  |  standard length using landmarks  |  SL_lm  |  length from the tip of the snout to the posterior-most part of trunk that meets the caudal fin (length from #1 to #6)	
  distance  |  standard length using bounding box  |  SL_bbox  |  length from the tip of the snout to the posterior-most part of trunk that meets the caudal fin (distance between the left-right sides of a bounding box around the head+eye and trunk)  
  area      |  eye area using pixels of mask  |  EA_m  |  area of the eye region (area of the eye based on the mask that segments the eye)  
  area      |  head area using pixels of mask  |  HA_m  |  area of the head region (area of the head based on the mask that segments the head, including the eye)  
  distance  |  head length using landmarks  |  HL_lm  |  length from the anterior-most part of the head to the posterior-most part of the head (length from #1 to #12)  
  distance  |  head length using bounding box  |  HL_bbox  |  length from the anterior-most part of the head to the posterior-most part of the head (distance between the left-right sides of a bounding box around the head+eye)  
  distance  |  preorbital depth using landmarks  |  pOD_lm  |  length from the anterior-most part of the eye to the anterior-most part of the head (length from #1 to #14)  
  distance  |  preorbital depth using bounding box  |  pOD_bbox  |  length from the anterior-most part of the eye to the anterior-most part of the head (distance between the left edge of the head bounding box and the eye bounding box)  
  distance  |  head depth through midline of the eye  |  HH_lm  |  length from the dorsal-most (top) part of the head to the ventral-most (bottom) part of the head through the midline of the eye (length from the dorsal-most (top) part of the head to the ventral-most (bottom) part of the head through landmark #18)  
  distance  |  eye diameter using landmarks  |  ED_lm  |  length across the eye along the anterior-posterior (left-right) axis (length from #14 to #15)  
  distance  |  eye diameter using landmarks  |  ED_bbox  |  length across the eye along the anterior-posterior (left-right) axis (distance between the left-right sides of a bounding box around the eye)  
  angle  |  fish angle using landmarks  |  Fa_lm  |  angle of the tilt of the fish from horizontal (angle between the SL_lm and and the horizontal line of the image)  
  angle  |  fish angle using PCA  |  Fa_pca  |  angle of the tilt of the fish from horizontal (angle between the pca through the midline of the fish mask and the horizontal line of the image)  
  
## 3- Extract trait information : Classes

We created classes to add more fexibility, which can be helpfull to generalize to other projects. [Trait_class](Scripts/Traits_class.py)

*Classes Overview*
+ Classes Name : Segmented_image, Measure_morphology, Visualization_morphology
+ Location : Trait_class.py
+ Description : 
  - Segmented_image class : This class creates an object "segmented_image" from [segmented_image.png](Scripts/test_images/INHS_FISH_000742_segmented.png). The object "segmented_image" imported the image.png and split into channels corresponding to the traits (trunk, dorsal_fin, etc.) in the form of a dictionary with key = trait  and value a mask. Then multiple functions will be applied to extract basic information on individual channel and on the whole fish.
    - Two functions of interest:
      + function get_fish_angle_pca : angle of the fish from principal component
      + function get_presence_matrix : precense and absence matrix with number of blob and percentage (by area) of the major blob per traits
  - Measure_morphology class : This class inherit from Segmented_image class. It will use individual trait information to measure dimension of interest on the fish [see Table](Traits_description/Minnow_Measurements_v1.csv) and position landmark. There are 3 main sections, (1) find landmarks, (2) measure using landmark, (3) measure using bbox (bounding box). 
    - Few functions of interest:
      + function all_landmark : find the landmarks defined in landmarks table
      + function all_measure_using_lm : measure dimension of interest using landmarks
      + fucntion all_measure_using_bbox : measure dimension of interest using bounding box

## 4- the Main function

The main function uses classes functionalities to collect information and wraps everything in final main .
The outputs are a series of .json files and .png file.
    + presence_matrix.json
    + measurements.json
    + landmark.json
    + landmark_image.png

#### 1) Using the landmarks
These trait classes functions have the suffix "_lm" to denote the method of extraction. 

The lengths (in pixels) are calculated as the distance between two landmarks (described in the "Definition" column of the trait description csvs).

#### 2) Using the bbox (bounding box)
These trait classes functions have the suffix "_bbox" to denote the method of extraction.

The lengths (in pixels) are calculated as the distance of a perpindicular line between the edges (either vertical or horizontal) of the bbox.

#### 3) Using the mask
These trait classes have the suffix "_m" to denote the method of extraction.

These areas are calculated as the total pixels in the mask of a trait (e.g., head area is the area of the mask of the head). These are described in the "Definition" column of the <a href="https://github.com/hdr-bgnn/Morphology-analysis/blob/main/Traits_description/Minnow_Measurements_v1.csv">Minnow_Measurements_v1.csv</a>.

### Usage and main function: 

*Quick start*
Create a segmented image object
```
import Trait_class as tc 
img_seg = tc.segmented_image("image_segmented.png")
```
*Main functions*:
 + img_seg.get_channels_mask() : Create a dictionnary key = trait, value = mask for the trait
 + img_seg.get_presence_matrix() : Create presence matrix
 + img_seg.all_landmark() : found the landmarks
 + img_seg.all_measure() : calculate the measurment

## 4- Input and Output

To use Morphology_main.py., simply fill in: Morphology_main.py input_file.png metadata.json measure.json landmark.json presence.json image_lm.png

As an example, the code below tests the data in fs/ess/PAS2136/Test_Data/ on the OSC
```
Morphology_main.py Test_Data/INHS_FISH_18609_segmented.png Test_Data/INHS_FISH_18609.js
on Test_Data/INHS_FISH_18609_measure.json Test_Data/INHS_FISH_18609_landmark.json Test_Data/INHS_FISH_18609_presence.json Test_Data/INHS_FISH_18609_image_lm.png
```

 + input_file.png : segmented fish image generated by [Maruf code](https://github.com/hdr-bgnn/BGNN-trait-segmentation/tree/main/Segment_mini), [example here](https://github.com/hdr-bgnn/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_segmented.png)
 + metadata.json : generated by [drexel](https://github.com/hdr-bgnn/drexel_metadata/tree/Thibault/gen_metadata_mini) [example here](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742.json)
 + measure.json : dictionnary, key = measure label, value = calculated value [example](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_measure.json)
 + landmark.json : dictionnary, key = landmark label, value = calculated value [example](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_landmark.json)
 + presence.json : nested dictionnaries, {key_1 = trait_name { key_2 = "number", value_2 = number of blob, key_3 = "percent", value percentage of the biggest blob}} [example](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_presence.json)
 + image_lm.png : original segmented fish image superimposed with landmark position and label [example here](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_image_lm.png)

## 5- Notebook to play

In development, you can check [this notebook](https://github.com/hdr-bgnn/Morphology-analysis/blob/main/Scripts/Morphology_dev.ipynb)
You will need to use [Morphology_env.yml](https://github.com/hdr-bgnn/Morphology-analysis/blob/main/Scripts/morphology_env.yml) to set up your environment before working (required dependencies). I recommend conda, miniconda as environment manager.

To set up your virtual environment in the OSC:

#go to OSC home directory
#open a cluster

#clone the repository onto your home directory
```git clone <SSH link>```

#navigate to scripts
```cd Morphology-analysis/Scripts```

#use conda
```
module load miniconda3
conda info -e #see what environments you have; you should be on "base"
conda env create -f morphology_env.yml -n morphology_env
```
-f means files to select (which is morphology_env.yml)
-n means to name the virtual environment, which here is "morphology_env"

#check that environment was made
```conda info -e```

#now you have a virtual environment!
#to activate it:
```
source acitvate morphology_env
#check that you're on the virtual environment
conda info -e #you should be on "morphology_env"
```
Once the environment is set up, you do not need to recreate it.

Launch the jupyter notebook app and set your kernel to "Python Morphology_jupyter".
```
#activate the virtual environment kernel for jupyter notebook
pip install ipykernel
python -m ipykernel install --user --name morphlogy_env --display-name "Python (Morphology_jupyter)"
```
Once you set up the kernel for jupyter notebook, you do not need to do it again.
**Launch Jupyter notebook Morphology_dev.ipynb**
  + Use OSC dashboard [onthedemand](https://ondemand.osc.edu/pun/sys/dashboard)
  + Tab Interactive Apps
  + Select Jupyter notebook
  + Choose the configuration you want (start with cores:1 Number_hours:1, Node_type:any)
  + Launch
  + Navigate to ~/Morphology-analysis/Scripts/Morphology_dev.ipynb
  + Change kernel to Morphology_jupyter


## 6-Container, usage and release

We use github action to create a container what run the main script [Morphology_main.py](https://github.com/hdr-bgnn/Morphology-analysis/blob/main/Scripts/Morphology_main.py). 
  1. The workflow to build the container is defined [here](https://github.com/hdr-bgnn/Morphology-analysis/blob/main/.github/workflows/Deploy_Morpholgy.yml).   
  2. The Dockerfile definition is [here](https://github.com/hdr-bgnn/Morphology-analysis/blob/main/Dockerfile)
  3. Pull command : 
  ```
  docker pull ghcr.io/hdr-bgnn/morphology-analysis/morphology:latest
  #or 
  singularity pull My_morphology_name.sif docker://ghcr.io/hdr-bgnn/morphology-analysis/morphology:latest
  ```
  4. To access the instruction Run : "
  ```
  singularity run My_morphology_name.sif
  ```
  5. Usage : 
  ```
  singularity exec My_morphology_name.sif Morphology_main.py  <input_file> <metadata.json> <measure.json> <landmark.json> <presence.json> <image_lm.png>
  # test with
  singularity exec My_morphology_name.sif Morphology_main.py Test_Data/INHS_FISH_18609_segmented.png Test_Data/INHS_FISH_18609.json   Test_Data/INHS_FISH_18609_measure.json Test_Data/INHS_FISH_18609_landmark.json Test_Data/INHS_FISH_18609_presence.json Test_Data/INHS_FISH_18609_image_lm.png
  ```
## 7- Development tricks

If you want to test new version of Morphology_main.py (upudated version on your local computer). You can use the container by bind the local folder (here it is in Scripts/) containing the updated version of Morphology_main.py and /pipeline/Morphology is where Morphology_main.py is expected to be in the container. Example:
```
singularity exec --bind Scripts/:/pipeline/Morphology morpho.sif Morphology_main.py Test_Data/INHS_FISH_18609_segmented.png Test_Data/INHS_FISH_18609.json Test_Data/INHS_FISH_18609_measure.json Test_Data/INHS_FISH_18609_landmark.json Test_Data/INHS_FISH_18609_presence.json Test_Data/INHS_FISH_18609_image_lm.png

```
