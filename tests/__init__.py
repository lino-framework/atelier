from unipath import Path

ROOTDIR = Path(__file__).parent.parent

# load  SETUP_INFO:
execfile(ROOTDIR.child('atelier','setup_info.py'),globals())

from atelier.test import SubProcessTestCase

class AtelierTestCase(SubProcessTestCase):
    project_root = ROOTDIR
    
class BasicTests(AtelierTestCase):
    def test_01(self): 
        self.assertEqual(1+1,2)

    def test_utils(self): self.run_simple_doctests('atelier/utils.py')
    def test_rstgen(self): self.run_simple_doctests('atelier/rstgen.py')
