import re
import os
import enum
import glob
import json
import random
import argparse
import itertools
import sys
import os.path

import numpy as np

import submodule_utils as utils
from submodule_utils.mixins import OutputMixin
from submodule_utils.metadata.group import (
        convert_yiping_to_mitch_format,
        convert_mitch_to_yiping_format)

default_component_id = 'create_cross_validation_splits'
default_n_train_groups = 2
default_subtypes = {'MMRD':0, 'P53ABN': 1, 'P53WT': 2, 'POLE': 3}
default_dataset_origin = ['ovcare']
default_patch_pattern = 'annotation/subtype/slide'
default_group_file_location = '/projects/ovcare/classification/cchen/ml/local_ec_100/patient_groups.json'
default_split_file_prefix = 'split'
default_split_location = '/projects/ovcare/classification/cchen/ml/local_ec_100/splits'

class CrossValidationGroupsCreator(OutputMixin):
    """Class that generates split files from groups where each split contains unique patients

    Attributes
    ----------
    seed : int
        seed for random shuffle

    n_train_groups : int
        Number of groups to merge together into one training group

    is_binary : bool
        Whether we want to categorize patches by the Tumor/Normal category (true) or by the subtype category (false)

    dataset_origin : list of str
        The origins of the slide dataset the patches are generated from. One of DATASET_ORIGINS

    CategoryEnum : enum.Enum
        The enum representing the categories and is one of (SubtypeEnum, BinaryEnum)

    group_file_location : str
        Group file to create cross validation groups with

    split_file_prefix : str
        The prefix for the name of the generated split files

    split_location : str
        The directory to save the cross validation split files

    patch_pattern : dict
        Dictionary describing the directory structure of the patch paths.
        A non-multiscale patch can be contained in a directory /path/to/patch/rootdir/Tumor/MMRD/VOA-1234/1_2.png so its patch_pattern is annotation/subtype/slide.
        A multiscale patch can be contained in a directory /path/to/patch/rootdir/Stroma/P53ABN/VOA-1234/10/3_400.png so its patch pattern is annotation/subtype/slide/magnification
    """
    @property
    def should_use_manifest(self):
        return self.define_method == 'use-manifest'

    @property
    def should_use_origin(self):
        return self.define_method == 'use-origin'

    def __init__(self, config):
        """Initialize create cross validation component.

        Arguments
        ---------
        config : argparse.Namespace
            The args passed by user
        """
        self.seed = config.seed
        self.n_train_groups = config.n_train_groups
        self.define_method = config.define_method
        self.is_binary = config.is_binary
        self.CategoryEnum = utils.create_category_enum(self.is_binary, config.subtypes)
        self.group_file_location = config.group_file_location
        self.split_file_prefix = config.split_file_prefix
        self.split_location = config.split_location
        self.patch_pattern = utils.create_patch_pattern(config.patch_pattern)

        if self.should_use_manifest:
            self.manifest = utils.read_manifest(config.manifest_location)
        elif self.should_use_origin:
            self.dataset_origin = config.dataset_origin
        else:
            raise NotImplementedError(f"Define method {self.define_method} is not implemented")



    def create_val_test_splits(self, eval_patches):
        """Function to create validation and test splits based on evaluation ids
        This function ensures unique patches in validation and testing sets

        Parameters
        ----------
        eval_patches : list
            List of patch ids in evaludation set

        Returns
        -------
        val_ids : list
            List of patch ids in validation set

        test_ids : list
            List of patch ids in testing set
        """
        subtype_names = [s.name for s in self.CategoryEnum]

        if self.should_use_origin:
            subtype_patient_slide_patch = utils.create_subtype_patient_slide_patch_dict(
                    eval_patches, self.patch_pattern, self.CategoryEnum,
                    is_binary=self.is_binary, dataset_origin=self.dataset_origin)
        else:
            subtype_patient_slide_patch = utils.create_subtype_patient_slide_patch_dict_manifest(
                    eval_patches, self.patch_pattern, self.CategoryEnum,
                    self.manifest, is_binary=self.is_binary)

        val_paths = []
        test_paths = []
        for subtype in subtype_names:
            try:
                patient_slide_patch = subtype_patient_slide_patch[subtype]
            except KeyError as e:
                if self.is_binary:
                    raise Exception(f'There are no {e} patches')
                else:
                    print(f'Warning: an eval set has no {e} patches')
                    continue
            patients = list(patient_slide_patch.keys())
            patient_idx = len(patients) // 2
            for patient_in_val in patients[:patient_idx]:
                for patch_paths in patient_slide_patch[patient_in_val].values():
                    val_paths += patch_paths
            for patient_in_test in patients[patient_idx:]:
                for patch_paths in patient_slide_patch[patient_in_test].values():
                    test_paths += patch_paths

        # make sure testing set has more data than validation set
        if len(val_paths) > len(test_paths):
            swap_paths = test_paths[:]
            test_paths = val_paths[:]
            val_paths = swap_paths[:]

        return val_paths, test_paths

    def create_train_val_test_splits(self):
        """Function to create training, validation and testing sets

        Parameters
        ----------
        patch_dir : string
            Absolute path to a directory contains extracted patches

        json_path : string
            Absoluate path to group information json file

        out_dir : string
            Absoluate path to the directory that store the splits

        n_groups : int
            Number of groups, each group contains patches from unique patients

        Returns
        -------
        None
        """
        latex_output = ''
        markdown_output = ''

        with open(self.group_file_location, 'r') as f:
            groups = convert_mitch_to_yiping_format(json.load(f))
        n_groups = len(groups)

        for train_group in list(itertools.combinations(list(range(1, n_groups + 1)),
                self.n_train_groups)):
            eval_group = list(set(range(1, n_groups + 1)) - set(train_group))
            train_patches = []
            eval_patches  = []

            for train_group_idx in train_group:
                train_patches += groups['group_' + str(train_group_idx)][:]

            for eval_group_idx in eval_group:
                eval_patches += groups['group_' + str(eval_group_idx)][:]

            val_patches, test_patches = self.create_val_test_splits(eval_patches)

            train_group = [str(t) for t in train_group]
            eval_group = [str(t) for t in eval_group]

            group_name = '_'.join(train_group) + '_train_' + \
                '_'.join(eval_group) + '_eval'
            markdown_output += self.markdown_header(f'({group_name}) patch counts')

            random.seed(self.seed)
            random.shuffle(train_patches)
            subtypes_count = utils.count_subtype(train_patches, self.patch_pattern,
                    self.CategoryEnum, is_binary=self.is_binary)
            latex_output += self.latex_formatter(subtypes_count,
                    'training patches')
            markdown_output += self.markdown_formatter(subtypes_count,
                    'training patches')

            random.seed(self.seed)
            random.shuffle(val_patches)
            subtypes_count = utils.count_subtype(val_patches, self.patch_pattern,
                    self.CategoryEnum, is_binary=self.is_binary)
            latex_output += self.latex_formatter(subtypes_count,
                    'validation patches')
            markdown_output += self.markdown_formatter(subtypes_count,
                    'validation patches')

            random.seed(self.seed)
            random.shuffle(test_patches)
            subtypes_count = utils.count_subtype(test_patches, self.patch_pattern,
                    self.CategoryEnum, is_binary=self.is_binary)
            latex_output += self.latex_formatter(subtypes_count,
                    'testing patches')
            markdown_output += self.markdown_formatter(subtypes_count,
                    'testing patches')
            markdown_output += '\n'

            split = {'group_1': train_patches, 'group_2': val_patches, 'group_3': test_patches}
            with open(os.path.join(self.split_location,
                    f'{self.split_file_prefix}.{group_name}.json'), 'w') as f:
                json.dump(convert_yiping_to_mitch_format(split), f)

        #print(latex_output)
        #print()
        print(markdown_output)
