# Morphology-analysis
Extract morphological characteristics from trait segmented fish

The goals of the tool is to extract measurments and landmarks of fish from the segmented fish iamge porduce by [Maruf code]().
It provides a framework with various tools such as class and notebook to help further development.
Another goal is to release working version to in container for easy integration into workflow such as [BGNN_Snakemake]
This tool is a part of a bigger project, find the overview [here]

## 1- Segmented image .png description

The segmented image input looks like this. It is produced using Maruf segementation (semantic) code based on CNN (unet) deeplearning algorithm, more description on the repo. The output is 11 classes (11 trait : 'dorsal_fin', 'adipos_fin', 'caudal_fin, 'anal_fin', 'pelvic_fin', 'pectoral_fin', 'head', 'eye', 'caudal_fin_ray, 'alt_fin_ray', 'trunk') that are color coded.

![segmented fish image](https://github.com/thibaulttabarin/Morphology-analysis/blob/main/Scripts/test_images/INHS_FISH_000742_segmented.png)

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
  
## 3- Class description

## 4- Notebook to play

## 5-Container, usage and release
