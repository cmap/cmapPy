import unittest
import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.math.fast_cov as fast_cov
import numpy


logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestFastCov(unittest.TestCase):
    @staticmethod
    def build_standard_x_y():
        x = numpy.array([[1,2,3], [5,7,11]])
        logger.debug("x:  {}".format(x))
        logger.debug("x.shape:  {}".format(x.shape))

        y = numpy.array([[13, 17, 19], [23, 29, 31]])
        logger.debug("y:  {}".format(y))
        logger.debug("y.shape:  {}".format(y.shape))

        return x, y

    def test_validate_x_y(self):
        shape = (3,2)
        
        #happy path just x
        x = numpy.zeros(shape)
        fast_cov.validate_x_y(x, None)
        fast_cov.validate_x_y(x, None)

        x = numpy.zeros(1)
        fast_cov.validate_x_y(x, None)
        fast_cov.validate_x_y(x, None)
        
        #unhappy path just x, x does not have shape attribute
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.validate_x_y(None, None)
        logger.debug("unhappy path just x, x does not have shape attribute - context.exception:  {}".format(context.exception))
        self.assertIn("x needs to be numpy array-like", str(context.exception))

        #unhappy path x does not have shape attribute, y does not have shape attribute
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.validate_x_y(None, 3)
        logger.debug("unhappy path x does not have shape attribute, y does not have shape attribute - context.exception:  {}".format(context.exception))
        self.assertIn("x needs to be numpy array-like", str(context.exception))
        self.assertIn("y needs to be numpy array-like", str(context.exception))

        #happy path x and y
        x = numpy.zeros(shape)
        y = numpy.zeros(shape)
        fast_cov.validate_x_y(x, y)
        fast_cov.validate_x_y(x, y)

        #happy path y different shape from x
        y = numpy.zeros((3,1))
        fast_cov.validate_x_y(x, y)

        #unhappy path y different shape from x, invalid axis
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.validate_x_y(x, y.T)
        logger.debug("unhappy path y different shape from x, invalid axis - context.exception:  {}".format(context.exception))
        self.assertIn("the number of rows in the x and y matrices must be the same", str(context.exception))
        
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.validate_x_y(x.T, y)
        logger.debug("unhappy path y different shape from x, invalid axis - context.exception:  {}".format(context.exception))
        self.assertIn("the number of rows in the x and y matrices must be the same", str(context.exception))

    def test_fast_cov_check_validations_run(self):
        #unhappy path check that input validation checks are run
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.fast_cov(None, None)
        logger.debug("unhappy path check that input validation checks are run - context.exception:  {}".format(context.exception))

    def test_fast_cov_just_x(self):
        logger.debug("*************happy path just x")
        x, _ = TestFastCov.build_standard_x_y()

        ex = numpy.cov(x, rowvar=False)
        logger.debug("expected ex:  {}".format(ex))

        r = fast_cov.fast_cov(x)
        logger.debug("r:  {}".format(r))
        
        self.assertTrue(numpy.allclose(ex, r))

        #happy path just x, transposed
        ex = numpy.cov(x, rowvar=True)
        logger.debug("happy path just x, transposed, expected ex:  {}".format(ex))
        r = fast_cov.fast_cov(x.T)
        logger.debug("r:  {}".format(r))
        self.assertTrue(numpy.allclose(ex, r))

    def test_fast_cov_x_and_y(self):
        logger.debug("*************happy path x and y")
        x, y = TestFastCov.build_standard_x_y()

        combined = numpy.hstack([x, y])
        logger.debug("combined:  {}".format(combined))
        logger.debug("combined.shape:  {}".format(combined.shape))

        off_diag_ind = combined.shape[1] / 2

        raw_ex = numpy.cov(combined, rowvar=False)
        logger.debug("raw expected produced from numpy.cov on full combined - raw_ex:  {}".format(raw_ex))
        ex = raw_ex[:off_diag_ind, off_diag_ind:]
        logger.debug("expected ex:  {}".format(ex))

        r = fast_cov.fast_cov(x, y)
        logger.debug("r:  {}".format(r))
        self.assertTrue(numpy.allclose(ex, r))

        #happy path x and y, other direction
        combined = numpy.hstack([x.T, y.T])
        off_diag_ind = combined.shape[1] / 2

        raw_ex = numpy.cov(combined, rowvar=False)
        logger.debug("happy path x and y, other direction, raw expected produced from numpy.cov on full combined - raw_ex:  {}".format(raw_ex))
        ex = raw_ex[:off_diag_ind, off_diag_ind:]
        logger.debug("expected ex:  {}".format(ex))

        r = fast_cov.fast_cov(x.T, y.T)
        logger.debug("r:  {}".format(r))
        self.assertTrue(numpy.allclose(ex, r))

    def test_fast_cov_x_and_y_different_shapes(self):
        logger.debug("*************happy path x and y different shapes")
        x, _ = TestFastCov.build_standard_x_y()
        y = numpy.array([[13, 17, 19, 23, 41], [23, 29, 31, 37, 43]])
        logger.debug("y.shape:  {}".format(y.shape))
        logger.debug("y:\n{}".format(y))

        combined = numpy.hstack([x, y])
        logger.debug("combined:  {}".format(combined))
        logger.debug("combined.shape:  {}".format(combined.shape))

        raw_ex = numpy.cov(combined, rowvar=False)
        logger.debug("raw expected produced from numpy.cov on full combined - raw_ex:  {}".format(raw_ex))
        logger.debug("raw_ex.shape:  {}".format(raw_ex.shape))

        ex = raw_ex[:x.shape[1], -y.shape[1]:]
        logger.debug("expected ex:  {}".format(ex))
        logger.debug("ex.shape:  {}".format(ex.shape))

        r = fast_cov.fast_cov(x, y)
        logger.debug("r:  {}".format(r))
        self.assertTrue(numpy.allclose(ex, r))


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
