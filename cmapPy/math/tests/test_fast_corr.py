import unittest
import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.math.fast_cov
import cmapPy.math.fast_corr as fast_corr
import numpy
import pandas


logger = logging.getLogger(setup_logger.LOGGER_NAME)

num_iterations_functional_tests = 20
max_dimension_functional_tests = 10
multiplier_max_functional_tests = 100


class TestFastCorr(unittest.TestCase):
    @staticmethod
    def build_standard_x_y():
        x = numpy.array([[1,7,2], [5,3,11]])
        logger.debug("x:\n{}".format(x))
        logger.debug("x.shape:  {}".format(x.shape))

        y = numpy.array([[13, 17, 19], [23, 31, 29]])
        logger.debug("y:\n{}".format(y))
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

    def test_fast_corr_just_x(self):
        logger.debug("*************happy path just x")
        x, _ = TestFastCorr.build_standard_x_y()

        ex = numpy.corrcoef(x, rowvar=False)
        logger.debug("expected ex:  {}".format(ex))

        r = fast_corr.fast_corr(x)
        logger.debug("r:  {}".format(r))
        
        self.assertTrue(numpy.allclose(ex, r))

        #happy path just x, destination provided
        dest = numpy.zeros((x.shape[1], x.shape[1]))
        r = fast_corr.fast_corr(x, destination=dest)
        self.assertIs(dest, r)
        self.assertTrue(numpy.allclose(ex, dest))

        #happy path just x, other direction
        ex = numpy.corrcoef(x, rowvar=True)
        logger.debug("happy path just x, other direction, expected ex:  {}".format(ex))
        r = fast_corr.fast_corr(x.T)
        logger.debug("r:  {}".format(r))
        self.assertTrue(numpy.allclose(ex, r))

    def test_fast_corr_x_and_y(self):
        logger.debug("*************happy path x and y")
        x, y = TestFastCorr.build_standard_x_y()

        combined = numpy.hstack([x, y])
        logger.debug("combined:  {}".format(combined))
        logger.debug("combined.shape:  {}".format(combined.shape))

        off_diag_ind = int(combined.shape[1] / 2)
        raw_ex = numpy.corrcoef(combined, rowvar=False)
        logger.debug("raw expected produced from numpy.cov on full combined - raw_ex:  {}".format(raw_ex))
        ex = raw_ex[:off_diag_ind, off_diag_ind:]
        logger.debug("expected ex:  {}".format(ex))

        r = fast_corr.fast_corr(x, y)
        logger.debug("r:  {}".format(r))
        self.assertTrue(numpy.allclose(ex, r))

        #happy path x, y, and destination
        dest = numpy.zeros((x.shape[1], y.shape[1]))
        r = fast_corr.fast_corr(x, y, dest)
        self.assertIs(dest, r)
        self.assertTrue(numpy.allclose(ex, dest))

        #happy path x and y, other direction
        combined = numpy.hstack([x.T, y.T])
        logger.debug("*************happy path x and y, other direction - combined:  {}".format(combined))
        logger.debug("combined.shape:  {}".format(combined.shape))

        off_diag_ind = int(combined.shape[1] / 2)

        raw_ex = numpy.corrcoef(combined, rowvar=False)
        logger.debug("raw expected produced from numpy.cov on full combined - raw_ex:  {}".format(raw_ex))
        ex = raw_ex[:off_diag_ind, off_diag_ind:]
        logger.debug("expected ex:  {}".format(ex))

        r = fast_corr.fast_corr(x.T, y.T)
        logger.debug("r:  {}".format(r))
        self.assertTrue(numpy.allclose(ex, r))
    
    def test_fast_corr_1D_arrays(self):
        logger.debug("*****************happy path test_fast_corr_1D_arrays")
        x = numpy.array(range(3))
        logger.debug("x.shape:  {}".format(x.shape))

        r = fast_corr.fast_corr(x)
        logger.debug("r:  {}".format(r))
        self.assertEqual(1., r[0][0])

        y = numpy.array(range(3,6))
        logger.debug("y.shape:  {}".format(y.shape))

        r = fast_corr.fast_corr(x, y)
        logger.debug("r:  {}".format(r))
        self.assertEqual(1., r[0][0])

        
    def test_fast_corr_x_and_y_different_shapes(self):
        logger.debug("*************happy path x and y different shapes")
        x, _ = TestFastCorr.build_standard_x_y()
        y = numpy.array([[13, 17, 19, 41, 23], [23, 29, 31, 37, 43]])
        logger.debug("y.shape:  {}".format(y.shape))
        logger.debug("y:\n{}".format(y))

        combined = numpy.hstack([x, y])
        logger.debug("combined:  {}".format(combined))
        logger.debug("combined.shape:  {}".format(combined.shape))

        raw_ex = numpy.corrcoef(combined, rowvar=False)
        logger.debug("raw expected produced from numpy.cov on full combined - raw_ex:  {}".format(raw_ex))
        logger.debug("raw_ex.shape:  {}".format(raw_ex.shape))

        ex = raw_ex[:x.shape[1], -y.shape[1]:]
        logger.debug("expected ex:  {}".format(ex))
        logger.debug("ex.shape:  {}".format(ex.shape))

        r = fast_corr.fast_corr(x, y)
        logger.debug("r:  {}".format(r))
        self.assertTrue(numpy.allclose(ex, r))

    def test_fast_corr_functional(self):
        logger.debug("*************happy path functional test using randomly generated matrices")

        for i in range(num_iterations_functional_tests):
            #the dimension containing the observations must have at least size 2
            x_shape = [numpy.random.randint(2, max_dimension_functional_tests),
                numpy.random.randint(1, max_dimension_functional_tests)]
            logger.debug("x_shape:  {}".format(x_shape))

            x = numpy.random.rand(x_shape[0], x_shape[1]) * numpy.random.randint(1, multiplier_max_functional_tests, size=1)
            logger.debug("x:\n{}".format(x))

            y_other_shape = numpy.random.randint(1, max_dimension_functional_tests, size=1)[0]
            y_shape = (x_shape[0], y_other_shape)
            logger.debug("y_shape:  {}".format(y_shape))
            y = numpy.random.rand(y_shape[0], y_shape[1]) * numpy.random.randint(1, multiplier_max_functional_tests, size=1)
            logger.debug("y:\n{}".format(y))

            combined = numpy.hstack([x, y])

            raw_ex = numpy.corrcoef(combined, rowvar=False)
            logger.debug("raw_ex.shape:  {}".format(raw_ex.shape))

            ex = raw_ex[:x.shape[1], -y.shape[1]:]
            logger.debug("ex:\n{}".format(ex))
            logger.debug("ex.shape:  {}".format(ex.shape))

            r = fast_corr.fast_corr(x, y)
            logger.debug("r:\n{}".format(r))
            logger.debug("r.shape:  {}".format(r.shape))

            self.assertTrue(numpy.allclose(ex, r))

    def test_fast_spearman(self):
        x, y = TestFastCorr.build_standard_x_y()

        ex = numpy.array([[1.0, 1.0, 1.0], [-1.0, -1.0, -1.0], [1.0, 1.0, 1.0]])

        r = fast_corr.fast_spearman(x, y)
        logger.debug("r:\n{}".format(r))

        self.assertTrue(numpy.allclose(ex, r))

        #happy path x, y, and destination
        dest = numpy.zeros((x.shape[1], y.shape[1]))
        r = fast_corr.fast_spearman(x, y, dest)
        self.assertIs(dest, r)
        self.assertTrue(numpy.allclose(ex, dest))

    def test_nan_fast_spearman(self):
        x, y = TestFastCorr.build_nan_containing_x_y()
        y[:,2] = y[:,2][::-1]
        logger.debug("updated y:\n{}".format(y))

        ex = numpy.array([[1.0, 1.0, -1.0], [numpy.nan, 1.0, -1.0], [1.0, 1.0, -1.0]])

        r = fast_corr.nan_fast_spearman(x, y)
        logger.debug("r:\n{}".format(r))

        nan_locs = numpy.isnan(ex)
        self.assertTrue(all(numpy.isnan(r[nan_locs])))

        self.assertTrue(numpy.allclose(ex[~nan_locs], r[~nan_locs]))

    def test_calculate_moments_with_additional_mask(self):
        x,y = TestFastCorr.build_nan_containing_x_y()
        x = numpy.ma.array(x, mask=numpy.isnan(x))
        y = numpy.ma.array(y, mask=numpy.isnan(y))

        r_x, r_x2, r_var = fast_corr.calculate_moments_with_additional_mask(x, y.mask)
        
        logger.debug("r_x:\n{}".format(r_x))
        for i in range(y.shape[1]):
            locs = ~numpy.isnan(y[:,i]) # locations in column where y is not nan
            logger.debug("check for r_x[{},:] - locs:  {}".format(i, locs))

            for j in range(x.shape[1]):
                c = numpy.ma.mean(x[locs, j])
                logger.debug("check for r_x[i,j] entry - c:  {}".format(i, j, c))
                self.assertTrue(numpy.isclose(c, r_x[i,j]))

        logger.debug("r_x2:\n{}".format(r_x2))
        for i in range(y.shape[1]):
            locs = ~numpy.isnan(y[:,i]) # locations in column where y is not nan
            logger.debug("check for r_x2[{},:] - locs:  {}".format(i, locs))

            for j in range(x.shape[1]):
                c = numpy.ma.mean(numpy.power(x[locs, j], 2.0))
                logger.debug("check for r_x2[{},{}] entry - c:  {}".format(i, j, c))
                self.assertTrue(numpy.isclose(c, r_x2[i,j]))


        logger.debug("r_var:\n{}".format(r_var))
        overlaps = cmapPy.math.fast_cov.calculate_non_mask_overlaps(x.mask, y.mask).T
        logger.debug("overlaps:\n{}".format(overlaps))
        locs = (0,0)
        n = float(overlaps[locs])
        c = (r_x2[locs] - r_x[locs]**2) * n / (n - 1.)
        logger.debug("check for locs:  {}  n:  {}  c:  {}".format(locs, n, c))
        self.assertTrue(numpy.isclose(c, r_var[locs]))
        locs = (1,0)
        n = float(overlaps[locs])
        c = (r_x2[locs] - r_x[locs]**2) * n / (n - 1.)
        logger.debug("check for locs:  {}  n:  {}  c:  {}".format(locs, n, c))
        # self.assertTrue(numpy.isclose(c, r_var[locs]))
        locs = (2,0)
        n = float(overlaps[locs])
        c = (r_x2[locs] - r_x[locs]**2) * n / (n - 1.)
        logger.debug("check for locs:  {}  n:  {}  c:  {}".format(locs, n, c))
        self.assertTrue(numpy.isclose(c, r_var[locs]))
        locs = (2,2)
        n = float(overlaps[locs])
        c = (r_x2[locs] - r_x[locs]**2) * n / (n - 1.)
        logger.debug("check for locs:  {}  n:  {}  c:  {}".format(locs, n, c))
        self.assertTrue(numpy.isclose(c, r_var[locs]))

    def test_nan_fast_corr_just_x(self):
        logger.debug("*************happy path just x")
        x, _ = TestFastCorr.build_nan_containing_x_y()
        
        logger.debug("current matrix - x:\n{}".format(x))
        ex_with_nan = numpy.corrcoef(x, rowvar=False)
        logger.debug("expected with nan's - ex_with_nan:\n{}".format(ex_with_nan))

        r = fast_corr.nan_fast_corr(x)
        logger.debug("r:\n{}".format(r))
        
        non_nan_locs = ~numpy.isnan(ex_with_nan)
        self.assertTrue(numpy.allclose(ex_with_nan[non_nan_locs], r[non_nan_locs]))

        check_nominal_nans = numpy.zeros(x.shape[1])

        u = x[1:,1]
        print(u)
        for i in range(x.shape[1]):
            t = x[1:, i]
            print(t)
            c = numpy.corrcoef(t, u)[0,1]
            print(c)
            check_nominal_nans[i] = c
        print(check_nominal_nans - r[:,1])
        logger.debug("calculate entries that would be nan - check_nominal_nans:  {}".format(check_nominal_nans))
        self.assertTrue(numpy.allclose(check_nominal_nans, r[:, 1]))
        self.assertTrue(numpy.allclose(check_nominal_nans, r[1, :]))

        x[0,1] = x[1,2]
        x[1,2] = numpy.nan
        logger.debug("current matrix - x:\n{}".format(x))
        ex_with_nan = numpy.corrcoef(x, rowvar=False)
        logger.debug("expected with nan's - ex_with_nan:\n{}".format(ex_with_nan))

        r = fast_corr.nan_fast_corr(x)
        logger.debug("r:\n{}".format(r))
        
        non_nan_locs = ~numpy.isnan(ex_with_nan)
        self.assertTrue(numpy.allclose(ex_with_nan[non_nan_locs], r[non_nan_locs]))

        check_nominal_nans = numpy.zeros(x.shape[1])

        u = x[(0,2),2]
        print(u)
        for i in range(x.shape[1]):
            t = x[(0,2), i]
            print(t)
            c = numpy.corrcoef(t, u)[0,1]
            print(c)
            check_nominal_nans[i] = c
        print(check_nominal_nans - r[:,2])
        logger.debug("calculate entries that would be nan - check_nominal_nans:  {}".format(check_nominal_nans))
        self.assertTrue(numpy.allclose(check_nominal_nans, r[:, 2]))
        self.assertTrue(numpy.allclose(check_nominal_nans, r[2, :]))

    def test_nan_fast_corr_different_shapes(self):
        x,y = TestFastCorr.build_standard_x_y()
        
        z = numpy.zeros((x.shape[0], x.shape[1]+2))
        z[:, :y.shape[1]] = y
        for i in range(y.shape[1], x.shape[1]+2):
            t = (i+1) * numpy.array(range(1, z.shape[0]+1))
            if i%2 == 0:
                z[:, i] = t
            else:
                z[:, i] = t[::-1]
        logger.debug("z:\n{}".format(z))
        logger.debug("z.shape:  {}".format(z.shape))

        combined = numpy.hstack([x, z])

        raw_ex = numpy.corrcoef(combined, rowvar=False)
        logger.debug("raw_ex.shape:  {}".format(raw_ex.shape))

        ex = raw_ex[:x.shape[1], -z.shape[1]:]
        logger.debug("ex:\n{}".format(ex))
        logger.debug("ex.shape:  {}".format(ex.shape))

        r = fast_corr.nan_fast_corr(x, z)
        logger.debug("r:\n{}".format(r))
        logger.debug("r.shape:  {}".format(r.shape))

        self.assertTrue(numpy.allclose(ex, r))
        

    def test_nan_fast_corr_functional(self):
        logger.debug("*************happy path functional test nan_fast_corr using randomly generated matrices")

        # first without any nan's
        for i in range(num_iterations_functional_tests):
            #the dimension containing the observations must have at least size 2
            x_shape = [numpy.random.randint(2, max_dimension_functional_tests),
                numpy.random.randint(1, max_dimension_functional_tests)]
            logger.debug("x_shape:  {}".format(x_shape))

            x = numpy.random.rand(x_shape[0], x_shape[1]) * numpy.random.randint(1, multiplier_max_functional_tests, size=1)
            logger.debug("x:\n{}".format(x))

            y_other_shape = numpy.random.randint(1, max_dimension_functional_tests, size=1)[0]
            y_shape = (x_shape[0], y_other_shape)
            logger.debug("y_shape:  {}".format(y_shape))
            y = numpy.random.rand(y_shape[0], y_shape[1]) * numpy.random.randint(1, multiplier_max_functional_tests, size=1)
            logger.debug("y:\n{}".format(y))

            combined = numpy.hstack([x, y])

            raw_ex = numpy.corrcoef(combined, rowvar=False)
            logger.debug("raw_ex.shape:  {}".format(raw_ex.shape))

            ex = raw_ex[:x.shape[1], -y.shape[1]:]
            logger.debug("ex:\n{}".format(ex))
            logger.debug("ex.shape:  {}".format(ex.shape))

            r = fast_corr.nan_fast_corr(x, y)
            logger.debug("r:\n{}".format(r))
            logger.debug("r.shape:  {}".format(r.shape))

            self.assertTrue(numpy.allclose(ex, r))


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
