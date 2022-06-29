# Morphology-analysis
Extract morphological characteristics from trait segmented fish

The goals of the tool is to extract measurments and landmarks of fish from the segmented fish iamge porduce by [Maruf code]().
It provides a framework with various tools such as class and notebook to help further development.
Another goal is to release working version to in container for easy integration into workflow such as [BGNN_Snakemake]
This tool is a part of a bigger project, find the overview [here]

## 1- Segmented image .png description

The segmented image input looks like this. It is produced using Maruf segementation (semantic) code based on CNN (unet) deeplearning algorithm, more description on the repo. The output is 11 classes (11 trait : 'dorsal_fin', 'adipos_fin', 'caudal_fin, 'anal_fin', 'pelvic_fin', 'pectoral_fin', 'head', 'eye', 'caudal_fin_ray, 'alt_fin_ray', 'trunk') that are color coded.

![segmented fish image](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_segmented.png)

Need the color legend.

When you export this image in python using pillow library (PIL.Image.open(file_name)), the corresponding color coding in RGB is 
{'background': [0, 0, 0],
'dorsal_fin': [254, 0, 0],
'adipos_fin': [0, 254, 0],
'caudal_fin': [0, 0, 254],
'anal_fin': [254, 254, 0],
'pelvic_fin': [0, 254, 254],
'pectoral_fin': [254, 0, 254],
'head': [254, 254, 254],
'eye': [0, 254, 102],
'caudal_fin_ray': [254, 102, 102],
'alt_fin_ray': [254, 102, 204],
'trunk': [0, 124, 124]}

The approach we take is the following :

  1. We isolate each indivual traits
  2. We remove small blob and fill holes
  3. We identify landmarks (defined in section 2-)
  4. We use landmarks and morphological tools (centroid, area...) to assess the measurement (**external characters**)


## 2- Landmarks and measurement

We use the following landmarks and measurement labels and description. If you had more features in the class and codes to extract landmarks or measurement, please update the image description and table.

![Fish landmarks](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Traits_description/Minnows_Landmarks_v1.png)

![Fish measurment](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Traits_description/Minnows_Measurments_v1.png)

**Landmarks Table**

type     |  landmarkNumber  |  terminology                                 |  position                                                      |  anatomicalDefinition  |  codeDefinition
----------|------------------|----------------------------------------------|----------------------------------------------------------------|------------------------|----------------
landmark  |  1               |  Tip of snout                                |  anterior-most (left-most) part of head                        |                        |
landmark  |  2               |  Beginning of the scales at the dorsal side  |  dorsal (top) of head that meets the trunk                     |                        |
landmark  |  3               |  Anterior insertion of the dorsal fin        |  anterior-most (left-most) insertion point of dorsal fin       |                        |
landmark  |  4               |  Posterior insertion of dorsal fin           |  posterior-most (right-most) insertion point of dorsal fin     |                        |
landmark  |  5               |  Dorsal insertion of the caudal fin          |  anterior/dorsal (upper left) insertion point of caudal fin    |                        |
landmark  |  6               |  End of vertebral column                     |  midline of caudal fin                                         |                        |
landmark  |  7               |  Ventral insertion of the caudal fin         |  anterior/ventral (lower left) insertion point of caudal fin   |                        |
landmark  |  8               |  Posterior insertion of the anal fin         |  posterior-most (right-most) insertion point of anal fin       |                        |
landmark  |  9               |  Anterior insertion of the anal fin          |  anterior-most (left-most) insertion point of anal fin         |                        |
landmark  |  10              |  Anterior insertion of the pelvic fin        |  anterior-most (left-most) insertion point of pelvic fin       |                        |
landmark  |  11              |  Superior insertions of the pectoral fin     |  anterior-most (left most) insertion point of pectoral fin     |                        |
landmark  |  12              |  Most dorsal point of operculum              |  posterior-most (right-most) part of head                      |                        |
landmark  |  13              |  Most ventral point of operculum             |  dorsal (lower) part of head that meets the trunk              |                        |
landmark  |  14              |  anterior-most (left-most) part of eye       |  anterior-most (left-most) part of eye                         |                        |
landmark  |  15              |  posterior-most (right-most) part of eye     |  posterior-most (right-most) part of eye                       |                        |
  
**Measurement Table**  
trait                            |  abbreviation  |  type      |  anatomicalDefinition                                                                                                                          |  codeDefinition
----------------------------------|----------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------|----------------
standard length                   |   SL           |  distance  |  length from the tip of the snout to the posterior-most part of trunk that meets the caudal fin                                                |
eye area                          |   EA           |  area      |  area of the eye                                                                                                                               |
head area, triangle               |   HAt          |  area      |  area of head as outlined by three points: tip of snout (landmark #1), back of head (landmark #2), and ventral portion of head (landmark #13)  |
head area, pixels                 |   HAp          |  area      |  area of head based on number of pixels                                                                                                        |
eye area to head area             |   EHA          |  area      |  ratio of eye area to head area                                                                                                                |
head-to-caudal length             |   HCL          |  distance  |  length along the dorsal side (top) from the back of the head (landmark #2) to the end of the peduncle (landmark #5)                           |
eye diameter                      |  ED            |  distance  |  length across the eye along the anterior-posterior (left-right) axis (landmarks #14 & #15)                                                    |
head length                       |  HL            |  distance  |  length from the anterior-most (left-most) part of the head (landmark #1) to the posterior-most (right-most) part of the head (landmark #12)   |
head depth                        |  HD            |  distance  |  length from the dorsal-most (top) part of the head (landmark #2) to the ventral-most (bottom) part of the head (landmark #13)                 |
snout length or preorbital depth  |  pOD           |  distance  |  length from the anterior-most (left-most) part of the eye (landmark #14) to the anterior-most (left-most)part of the head (landmark #1)       |
  
## 3- Class description

We create a class to add more fexibility and give a frame work for further developement. Here is a short description of the class "Trait_class", couples functionality and usage. The best way understand it is to play with the class using the Notebook.

1. Class Overview
+ Class Name : Trait_class
+ Location : Trait_class.py
+ Description : This class create an object "segmented_image" from [segmented_image.png](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Scripts/test_images/INHS_FISH_000742_segmented.png). Upon the initialization (creation of the object), the image.png is imported converted and is split in several channel corresponding to the traits (trunk, dorsal fin...) in the form of dictionnary with key = trait  and value a mask. Then multiple function will extract information on individual channel.

### Usage and main fucntion: 
2. Quick start
Create a segmented image object
```
import Trait_class as tc 
img_seg = tc.segmented_image("image_segmented.png")
```
3. Main functions:
 + img_seg.get_channels_mask() : Create a dictionnary key = trait, value = mask for the trait
 + img_seg.get_presence_matrix() : Create presence matrix
 + img_seg.all_landmark() : found the landmarks
 + img_seg.all_measure() : calculate the measurment

## 4- Input and Output
The main script is Morphology_main.py The usage is python Morphology_main.py  input_file.png metadata.json measure.json landmark.json presence.json image_lm.png

 + input_file.png : segmented fish image generated by [Maruf code](), [example here](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_segmented.png)
 + metadata.json : generated by [drexel]() [example here](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742.json)
 + measure.json : dictionnary, key = measure label, value = calculated value [example](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_measure.json)
 + landmark.json : dictionnary, key = landmark label, value = calculated value [example](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_landmark.json)
 + presence.json : nested dictionnaries, {key_1 = trait_name { key_2 = "number", value_2 = number of blob, key_3 = "percent", value percentage of the biggest blob}} [example](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_presence.json)
 + image_lm.png : original segmented fish image superimposed with landmark position and label [example here](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Test_Data/INHS_FISH_000742_image_lm.png)

## 5- Notebook to play
In development, you can check [this notebook](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Scripts/Morphology_dev.ipynb)
You will need to use [Morphology_env.yml](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Scripts/morphology_env.yml) to set up your environment before working (required dependencies). I recommend conda, miniconda as environment manager.


## 6-Container, usage and release

We use github action to create a container what run the main script [Morphology_main.py](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Scripts/Morphology_main.py). 
  1. The workflow to build the container is defined [here](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/.github/workflows/Deploy_Morpholgy.yml).   
  2. The Dockerfile definition is [here](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Dockerfile)
  3. Pull command : docker pull ghcr.io/thibaulttabarin/morphology-analysis/morphology:0.0.2 or singularity pull My_morphology_name.sif
  4. To access the instruction Run : "singularity run My_morphology_name.sif" or 
  5. Usage : singularity exec My_morphology_name.sif Morphology_main.py  <input_file> <metadata.json> <measure.json> <landmark.json> <presence.json> <image_lm.png>
