#!/usr/bin/env python

import sys,os
import unittest
import traceback
import pdb
import glob
import getpass
import ConfigParser
import shutil
import tempfile

basepath = os.path.dirname(os.path.realpath(__file__))
while not os.path.isfile(os.path.join(basepath,'common','monoTestCase.py')):
    basepath = os.path.dirname(basepath)
if not basepath in sys.path:
    sys.path.append(basepath)

import common.monotesting as mono
from common.helpers import *
from common.monoTestCase import monoTestCase


####################################################################
#
#    smokeTestCase class
#

class smokeTestCase(monoTestCase):
    testcaseid = 0

    def __init__(self,methodname='runTest'):
        if isAppliance():
            if getpass.getuser() != "root":
                raise Exception("You must run this script as root")

        monoTestCase.__init__(self,methodname)
        self.verificationErrors = []
        unittest.TestCase.__init__(self, methodname)


    def remove(self,filepath):
        if os.path.exists(filepath):
            os.remove(filepath)

    def __printResults(self,tmpfiles,filetype,expected=True):
        expected = "%s" % (['Unexpected','Missing'][expected])
        if len(tmpfiles) > 0:
            print ''
        for f in tmpfiles:
            print "   %s %s: %s" % (expected,filetype,f)
        self.assertEqual(0,len(tmpfiles),"%d %s %ss"% (len(tmpfiles),expected.lower(),filetype))

    #---------------------------------------------------------------
    # keep these around just in case

    def checkList(self,alist,func,filetype,expected):
        errors = []
        for cur in alist:
            if func(cur) ^ expected:
                errors.append(cur)
        self.__printResults(errors,filetype,expected)

    def checkFiles(self,list):
        self.checkList(list,os.path.isfile,'file',expected=True)

    def checkDirs(self,list):
        self.checkList(list,os.path.isdir,'dir',expected=True)

    def checkSymlinks(self, list):
        self.checkList(list,os.path.islink,'symlink',expected=True)

    def checkUnexpectedFiles(self,list):
        self.checkList(list,os.path.isfile,'file',expected=False)

    def checkUnexpectedDirs(self,list):
        self.checkList(list,os.path.isdir,'dir',expected=False)

    def checkUnexpectedSymlinks(self,list):
        self.checkList(list,os.path.islink,'symlink',expected=False)

    #---------------------------------------------------------------

    def checkForList(self, dict, chkFunc):
        #pdb.set_trace()
        emptyDirErrors = []
        filesNotFound = []
        unexpectedFilesFound = []
        for curDirGlob in dict.keys():
            globList = glob.glob(curDirGlob)

            if (globList == []):
                emptyDirErrors.append("\t [%s] either doesn't exist, or is an empty directory." % curDirGlob)
            #self.assertNotEqual(globList, [], "[%s] either doesn't exist, or is an empty directory." % curDirGlob)

            for curDir in globList:
                # check that the expected files exist
                for curFile in dict[curDirGlob]:
                    for wholeFile in glob.glob(os.path.join(curDir, curFile)):
                        if (chkFunc(wholeFile) == False):
                            filesNotFound.append("\t [%s] Not Found." % wholeFile)
                        #self.assertTrue(chkFunc(wholeFile),"[%s] Not Found." % wholeFile)

                # check that there aren't any unexpected files that exist
                filesInDir = glob.glob(curDir + os.sep + "*")
                for curFile in filesInDir:
                    if chkFunc(curFile):
                        fileNameOnly = os.path.basename(curFile)

                        if (fileNameOnly not in dict[curDirGlob]):
                            unexpectedFilesFound.append("\t [%s] unexpectedly exists." % curFile)
                        #self.assertTrue(fileNameOnly in dict[curDirGlob], "[%s] unexpectedly exists." % curFile)

        if (len(emptyDirErrors) != 0) or \
           (len(filesNotFound) != 0) or \
           (len(unexpectedFilesFound) != 0):
            print "\n\nUnexpectedly Empty Directories:"
            for err in emptyDirErrors:
                printColor(err,'red')

            print "\n\nFiles Not Found:"
            for err in filesNotFound:
                printColor(err,'red')

            print "\n\nFiles Found Unexpectedly:"
            for err in unexpectedFilesFound:
                printColor(err,'red')

            self.fail("File errors")


    def checkForFiles(self,fileDict):
        self.checkForList(fileDict, os.path.isfile)

    def checkForSymlinks(self,symlinksDict):
        self.checkForList(symlinksDict, os.path.islink)
    #---------------------------------------------------------------
    # These functions are mostly used in the vmware test cases
    def getFileSize(self, filePath):
        statinfo = os.stat(filePath)
        return int(statinfo.st_size)

    def getActiveSwapSize(self):
        cmdOut = executeCmd("free -m")
        return int(cmdOut[3].split()[1])

    def addGlobalSectionHeader(self, fileName, tmpFile):
        fd = open(tmpFile,"w")
        fd.write("[global]\n")

        for curLine in open(fileName).readlines():
            fd.write(curLine)

    def verifyZypperCredentials(self, credentialFileName, expectedData):
        tmpFile = tempfile.mktemp(".ini")
        self.addGlobalSectionHeader(credentialFileName, tmpFile)

        config = ConfigParser.ConfigParser()
        config.read(tmpFile)
        for curData in expectedData:
            self.assertEqual(config.get("global",curData[0]), curData[1])

    def verifyChkconfigIsSet(self, daemon, status):
        cmdOut = executeCmd("chkconfig " + daemon)[0].split()
        self.assertEqual(cmdOut[0], daemon)
        self.assertEqual(cmdOut[1], status)

    def areZypperRepoRefreshesOff(self):
        cmdOut = executeCmd("zypper lr")[2:-1]
        for curRefresh in cmdOut:
            self.assertEqual(curRefresh.split()[-1], "No")

    def canZypperReposBeRefreshed(self):
        cmdOut = executeCmd("zypper ref")[-2].strip()
        self.assertEqual(cmdOut, "All repositories have been refreshed.")

    def verifyZypperRepoData(self, expectedRepoData):
        cmdOut = executeCmd("zypper lr -u")[2:-1]
        numVerifiedRepos = 0

        for curLine in cmdOut:
            curRepo = curLine.split("|")
            alias = curRepo[1].strip()
            name = curRepo[2].strip()
            enabled = curRepo[3].strip()
            refresh = curRepo[4].strip()
            uri = curRepo[5].strip()
            self.assertEqual(name, expectedRepoData[alias][0])
            self.assertEqual(enabled, expectedRepoData[alias][1])
            self.assertEqual(refresh, expectedRepoData[alias][2])
            self.assertEqual(uri, expectedRepoData[alias][3])
            numVerifiedRepos += 1
        self.assertEqual(numVerifiedRepos, len(expectedRepoData))

    def verifyDiskSize(self, mntPoint, expectedSize):
        s = os.statvfs(mntPoint)
        actualSize = (s.f_blocks * s.f_frsize / 1024)
        self.assertGreaterThanOrEquals(actualSize, expectedSize)

    def verifyDiskInodeCount(self, mntPoint, expectedNumberOfInodes):
        s = os.statvfs(mntPoint)
        actualNumberOfInodes = s.f_files
        self.assertGreaterThanOrEquals(actualNumberOfInodes, expectedNumberOfInodes)

    def verifyDesktopFileData(self, filePath, fileName, expectedData):
        fullPath = os.path.join(filePath, fileName)
        self.assertTrue(os.path.isfile(fullPath),"%s does not exist!" % fullPath)

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(filePath,fileName))
        for curData in expectedData:
            self.assertEqual(config.get("Desktop Entry",curData[0]), curData[1])

    def verifyOnlyExpectedDesktopFilesExist(self, filePath, expectedData):
        desktopFiles = {}
        for curIcon in expectedData:
            desktopFiles[curIcon[0]] = curIcon[0]

        entries = glob.glob(filePath + os.sep + "*.desktop")
        unexpectedFilesFound = []
        for curEntry in entries:
            if os.path.isfile(curEntry):
                fileName = os.path.basename(curEntry)
                #self.assertEqual(desktopFiles[fileName], fileName)
                if (fileName not in desktopFiles):
                    unexpectedFilesFound.append("\t [%s] unexpectedly exists." % fileName)

        if (len(unexpectedFilesFound) != 0):
            print "\n\nFiles Found Unexpectedly:"
            for err in unexpectedFilesFound:
                printColor(err,'red')
            self.fail("Files Found Unexpectedly.")


    def verifyProcessIsRunningAsUser(self, processName, userName):
        cmdOut = executeCmd("ps -e -o pid,user,command|grep %s|grep -v grep" % processName)[0].split()
        self.assertEqual(cmdOut[1], userName)
        self.assertEqual(cmdOut[2], processName)

    def verifyFilePermissions(self, filePath, expectedPermissions, expectedUid, expectedGid):
        self.assertTrue(os.path.isfile(filePath), "%s is not a file" % filePath)
        st = os.stat(filePath)
        self.assertEqual(st.st_mode, expectedPermissions)
        self.assertEqual(st.st_uid, expectedUid)
        self.assertEqual(st.st_gid, expectedGid)

    def verifyDirectoryPermissions(self, dirPath, expectedPermissions, expectedUid, expectedGid):
        self.assertTrue(os.path.isdir(dirPath), "%s is not a directory" % dirPath)
        st = os.stat(dirPath)
        self.assertEqual(st.st_mode, expectedPermissions)
        self.assertEqual(st.st_uid, expectedUid)
        self.assertEqual(st.st_gid, expectedGid)

    def howManyTimesDoesFileContainThisLine(self, fileName, line):
        # Basically, this is "grep file for this exact line"
        numFound = 0
        for curLine in open(fileName).readlines():
            if line in curLine:
                numFound += 1
        return numFound

    def doesFileContainLine(self, fileName, line):
        numFound = self.howManyTimesDoesFileContainThisLine(fileName, line)
        if numFound == 0:
            return False
        else:
            return True

    def verifyFileContainsLine(self, fileName, line):
        # Basically, this is "grep file for this exact line"
        found = self.doesFileContainLine(fileName, line)
        self.assertTrue(found, "%s was not found in %s" % (line, fileName))

    def verifyFileDoesNotContainLine(self, fileName, line):
        # Basically, this is "grep file for and make sure it doesn't contain this exact line"
        found = self.doesFileContainLine(fileName, line)
        self.assertFalse(found, "%s was found in %s" % (line, fileName))

    def verifyRpmDoesntOwnFile(self, fileName):
        if os.path.isfile(fileName):
            out = executeCmd("rpm -qf " + fileName)[0]
            self.assertEqual(out, "file " + fileName + " is not owned by any package")
        else:
            printColor("\n\n\tError: File doesn't exist [" + fileName + "]",'red')
            self.fail("Missing RPMs")
            

    def verifyTheseRpmsAreInstalled(self, expectedRpms):
        rpms = executeCmd("rpm -qa --queryformat '%{NAME}\n'")[0:-1]
        #rpms = dict(zip(cmdOut,cmdOut))

        errors = []
        for curExpRpm in expectedRpms:
            if not curExpRpm in rpms:
                errors.append("\t'%s' is missing" % (curExpRpm))
            #self.assertEqual(rpms[curExpRpm], curExpRpm)

        if len(errors) != 0:
            print "\n\nMissing RPMs:"
            for err in errors:
                printColor(err,'red')
            self.fail("Missing RPMs")


    def verifyKernelCommandLineOptions(self, expectedOptions):
        actualOptions = open("/proc/cmdline","r").read().split()

        if 'root=/dev/sda1' in actualOptions and \
           not 'root=/dev/sda1' in expectedOptions:
           expectedOptions.append('root=/dev/sda1')

        expectedOptions.sort()
        actualOptions.sort()

        self.assertEqual(actualOptions, expectedOptions)

    #---------------------------------------------------------------
def generateFileList(basepath,filename):
    f = open(filename,'w')
    files = {}
    symlinks = {}
    for curWalkDirEntries  in os.walk(basepath):
        curWalkDir = curWalkDirEntries[0]
        curWalkFiles = curWalkDirEntries[2]

        filesInCurDir = []
        linksInCurDir = []
        for curFileInDir in curWalkFiles:
            fullPath = os.path.join(curWalkDir, curFileInDir)
            if os.path.isfile(fullPath):
                filesInCurDir.append(curFileInDir)
            elif os.path.islink(fullPath):
                linksInCurDir.append(curFileInDir)
            else:
                raise Exception("%s is not a file or link" % fullPath)

        files[curWalkDir] = filesInCurDir
        symlinks[curWalkDir] = linksInCurDir

    f.write("\nimport os")
    f.write("\nbasepath = '%s'\n" % basepath)
    f.write("\nfiles = {",)
    for curKey in files.keys():
        if len(files[curKey]) > 0:
            newPathList = curKey.replace(basepath,"").split(os.path.sep)[1:]

#            # make it so that the gac checks will pass, even if the gac UUID changes
#            if "gac" in newPathList:
#                newPathList[-1] = "*"

            f.write("\n    os.path.join(basepath")
            for curPath in newPathList:
                f.write(", '%s'" % curPath)
            f.write("):[")
            for curFile in files[curKey]:
                f.write("'%s'," % (curFile))
            f.write("],")
    f.write("\n}\n")

    f.write("\nsymlinks = {")
    for curKey in symlinks.keys():
        if len(symlinks[curKey]) > 0:
            newPathList = curKey.replace(basepath,"").split(os.path.sep)[1:]
            f.write("\n    os.path.join(basepath")
            for curPath in newPathList:
                f.write(", '%s'" % curPath)
            f.write("):[")
            for curFile in symlinks[curKey]:
                f.write("'%s'," % (curFile))
            f.write("],")
    f.write("\n}\n\n")

    f.close()

# vim:ts=4:expandtab:
