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
        x = numpy.array([[1,2,3], [5,7,11]], dtype=float)
        logger.debug("x:  {}".format(x))
        logger.debug("x.shape:  {}".format(x.shape))

        y = numpy.array([[13, 17, 19], [23, 29, 31]], dtype=float)
        logger.debug("y:  {}".format(y))
        logger.debug("y.shape:  {}".format(y.shape))

        return x, y

    @staticmethod
    def build_nan_containing_x_y():
        x = numpy.array([[1,numpy.nan,2], [3,5,7], [11,13,17]], dtype=float)
        logger.debug("x:\n{}".format(x))
        logger.debug("x.shape:  {}".format(x.shape))

        y = numpy.array([[19, 23, 29], [31, 37, 41], [numpy.nan, 43, 47]], dtype=float)
        logger.debug("y:\n{}".format(y))
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

        off_diag_ind = int(combined.shape[1] / 2)

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
        off_diag_ind = int(combined.shape[1] / 2)

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

    def test_fast_cov_1D_arrays(self):
        logger.debug("*****************happy path test_fast_cov_1D_arrays")
        x = numpy.array(range(3))
        logger.debug("x.shape:  {}".format(x.shape))

        r = fast_cov.fast_cov(x)
        logger.debug("r:  {}".format(r))
        self.assertEqual(1., r[0][0])

        y = numpy.array(range(3,6))
        logger.debug("y.shape:  {}".format(y.shape))

        r = fast_cov.fast_cov(x, y)
        logger.debug("r:  {}".format(r))
        self.assertEqual(1., r[0][0])

    def test_calculate_non_mask_overlaps(self):
        x = numpy.zeros((3,3))
        x[0,1] = numpy.nan
        x = numpy.ma.array(x, mask=numpy.isnan(x))
        logger.debug("happy path x has 1 nan - x:\n{}".format(x))

        r = fast_cov.calculate_non_mask_overlaps(x.mask, x.mask)
        logger.debug("r:\n{}".format(r))
        
        expected = numpy.array([[3,2,3], [2,2,2], [3,2,3]], dtype=int)
        self.assertTrue(numpy.array_equal(expected, r))

    def test_nan_fast_cov_just_x(self):
        logger.debug("*************happy path just x")
        x, _ = TestFastCov.build_nan_containing_x_y()

        ex_with_nan = numpy.cov(x, rowvar=False)
        logger.debug("expected with nan's - ex_with_nan:\n{}".format(ex_with_nan))

        r = fast_cov.nan_fast_cov(x)
        logger.debug("r:\n{}".format(r))
        
        non_nan_locs = ~numpy.isnan(ex_with_nan)
        self.assertTrue(numpy.allclose(ex_with_nan[non_nan_locs], r[non_nan_locs]))

        check_nominal_nans = []
        u = x[1:, 1]
        for i in range(3):
            t = x[1:, i]
            c = numpy.cov(t, u, bias=False)[0,1]
            check_nominal_nans.append(c)
        logger.debug("calculate entries that would be nan - check_nominal_nans:  {}".format(check_nominal_nans))
        self.assertTrue(numpy.allclose(check_nominal_nans, r[:, 1]))
        self.assertTrue(numpy.allclose(check_nominal_nans, r[1, :]))

    def test_nan_fast_cov_x_and_y(self):
        logger.debug("*************happy path x and y")
        x, y = TestFastCov.build_nan_containing_x_y()

        combined = numpy.hstack([x, y])
        logger.debug("combined:\n{}".format(combined))
        logger.debug("combined.shape:  {}".format(combined.shape))

        off_diag_ind = int(combined.shape[1] / 2)

        raw_ex = numpy.cov(combined, rowvar=False)
        logger.debug("raw expected produced from numpy.cov on full combined - raw_ex:\n{}".format(raw_ex))
        ex = raw_ex[:off_diag_ind, off_diag_ind:]
        logger.debug("expected ex:\n{}".format(ex))

        r = fast_cov.nan_fast_cov(x, y)
        logger.debug("r:\n{}".format(r))

        non_nan_locs = ~numpy.isnan(ex)
        logger.debug("ex[non_nan_locs]:  {}".format(ex[non_nan_locs]))
        logger.debug("r[non_nan_locs]:  {}".format(r[non_nan_locs]))
        self.assertTrue(numpy.allclose(ex[non_nan_locs], r[non_nan_locs]))

        check_nominal_nans = []
        t = x[1:, 1]
        for i in [1,2]:
            u = y[1:, i]
            c = numpy.cov(t,u)
            check_nominal_nans.append(c[0,1])
        logger.debug("calculate entries that would be nan - check_nominal_nans:  {}".format(check_nominal_nans))
        logger.debug("r values to compare to - r[1, 1:]:  {}".format(r[1, 1:]))
        self.assertTrue(numpy.allclose(check_nominal_nans, r[1, 1:]))
        
        check_nominal_nans = []
        u = y[:2, 0]
        for i in [0, 2]:
            t = x[:2, i]
            c = numpy.cov(t,u)
            check_nominal_nans.append(c[0,1])
        logger.debug("calculate entries that would be nan - check_nominal_nans:  {}".format(check_nominal_nans))
        logger.debug("r values to compare to - r[[0,2], 0]:  {}".format(r[[0,2], 0]))
        self.assertTrue(numpy.allclose(check_nominal_nans, r[[0,2], 0]))

        self.assertTrue(numpy.isnan(r[1,0]), """expect this entry to be nan b/c for the intersection of x[:,1] and y[:,0] 
            there is only one entry in common, therefore covariance is undefined""")

    def test_nan_fast_cov_x_and_y_different_shapes(self):
        logger.debug("*************happy path x and y different shapes")
        x, t = TestFastCov.build_nan_containing_x_y()
        y = numpy.zeros((t.shape[0], t.shape[1]+1))
        y[:, :t.shape[1]] = t
        y[:, t.shape[1]] = [53, 59, 61]
        
        logger.debug("y.shape:  {}".format(y.shape))
        logger.debug("y:\n{}".format(y))

        combined = numpy.hstack([x, y])
        logger.debug("combined:\n{}".format(combined))
        logger.debug("combined.shape:  {}".format(combined.shape))

        raw_ex = numpy.cov(combined, rowvar=False)
        logger.debug("raw expected produced from numpy.cov on full combined - raw_ex:\n{}".format(raw_ex))
        logger.debug("raw_ex.shape:  {}".format(raw_ex.shape))

        ex = raw_ex[:x.shape[1], -y.shape[1]:]
        logger.debug("expected ex:\n{}".format(ex))
        logger.debug("ex.shape:  {}".format(ex.shape))

        r = fast_cov.nan_fast_cov(x, y)
        logger.debug("r:\n{}".format(r))

        non_nan_locs = ~numpy.isnan(ex)
        logger.debug("ex[non_nan_locs]:  {}".format(ex[non_nan_locs]))
        logger.debug("r[non_nan_locs]:  {}".format(r[non_nan_locs]))
        self.assertTrue(numpy.allclose(ex[non_nan_locs], r[non_nan_locs]))

        check_nominal_nans = []
        t = x[1:, 1]
        for i in [1,2,3]:
            u = y[1:, i]
            c = numpy.cov(t,u)
            check_nominal_nans.append(c[0,1])
        logger.debug("calculate entries that would be nan - check_nominal_nans:  {}".format(check_nominal_nans))
        logger.debug("r values to compare to - r[1, 1:]:  {}".format(r[1, 1:]))
        self.assertTrue(numpy.allclose(check_nominal_nans, r[1, 1:]))
        
        check_nominal_nans = []
        u = y[:2, 0]
        for i in [0, 2]:
            t = x[:2, i]
            c = numpy.cov(t,u)
            check_nominal_nans.append(c[0,1])
        logger.debug("calculate entries that would be nan - check_nominal_nans:  {}".format(check_nominal_nans))
        logger.debug("r values to compare to - r[[0,2], 0]:  {}".format(r[[0,2], 0]))
        self.assertTrue(numpy.allclose(check_nominal_nans, r[[0,2], 0]))

        self.assertTrue(numpy.isnan(r[1,0]), """expect this entry to be nan b/c for the intersection of x[:,1] and y[:,0] 
            there is only one entry in common, therefore covariance is undefined""")

    def test_nan_fast_cov_all_nan(self):
        x = numpy.zeros(3)
        x[:] = numpy.nan
        x = x[:, numpy.newaxis]
        logger.debug("x:\n{}".format(x))

        r = fast_cov.nan_fast_cov(x)
        logger.debug("r:\n{}".format(r))
        
        self.assertEqual(0, numpy.sum(numpy.isnan(r)))
        
    def test_nan_fast_cov_1D_arrays(self):
        logger.debug("*****************happy path test_nan_fast_cov_1D_arrays")
        x = numpy.array(range(3))
        logger.debug("x.shape:  {}".format(x.shape))

        r = fast_cov.nan_fast_cov(x)
        logger.debug("r:  {}".format(r))
        self.assertEqual(1., r[0][0])

        y = numpy.array(range(3,6))
        logger.debug("y.shape:  {}".format(y.shape))

        r = fast_cov.fast_cov(x, y)
        logger.debug("r:  {}".format(r))
        self.assertEqual(1., r[0][0])
        
if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
