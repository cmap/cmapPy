import unittest
import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.math.fast_cov as fast_cov
import numpy
import tempfile
import os


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

    def test_validate_inputs(self):
        shape = (3,2)
        
        #happy path just x
        x = numpy.zeros(shape)
        fast_cov.validate_inputs(x, None, None)

        x = numpy.zeros(1)
        fast_cov.validate_inputs(x, None, None)
        
        #unhappy path just x, x does not have shape attribute
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.validate_inputs(None, None, None)
        logger.debug("unhappy path just x, x does not have shape attribute - context.exception:  {}".format(context.exception))
        self.assertIn("x needs to be numpy array-like", str(context.exception))

        #unhappy path x does not have shape attribute, y does not have shape attribute
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.validate_inputs(None, 3, None)
        logger.debug("unhappy path x does not have shape attribute, y does not have shape attribute - context.exception:  {}".format(context.exception))
        self.assertIn("x needs to be numpy array-like", str(context.exception))
        self.assertIn("y needs to be numpy array-like", str(context.exception))

        #happy path x and y
        x = numpy.zeros(shape)
        y = numpy.zeros(shape)
        fast_cov.validate_inputs(x, y, None)

        #happy path y different shape from x
        y = numpy.zeros((3,1))
        fast_cov.validate_inputs(x, y, None)

        #unhappy path y different shape from x, invalid axis
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.validate_inputs(x, y.T, None)
        logger.debug("unhappy path y different shape from x, invalid axis - context.exception:  {}".format(context.exception))
        self.assertIn("the number of rows in the x and y matrices must be the same", str(context.exception))
        
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.validate_inputs(x.T, y, None)
        logger.debug("unhappy path y different shape from x, invalid axis - context.exception:  {}".format(context.exception))
        self.assertIn("the number of rows in the x and y matrices must be the same", str(context.exception))

        #happy path with x, destination
        x = numpy.zeros(shape)
        dest = numpy.zeros((shape[1], shape[1]))
        fast_cov.validate_inputs(x, None, dest)

        #unhappy path with x, destination wrong size
        dest = numpy.zeros((shape[1]+1, shape[1]))
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.validate_inputs(x, None, dest)
        logger.debug("unhappy path incorrrect shape of destination for provided x - context.exception:  {}".format(context.exception))
        self.assertIn("x and destination provided", str(context.exception))
        self.assertIn("destination must have shape matching", str(context.exception))

        #happy path with x, y, destination
        x = numpy.zeros(shape)
        y = numpy.zeros((shape[0], shape[1]+1))
        dest = numpy.zeros((shape[1], shape[1]+1))
        fast_cov.validate_inputs(x, y, dest)

        #unhappy path x, y, destination wrong size
        dest = numpy.zeros((shape[1], shape[1]+2))
        with self.assertRaises(fast_cov.CmapPyMathFastCovInvalidInputXY) as context:
            fast_cov.validate_inputs(x, y, dest)
        logger.debug("unhappy path incorrrect shape of destination for provided x, y - context.exception:  {}".format(context.exception))
        self.assertIn("x, y, and destination provided", str(context.exception))
        self.assertIn("destination must have number of", str(context.exception))

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

        #happy path just x, uses destination
        dest = numpy.zeros((x.shape[1], x.shape[1]))
        r = fast_cov.fast_cov(x, destination=dest)
        logger.debug("happy path just x, uses destination - r:  {}".format(r))
        self.assertIs(dest, r)
        self.assertTrue(numpy.allclose(ex, dest))

        #happy path just x, uses destination which is a different type
        dest = dest.astype(numpy.float16)
        r = fast_cov.fast_cov(x, destination=dest)
        logger.debug("happy path, just x, uses destination which is a different type - r:  {}".format(r))
        self.assertIs(dest, r)
        self.assertTrue(numpy.allclose(ex, dest))

        #happy path just x, uses destination that is a numpy.memmap
        outfile = tempfile.mkstemp()
        logger.debug("happy path, just x, uses destination which is a numpy.memmap - outfile:  {}".format(outfile))
        dest = numpy.memmap(outfile[1], dtype="float16", mode="w+", shape=ex.shape)
        dest_array = numpy.asarray(dest)
        r = fast_cov.fast_cov(x, destination=dest_array)
        dest.flush()
        logger.debug(" - r:  {}".format(r))
        os.close(outfile[0])
        os.remove(outfile[1])

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

        #happy path x, y, and destination
        dest = numpy.zeros((x.shape[1], y.shape[1]))
        r = fast_cov.fast_cov(x, y, dest)
        logger.debug("happy path x, y, and destination - r:  {}".format(r))
        self.assertIs(dest, r)
        self.assertTrue(numpy.allclose(ex, dest))

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

        #happy path x and y different shapes, using destination
        dest = numpy.zeros((x.shape[1], y.shape[1]))
        r = fast_cov.fast_cov(x, y, dest)
        logger.debug("happy path x and y different shapes, using destination - r:  {}".format(r))
        self.assertIs(dest, r)
        self.assertTrue(numpy.allclose(ex, dest))

if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
