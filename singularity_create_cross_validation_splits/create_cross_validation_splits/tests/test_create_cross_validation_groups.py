import pytest
import unittest
import random

import submodule_utils as utils
from create_cross_validation_splits.tests import (
        GROUP_FILE_LOCATION, OUTPUT_DIR)
from create_cross_validation_splits.parser import create_parser
from create_cross_validation_splits import *
random.seed(default_seed)

def test_create_val_test_splits():
    args_str = f"""
    from-arguments
    --is_binary
    --group_file_location {GROUP_FILE_LOCATION}
    --split_location {OUTPUT_DIR}
    """
    parser = create_parser()
    config = parser.get_args(args_str.split())
    cvgc = CrossValidationGroupsCreator(config)
    
    VOA_1000__eval_patches = [
        '/path/to/patch/Tumor/CC/VOA-1000A/0_0.png',
        '/path/to/patch/Tumor/CC/VOA-1000B/1_0.png',
        '/path/to/patch/Tumor/CC/VOA-1000C/2_0.png',
        '/path/to/patch/Other/CC/VOA-1000D/3_0.png',
        '/path/to/patch/Necrosis/CC/VOA-1000D/4_0.png',

    ]
    VOA_2000__eval_patches = [
        '/path/to/patch/Tumor/CC/VOA-2000A/0_0.png',
        '/path/to/patch/Tumor/CC/VOA-2000B/1_0.png',
        '/path/to/patch/Stroma/CC/VOA-2000C/2_0.png',
        '/path/to/patch/MucinousBorderlineTumor/CC/VOA-2000C/3_0.png',
    ]
    eval_patches = []
    eval_patches.extend(VOA_1000__eval_patches)
    eval_patches.extend(VOA_2000__eval_patches)
    random.shuffle(eval_patches)

    val_paths, test_paths = cvgc.create_val_test_splits(eval_patches)
    assert len(test_paths) == 5
    assert len(val_paths) == 4
    assert set(test_paths).issuperset(set(VOA_1000__eval_patches[:3]))
    assert set(val_paths).issuperset(set(VOA_2000__eval_patches[:3]))

def test_create_val_test_splits_for_tcga():
    is_binary = True
    dataset_origin = 'tcga'
    patch_pattern = 'slide/annotation'
    args_str = f"""
    from-arguments
    --is_binary
    --patch_pattern {patch_pattern}
    --dataset_origin {dataset_origin}
    --group_file_location {GROUP_FILE_LOCATION}
    --split_location {OUTPUT_DIR}
    """
    parser = create_parser()
    config = parser.get_args(args_str.split())
    cvgc = CrossValidationGroupsCreator(config)
    
    TCGA_PG_A6IB__eval_patches = [
        '/path/to/patch/TCGA-PG-A6IB-01Z-00-DX4.631A44B6-43E0-4481-AF1F-3EB484784672/Tumor/1_0.png',
        '/path/to/patch/TCGA-PG-A6IB-01Z-00-DX4.631A44B6-43E0-4481-AF1F-3EB484784672/Tumor/2_0.png',
        '/path/to/patch/TCGA-PG-A6IB-01Z-00-DX1.575AC6BD-6ABA-468D-9A46-DC61BD92269C/Tumor/3_0.png',
        '/path/to/patch/TCGA-PG-A6IB-01Z-00-DX4.631A44B6-43E0-4481-AF1F-3EB484784672/Stroma/2_0.png'
    ]
    TCGA_AX_A1CC__eval_patches = [
        '/path/to/patch/TCGA-AX-A1CC-01Z-00-DX2.9DBD4FAD-5E16-450D-8B8F-CCDD34A211F1/Tumor/1_0.png',
        '/path/to/patch/TCGA-AX-A1CC-01Z-00-DX2.9DBD4FAD-5E16-450D-8B8F-CCDD34A211F1/Tumor/2_0.png',
        '/path/to/patch/TCGA-AX-A1CC-01Z-00-DX2.9DBD4FAD-5E16-450D-8B8F-CCDD34A211F1/Necrosis/2_0.png'
    ]
    eval_patches = []
    eval_patches.extend(TCGA_PG_A6IB__eval_patches)
    eval_patches.extend(TCGA_AX_A1CC__eval_patches)
    random.shuffle(eval_patches)

    val_paths, test_paths = cvgc.create_val_test_splits(eval_patches)
    assert len(test_paths) == 4
    assert len(val_paths) == 3
    assert set(test_paths).issuperset(set(TCGA_PG_A6IB__eval_patches[:3]))
    assert set(val_paths).issuperset(set(TCGA_AX_A1CC__eval_patches[:3]))
