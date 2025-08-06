# Create Cross Validation Groups


### Development Information ###

```
Date Created: 22 July 2020
Last Update: 26 July 2021 by Amirali
Developer: Colin Chen
Version: 1.1
```

**Before running any experiment to be sure you are using the latest commits of all modules run the following script:**
```
(cd /projects/ovcare/classification/singularity_modules ; ./update_modules.sh --bcgsc-pass your/bcgsc/path)
```

## Usage

```
usage: app.py [-h] {from-experiment-manifest,from-arguments} ...

Generates training, validation and testing splits for cross validation given a group file. Example: suppose a group file has 3 groups 1, 2, 3. Then this component will generate a new group file where

1) 1 and 2 are combined into a training group, and 3 is spit into a validation group and a test group
2) 2 and 3 are combined into a training group, and 1 is spit into a validation group and a test group
3) 1 and 3 are combined into a training group, and 2 is spit into a validation group and a test group

The patient_groups.json file uses Mitch's format for groups and is a json file with the format

{
    "chunks": [
        {
            "id": int,
            "imgs": list of paths to patches
        },
        ...
    ]
}

The component also produces counts for the number of patches, slides and patients for each category (see below) like the below:

|| Binary T/N counts                    || Other || Tumor || Total ||
| 1 2 train 3 eval - training patches   | 6036   | 6036   | 12072  |
| 1 2 train 3 eval - validation patches | 99     | 794    | 893    |
| 1 2 train 3 eval - testing patches    | 2919   | 2224   | 5143   |
| 1 3 train 2 eval - training patches   | 6036   | 6036   | 12072  |
...

Categories are:
 (1) if the --is_binary flag is selected, then categories=('Tumor', 'Other') where 'Tumor' is any patch annotated as 'Tumor' and 'Other' is any patch with annotated as 'Other', 'MucinousBorderlineTumor', 'Necrosis' or 'Stroma'
 (2) if the --is_binary flag is not selected, then categories=subtype (i.e. CC, EC, MC, LGSC, HGSC)

positional arguments:
  {from-experiment-manifest,from-arguments}
                        Choose whether to use arguments from experiment manifest or from commandline
    from-experiment-manifest
                        Use experiment manifest

    from-arguments      Use arguments

optional arguments:
  -h, --help            show this help message and exit

usage: app.py from-experiment-manifest [-h] [--component_id COMPONENT_ID]
                                       experiment_manifest_location

positional arguments:
  experiment_manifest_location

optional arguments:
  -h, --help            show this help message and exit

  --component_id COMPONENT_ID

usage: app.py from-arguments [-h] [--seed SEED]
                             [--n_train_groups N_TRAIN_GROUPS] [--is_binary]
                             [--subtypes SUBTYPES [SUBTYPES ...]]
                             [--patch_pattern PATCH_PATTERN]
                             --group_file_location GROUP_FILE_LOCATION
                             [--split_file_prefix SPLIT_FILE_PREFIX]
                             --split_location SPLIT_LOCATION
                             {use-manifest,use-origin} ...

positional arguments:
  {use-manifest,use-origin}
                        Specify how to define patient ID and slide ID:
                            1. use-manifest 2. origin
    use-manifest        Use manifest file to locate slides.
                            a CSV file with minimum of 4 column and maximum of 6 columns. The name of columns
                            should be among ['origin', 'patient_id', 'slide_id', 'slide_path', 'annotation_path', 'subtype'].
                            origin, slide_id, patient_id must be one of the columns.

    use-origin          Use origin for detecting patient ID and slide ID.
                            NOTE: It only works for German, OVCARE, and TCGA.

optional arguments:
  -h, --help            show this help message and exit

  --seed SEED           Seed for random shuffle.
                         (default: 256)

  --n_train_groups N_TRAIN_GROUPS
                        Number of groups from group JSON file to combine together into one training group.
                         (default: 2)

  --is_binary           Whether we want to count patches by Tumor/Normal (true) or by subtype (false)
                         (default: False)

  --subtypes SUBTYPES [SUBTYPES ...]
                        Space separated words describing subtype=groupping pairs for this study. Example: if doing one-vs-rest on the subtypes MMRD vs P53ABN, P53WT and POLE then the input should be 'MMRD=0 P53ABN=1 P53WT=1 POLE=1'
                         (default: {'MMRD': 0, 'P53ABN': 1, 'P53WT': 2, 'POLE': 3})

  --patch_pattern PATCH_PATTERN
                        '/' separated words describing the directory structure of the patch paths. The words are ('annotation', 'subtype', 'slide', 'patch_size', 'magnification'). A non-multiscale patch can be contained in a directory /path/to/patch/rootdir/Tumor/MMRD/VOA-1234/1_2.png so its patch_pattern is annotation/subtype/slide. A multiscale patch can be contained in a directory /path/to/patch/rootdir/Stroma/P53ABN/VOA-1234/10/3_400.png so its patch pattern is annotation/subtype/slide/magnification
                         (default: annotation/subtype/slide)

  --group_file_location GROUP_FILE_LOCATION
                        Path to group JSON file to create cross validation groups with.
                         (default: None)

  --split_file_prefix SPLIT_FILE_PREFIX
                        The prefix for the name of the generated split files.
                         (default: split)

  --split_location SPLIT_LOCATION
                        Path to directory to save the cross validation split files.
                         (default: None)

usage: app.py from-arguments use-origin [-h]
                                        [--dataset_origin DATASET_ORIGIN [DATASET_ORIGIN ...]]

optional arguments:
  -h, --help            show this help message and exit

  --dataset_origin DATASET_ORIGIN [DATASET_ORIGIN ...]
                        List of the origins of the slide dataset the patches are generated from. Should be from ('ovcare', 'tcga', 'german', 'other'). (For multiple origins, works for TCGA+ovcare. Mix of Other origins must be tested.)
                         (default: ['ovcare'])

usage: app.py from-arguments use-manifest [-h] --manifest_location
                                          MANIFEST_LOCATION

optional arguments:
  -h, --help            show this help message and exit

  --manifest_location MANIFEST_LOCATION
                        Path to manifest CSV file.
                         (default: None)

```

