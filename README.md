# PDAC-PathAI-MolecularClassifier

This codebase is associated with the paper titled "A Deep Learning Approach for the Identification of the Molecular Subtypes of Pancreatic Ductal Adenocarcinoma Based on Whole-Slide Pathology Images" (AJPA-D-24-00272R1) published in The American Journal of Pathology.

## Pipeline Overview

To run the pipeline, you need to execute the following modules in order:

1. **singularity_extract_annotated_patches**
   - This module extracts annotated patches from whole-slide pathology images. It processes the images to identify and extract regions of interest based on provided annotations.

2. **singularity_create_groups**
   - This module groups the extracted patches into different categories or classes based on predefined criteria. It helps in organizing the data for subsequent processing steps.

3. **singularity_create_cross_validation_splits**
   - This module creates cross-validation splits from the grouped patches. It divides the data into training and validation sets to facilitate model training and evaluation.

4. **singularity_train**
   - This module trains the deep learning model using the training data. It involves setting up the model architecture, defining the training parameters, and running the training process.

5. **singularity_auto_annotate**
   - This module automatically annotates new whole-slide pathology images using the trained model. It predicts the molecular subtypes of pancreatic ductal adenocarcinoma for the input images.

## Creating Singularity Image

To create a Singularity image using the provided `.def` file, follow these steps:

1. Open a terminal.
2. Navigate to the directory containing the `.def` file.
3. Run the following command to build the Singularity image:

   ```sh
   singularity build <image_name>.sif <definition_file>.def# PDAC-PathAI-MolecularClassifier
