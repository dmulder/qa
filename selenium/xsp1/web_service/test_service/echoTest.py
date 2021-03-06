#!/usr/bin/env python

import sys
import os
import unittest
import time
import re

basepath = os.path.dirname(os.path.realpath(__file__))
while not os.path.isfile(os.path.join(basepath,'common','monoTestCase.py')):
    basepath = os.path.dirname(basepath)
if not basepath in sys.path:
    sys.path.append(basepath)

import common.monotesting as mono
from selenium.xsp1.xsp1TestCase import xsp1TestCase

class WebService_TestService_EchoTest(xsp1TestCase):
    xsp1TestCaseId = 426296
    xsp2TestCaseId = 841152
    xsp4TestCaseId = None

    def test(self):
        try:
            sel = self.selenium
            sel.open("/index.aspx")
            sel.click("link=TestService.asmx")
            sel.wait_for_page_to_load("30000")
            sel.click("link=Echo")
            sel.wait_for_page_to_load("30000")
            sel.click("//a[2]/span")
            sel.wait_for_page_to_load("30000")
            sel.type("a", "this is a test")
            sel.click("//input[@value='Invoke']")
            sel.wait_for_page_to_load("30000")
            self.failUnless(re.search(r"^[\s\S]*this is a test[\s\S]*$", sel.get_text("//html/body/table/tbody/tr/td[2]/div/div/div")))

        except Exception, e:
            self.verificationErrors.append(str(e))


if __name__ == "__main__":
    mono.monotesting_main()


# vim:ts=4:expandtab:
