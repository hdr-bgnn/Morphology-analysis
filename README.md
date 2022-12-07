# Morphology-analysis

The primary goal of this repository is to produce a presence table (default), create landmarks (optional), visualize landmarks (optional), and extract measurements (optional) from a segmented fish image (see [BGNN-trait-segmentation](https://github.com/hdr-bgnn/BGNN-trait-segmentation)).

Secondarily, this repository provides a framework for creating modularized tools by using classes.

Finally, this repository also provides a way to visualize outputs of the tools and test functionalities using a jupyter notebook. 

This repository is automatically containerized when a new release is published. This allows for easy integration into the [BGNN_Snakemake](https://github.com/hdr-bgnn/BGNN_Snakemake).

This tool can me made more generalizable, but was originally developed for the [Minnows Project](https://github.com/hdr-bgnn/Minnow_Segmented_Traits).

## 1- Input: Segmented Image

The input is the output of the segmentation model, which is a file named basename_segmented.png, where "basename" is the file name for the original image. The segmentation model uses [M. Maruf's segmentation code](https://github.com/hdr-bgnn/BGNN-trait-segmentation/blob/main/Segment_mini/scripts/segmentation_main.py) and is based on a Convolutional Neural Network (CNN; more specifically unet). More information can be found on the [BGNN-trait-segmentation repository](https://github.com/hdr-bgnn/BGNN-trait-segmentation).

The segmented image looks like image below, with traits color-coded and visualized by "blobs".  There are 11 trait classes corresponding to the annotated traits. Here, only 9 are used (alt_fin_ray and caudal_fin_ray are excluded).


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


## 2- Default Tool: Presence

The input of the presence class, or tool, is a semgemented image named "basename_segmented.png" generated by [Virginia Tech](https://github.com/hdr-bgnn/BGNN-trait-segmentation).

The output of the presence tool is a presence table named "basename_presence.json" for each image.

To check for the presence of traits, the tool:

  1. Isolates an individual trait (e.g., isolates the dorsal_fin)
  2. Counts the number of blobs for that trait
  3. Calculates the percentage of the area of the largest blob as a proportion of the area of the total blobs for that trait


## 3- Optional Tools: Landmark, Visualize, Metadata, and Measure

The input for the measure tool is a metadata file named "basename_metadata.json" generated by [Drexel](https://github.com/hdr-bgnn/drexel_metadata/tree/Thibault/gen_metadata_mini).

To create landmarks, visualizations, and extract measurements, the tool:

  1. Isolates an individual trait (e.g., isolates the dorsal_fin)
  2. Removes any small blobs of a trait and fills in gaps between blobs of a trait
  3. Identify and place landmarks
  4. Extract measurements of traits using landmarks (_lm), masks (_m), or a bounding box (_bbox)

The user can specify which method of measurement extraction to use (described more below under *measurements*).

Please create an [issue](https://github.com/hdr-bgnn/Morphology-analysis/issues/new) to suggest an additional landmark or measurement. 


### Landmarks

The landmarks used are shown and described below:

![Fish landmarks](Traits_description/Minnow_Landmarks_v1.png)


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


### Visualize

This tool saves the segmented fish image with landmarks. 

Here is an [example](Test_Data/INHS_FISH_000742_image_lm.png) of a visualization of the landmarks on the segmented image.


### Metadata

This is an input file. The file should be generated by [drexel](https://github.com/hdr-bgnn/drexel_metadata/tree/Thibault/gen_metadata_mini) and named basename_metadata.json.
This file contains information about the rule and scale (pixels per cm) to be used for the **Measure** tool. 

The scale function within this tool outputs if a ruler is found, the scale in pixels, and the unit (cm).

Here is an [example](Test_Data/INHS_FISH_000742.json) of a metadata file.

  
### Measure

The output of the measure tool is a file named basename_measure.json that has measurements (in pixels) for each trait.

The measurements extracted are shown and described below:

![Fish measurment](Traits_description/Minnow_Measurements_v1.png)


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

  
#### Method of Measurement Extraction

Each method of measurement extracted is a separate class, which adds more flexibility. These are described in [Trait_class](Scripts/Traits_class.py)

Since the functions are modular, the method for extracting measurements can be specified:


_landmarks_


These measurement trait classes functions have the suffix *"_lm"* to denote the method of extraction. 
The lengths (in pixels) are calculated as the distance between two landmarks (described in the "Definition" column of the trait description csv).


_bounding box (bbox)_


These trait classes functions have the suffix *"_bbox"* to denote the method of extraction.
The lengths (in pixels) are calculated as the distance of a perpendicular line between the edges (either vertical or horizontal) of the bounding box (bbox).


#### Areas


Areas are calculated as the total pixels in the mask of a trait (e.g., head area is the area of the mask of the head). These are described in the "Definition" column of the [Minnow_Measurements_v1.csv](https://github.com/hdr-bgnn/Morphology-analysis/blob/main/Traits_description/Minnow_Measurements_v1.csv).

_mask_


These trait classes have the suffix *"_m"* to denote the method of extraction.


## 4- Usage

By default Morphology_main.py outputs a presence table. Creating landmarks, visualizing landmarks, and measurement tables are optional outputs. 

The inputs for the tools are:

* segmented image: filename_segmented.png (**required**)
* Metadata: basename_metadata.json (*optional*)

The outputs for the tools are:

* Presence: basename_presence.json (**required**)
* Landmark: basename_landmark.json (*optional*)
* Visualize: basename_lm_image.png (*optional*)
* Measure: basename_morphology.json (*optional*)


The main arguments to run this repository are:
```
Morphology_main.py input_image output_presence 
```

To add optional tools, simply add one or all of the following, where "--" denotes the tool and the second term is the output file:

*landmark*
```
--landmark LANDMARK.json
```

*visualize*
```
--visualize VISUALIZE.png
```

*measure*
```
--measure  MEASURE.json
```


Here is an example using [Test_Data](https://github.com/hdr-bgnn/Morphology-analysis/Test_Data): 
```
cd Morphology-analysis/
./Script/Morphology_main.py --metadata Test_Data/INHS_FISH_000742.json --morphology Test_Data/INHS_FISH_000742_measure.json --landmark Test_Data/INHS_FISH_000742_landmark.json --lm_image Test_Data/INHS_FISH_000742_image_lm.png Test_Data/INHS_FISH_000742_segmented.png Test_Data/INHS_FISH_000742_presence.json
```


If no arguments are given, an error message will say "missing two positional arguments", which are the input file and the output file. Use "-h" to pull up the help file with the full list of arguments. 


## 5- Version control

The repository is containerized each release and is stored on the GitHub registry. The containerized version is called to run the main script, [Morphology_main.py](Scripts/Morphology_main.py). 

The workflow to build the container is defined [here](.github/workflows/Deploy_Morpholgy.yml).   

The Dockerfile definition is [here](Dockerfile).

Pull the latest image: 
```
docker pull ghcr.io/hdr-bgnn/morphology-analysis/morphology:latest 
#singularity pull docker://ghcr.io/hdr-bgnn/morphology-analysis/morphology:latest
```

Run the container: 
```
singularity exec morphology_latest.sif Morphology_main.py  <input_file> <presence.json> --metadata <metadata.json> --morphology <Morphology.json> --landmark <landmark.json> --lm_image <image_lm.png>

# Example
singularity exec morphology_latest.sif Morphology_main.py --metadata Test_Data/INHS_FISH_000742.json --morphology Test_Data/INHS_FISH_000742_measure.json --landmark Test_Data/INHS_FISH_000742_landmark.json --lm_image Test_Data/INHS_FISH_000742_image_lm.png Test_Data/INHS_FISH_000742_segmented.png Test_Data/INHS_FISH_000742_presence.json
```
  
## 6- Play

**Work in Progress (open to improvement and development)**

In development, you can check [this notebook](https://github.com/hdr-bgnn/Morphology-analysis/blob/main/Scripts/Morphology_dev.ipynb)
You will need to use [Morphology_env.yml](https://github.com/hdr-bgnn/Morphology-analysis/blob/main/Scripts/morphology_env.yml) to set up your environment before working (required dependencies). I recommend conda, miniconda as environment manager.

To set up your virtual environment in the OSC:

1. Create an account on the OSC
2. Go to OSC home directory
3. Open a cluster
4. Clone the repository onto your home directory

  ```
  git clone <SSH link>
  ```

5. Navigate to scripts

  ```
  cd Morphology-analysis/Scripts
  ```
  
6. Run conda & create an environment

  ```
  module load miniconda3
  conda info -e #should be on "base"
  conda env create -f morphology_env.yml -n morphology_env
  ```
  
  -f means files to select (which is morphology_env.yml)
  
  -n means to name the virtual environment, which here is "morphology_env"

  Check that the environment was made

  ```
  conda info -e
  ```
  
  Activate the environment 

  ```
  source acitvate morphology_env
  ```
  
  Check that you're on the virtual environment

  ```
  conda info -e #you should be on "morphology_env"
  ```
  
  Once the environment is set up, you do not need to recreate it.
  
7. Launch the jupyter notebook app and set your kernel to "Python Morphology_jupyter".

  Activate the virtual environment kernel for jupyter notebook

  ```
  pip install ipykernel
  python -m ipykernel install --user --name morphlogy_env --display-name "Python (Morphology_jupyter)"
  ```

  Once you set up the kernel for jupyter notebook, you do not need to do it again.


**Launch Jupyter notebook Morphology_dev.ipynb**
  + Use OSC dashboard [On Demand](https://ondemand.osc.edu/pun/sys/dashboard)
  + Tab Interactive Apps
  + Select Jupyter notebook
  + Choose the configuration you want (start with cores:1 Number_hours:1, Node_type:any)
  + Launch
  + Navigate to ~/Morphology-analysis/Scripts/Morphology_dev.ipynb
  + Change kernel to Morphology_jupyter
