import logging

from submodule_utils.logging import logger_factory
import create_cross_validation_splits.parser as parser
from create_cross_validation_splits import *

logger_factory()
logger = logging.getLogger('create_cross_validation_splits')

if __name__ == "__main__":
    config = parser.get_args()
    cvgc = CrossValidationGroupsCreator(config)
    cvgc.create_train_val_test_splits()
