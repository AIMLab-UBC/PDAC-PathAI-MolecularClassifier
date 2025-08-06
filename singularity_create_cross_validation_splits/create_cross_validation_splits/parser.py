import argparse

from submodule_utils import (BALANCE_PATCHES_OPTIONS, DATASET_ORIGINS,
        PATCH_PATTERN_WORDS, set_random_seed, DEAFULT_SEED)
from submodule_utils.manifest.arguments import manifest_arguments
from submodule_utils.arguments import (
        AIMArgumentParser,
        dir_path, file_path, dataset_origin, balance_patches_options,
        str_kv, int_kv, subtype_kv, make_dict,
        ParseKVToDictAction, CustomHelpFormatter)
from create_cross_validation_splits import *

description="""Generates training, validation and testing splits for cross validation given a group file. Example: suppose a group file has 3 groups 1, 2, 3. Then this component will generate a new group file where

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
"""
epilog="""
"""

@manifest_arguments(description=description, epilog=epilog,
        default_component_id=default_component_id)
def create_parser(parser):
    parser.add_argument("--seed", type=int, default=DEAFULT_SEED,
            help="Seed for random shuffle.")

    parser.add_argument("--n_train_groups", type=int, default=default_n_train_groups,
            help='Number of groups from group JSON file to combine together into one training group.')

    parser.add_argument("--is_binary", action='store_true',
            help='Whether we want to count patches by Tumor/Normal (true) or by subtype (false)')

    parser.add_argument("--subtypes", nargs='+', type=subtype_kv,
            action=ParseKVToDictAction, default=default_subtypes,
            help="Space separated words describing subtype=groupping pairs for this study. "
            "Example: if doing one-vs-rest on the subtypes MMRD vs P53ABN, P53WT and POLE then "
            "the input should be 'MMRD=0 P53ABN=1 P53WT=1 POLE=1'")

    parser.add_argument("--patch_pattern", type=str,
            default=default_patch_pattern,
            help="'/' separated words describing the directory structure of the "
            f"patch paths. The words are {tuple(PATCH_PATTERN_WORDS)}. "
            "A non-multiscale patch can be contained in a directory "
            "/path/to/patch/rootdir/Tumor/MMRD/VOA-1234/1_2.png so its patch_pattern is "
            "annotation/subtype/slide. A multiscale patch can be contained in a "
            "directory /path/to/patch/rootdir/Stroma/P53ABN/VOA-1234/10/3_400.png so "
            "its patch pattern is annotation/subtype/slide/magnification")

    parser.add_argument("--group_file_location", type=file_path, required=True,
            help="Path to group JSON file to create cross validation groups with.")

    parser.add_argument("--split_file_prefix", type=str,
            default=default_split_file_prefix,
            help="The prefix for the name of the generated split files.")

    parser.add_argument("--split_location", type=dir_path, required=True,
            help="Path to directory to save the cross validation split files.")

    help_subparsers_define = """Specify how to define patient ID and slide ID:
    1. use-manifest 2. origin"""
    subparsers_define = parser.add_subparsers(dest="define_method",
            required=True,
            parser_class=AIMArgumentParser,
            help=help_subparsers_define)

    help_manifest_ = """Use manifest file to locate slides.
    a CSV file with minimum of 4 column and maximum of 6 columns. The name of columns
    should be among ['origin', 'patient_id', 'slide_id', 'slide_path', 'annotation_path', 'subtype'].
    origin, slide_id, patient_id must be one of the columns."""

    parser_manifest_ = subparsers_define.add_parser("use-manifest",
            help=help_manifest_)
    parser_manifest_.add_argument("--manifest_location", type=file_path, required=True,
            help="Path to manifest CSV file.")

    help_origin = """Use origin for detecting patient ID and slide ID.
    NOTE: It only works for German, OVCARE, and TCGA."""

    parser_origin = subparsers_define.add_parser("use-origin",
            help=help_origin)
    parser_origin.add_argument('--dataset_origin', type=dataset_origin, nargs='+',
            default=default_dataset_origin,
            help="List of the origins of the slide dataset the patches are generated from. "
            f"Should be from {tuple(DATASET_ORIGINS)}. "
            "(For multiple origins, works for TCGA+ovcare. Mix of Other origins must be tested.)")

def get_args():
        parser = create_parser()
        args = parser.get_args()
        set_random_seed(args.seed)
        return args
