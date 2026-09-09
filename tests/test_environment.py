import sys

import numpy as np
import nsblowup


def test_environment():
    assert sys.version_info >= (3, 11)
    assert np.ones(1).dtype == np.float64
    assert nsblowup.__doc__