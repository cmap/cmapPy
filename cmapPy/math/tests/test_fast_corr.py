import unittest
import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
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
        logger.debug("x:  {}".format(x))
        logger.debug("x.shape:  {}".format(x.shape))

        y = numpy.array([[13, 17, 19], [23, 31, 29]])
        logger.debug("y:  {}".format(y))
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

        off_diag_ind = combined.shape[1] / 2

        raw_ex = numpy.corrcoef(combined, rowvar=False)
        logger.debug("raw expected produced from numpy.cov on full combined - raw_ex:  {}".format(raw_ex))
        ex = raw_ex[:off_diag_ind, off_diag_ind:]
        logger.debug("expected ex:  {}".format(ex))

        r = fast_corr.fast_corr(x, y)
        logger.debug("r:  {}".format(r))
        self.assertTrue(numpy.allclose(ex, r))

        #happy path x and y, other direction
        combined = numpy.hstack([x.T, y.T])
        logger.debug("*************happy path x and y, other direction - combined:  {}".format(combined))
        logger.debug("combined.shape:  {}".format(combined.shape))

        off_diag_ind = combined.shape[1] / 2

        raw_ex = numpy.corrcoef(combined, rowvar=False)
        logger.debug("raw expected produced from numpy.cov on full combined - raw_ex:  {}".format(raw_ex))
        ex = raw_ex[:off_diag_ind, off_diag_ind:]
        logger.debug("expected ex:  {}".format(ex))

        r = fast_corr.fast_corr(x.T, y.T)
        logger.debug("r:  {}".format(r))
        self.assertTrue(numpy.allclose(ex, r))
    
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

        for i in xrange(num_iterations_functional_tests):
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
        logger.debug("r:  {}".format(r))

        self.assertTrue(numpy.allclose(ex, r))


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
