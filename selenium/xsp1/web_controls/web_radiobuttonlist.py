#!/usr/bin/env python

import sys, unittest, time, re

sys.path.append('../../..')
import common.monotesting as mono
from selenium.xsp1.xsp1TestCase import xsp1TestCase

class WebControls_WebRadioButtonList(xsp1TestCase):
    xsp1TestCaseId = 838907
    xsp2TestCaseId = 861814
    xsp4TestCaseId = None

    def rbl1XPath(self, idx):
        return "//*[@id=\"rbl1_" + idx + "\"]"
    
    def rbl2XPath(self, idx):
        return "//*[@id=\"rbl2_" + idx + "\"]"
        
    def test(self):
        if not self.canRun:
            return
        try:
            sel = self.selenium
            sel.open("/")
            sel.click("link=web_radiobuttonlist")
            sel.wait_for_page_to_load("30000")
            self.failIf(sel.is_checked(self.rbl1XPath("0")))
            sel.click("rbl1_0")
            self.failUnless(sel.is_checked(self.rbl1XPath("0")))
            self.failIf(sel.is_checked(self.rbl1XPath("1")))
            sel.click("rbl1_1")
            self.failUnless(sel.is_checked(self.rbl1XPath("1")))
            self.failIf(sel.is_checked(self.rbl1XPath("0")))
            self.failIf(sel.is_checked(self.rbl1XPath("2")))
            sel.click("rbl1_2")
            self.failUnless(sel.is_checked(self.rbl1XPath("2")))
            self.failIf(sel.is_checked(self.rbl1XPath("3")))
            self.failIf(sel.is_checked(self.rbl1XPath("3")))
            sel.click("rbl1_3")
            self.failUnless(sel.is_checked(self.rbl1XPath("3")))
            self.failIf(sel.is_checked(self.rbl1XPath("2")))
            self.failIf(sel.is_checked(self.rbl1XPath("5")))
            sel.click("rbl1_5")
            self.failUnless(sel.is_checked(self.rbl1XPath("5")))
            self.failIf(sel.is_checked(self.rbl1XPath("3")))
            self.failIf(sel.is_checked(self.rbl2XPath("0")))
            sel.click("rbl2_0")
            self.failUnless(sel.is_checked(self.rbl2XPath("0")))
            self.failIf(sel.is_checked(self.rbl2XPath("1")))
            sel.click("rbl2_1")
            self.failUnless(sel.is_checked(self.rbl2XPath("1")))
            self.failIf(sel.is_checked(self.rbl2XPath("0")))
            self.failIf(sel.is_checked(self.rbl2XPath("2")))
            sel.click("rbl2_2")
            self.failUnless(sel.is_checked(self.rbl2XPath("2")))
            self.failIf(sel.is_checked(self.rbl2XPath("3")))
            self.failIf(sel.is_checked(self.rbl2XPath("3")))
            sel.click("rbl2_3")
            self.failUnless(sel.is_checked(self.rbl2XPath("3")))
            self.failIf(sel.is_checked(self.rbl2XPath("2")))
            self.failIf(sel.is_checked(self.rbl2XPath("5")))
            sel.click("rbl2_5")
            self.failUnless(sel.is_checked(self.rbl2XPath("5")))
            self.failIf(sel.is_checked(self.rbl2XPath("3")))
    
        except Exception,e:
            self.verificationErrors.append(str(e))


if __name__ == "__main__":
    mono.monotesting_main()


# vim:ts=4:expandtab:
