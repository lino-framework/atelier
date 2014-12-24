from unipath import Path

ROOTDIR = Path(__file__).parent.parent

# load  SETUP_INFO:
SETUP_INFO = {}
execfile(ROOTDIR.child('atelier', 'project_info.py'), globals())

from atelier.test import TestCase


class BaseTestCase(TestCase):
    project_root = ROOTDIR
    

class BasicTests(BaseTestCase):

    def test_01(self):
        self.assertEqual(1+1, 2)

    def test_utils(self):
        self.run_simple_doctests('atelier/utils.py')

    def test_rstgen(self):
        self.run_simple_doctests('atelier/rstgen.py')


class PackagesTests(BaseTestCase):
    def test_packages(self):
        self.run_packages_test(SETUP_INFO['packages'])


class SphinxTests(BaseTestCase):
    def test_sphinxconf(self):
        self.run_simple_doctests('atelier/sphinxconf/__init__.py')

    def test_base(self):
        self.run_simple_doctests('atelier/sphinxconf/base.py')
