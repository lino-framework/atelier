# -*- coding: UTF-8 -*-

from atelier import SETUP_INFO
from atelier.test import TestCase


class BasicTests(TestCase):

    def test_01(self):
        self.assertEqual(1+1, 2)

    # the following test case should always be commented out
    # def test_fail_with_unicode_error(self):
    #     self.fail(u"Scheiße wa!")

    def test_utils(self):
        self.run_simple_doctests('atelier/utils.py')

    def test_sheller(self):
        self.run_simple_doctests('atelier/sheller.py')


class PackagesTests(TestCase):
    def test_packages(self):
        self.run_packages_test(SETUP_INFO['packages'])


class SphinxTests(TestCase):
    def test_sphinxconf(self):
        self.run_simple_doctests('atelier/sphinxconf/__init__.py')

    def test_base(self):
        self.run_simple_doctests('atelier/sphinxconf/base.py')

    def test_sigal(self):
        self.run_simple_doctests('atelier/sphinxconf/sigal_image.py')
