#!/usr/bin/env python

import sys, unittest, time, re

sys.path.append('../../..')
import common.monotesting as mono
from selenium.xsp1.xsp1TestCase import xsp1TestCase

class HtmlControls_Button(xsp1TestCase):
    xsp1TestCaseId = 838534
    xsp2TestCaseId = 861705
    xsp4TestCaseId = None

    def test(self):
        if not self.canRun:
            return
        try:
            sel = self.selenium
            sel.open("/")
            sel.click("link=button")
            sel.wait_for_page_to_load("30000")
            self.failUnless(sel.is_text_present("HtmlButton Sample"))
            sel.click("Button1")
            time.sleep(1)
            self.assertEqual("You activated Button1", sel.get_text("Span1"))
            self.failUnless(sel.is_element_present("//*[@id=\"Button1\"]"))
            sel.click("Button1")
            sel.wait_for_page_to_load("30000")
            self.assertEqual("You deactivated Button1", sel.get_text("Span1"))
    
        except Exception,e:
            self.verificationErrors.append(str(e))


if __name__ == "__main__":
    mono.monotesting_main()


# vim:ts=4:expandtab:
