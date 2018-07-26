#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DLC2.3 running code
# 
#
# Authors: Hao BAI (hao.bai@insa-rouen.fr)
# Version: 0.0
# Date: 25/07/2018
#
# Comments:
#     - 0.0: 
#
# Description:
# Combine wind condition EOG with loss of grid at different moment
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



#-----------------------------------------------------------------------------------------
#                                        MODULES
#-----------------------------------------------------------------------------------------
#============================== Modules Communs ==============================
import os, re, numpy, time
import fileinput # iterate over lines from multiple input files
import shutil # high-level file operations
import subprocess # call a bash command e.g. 'ls'
from contextlib import contextmanager
#============================== Modules Personnels ==============================



#-----------------------------------------------------------------------------------------
#                                    CLASS DEFINITION
#-----------------------------------------------------------------------------------------
@contextmanager
def cd(newdir):
    prevdir = os.getcwd() # save current working path
    os.chdir(os.path.expanduser(newdir)) # change directory
    try:
        yield
    finally:
        os.chdir(prevdir) # revert to the origin workinng path


class DLC(object):
    """docstring for DLC"""
    def __init__(self, wind='', gridLossTime=[], outputFolder='/', toLog=False):
        self.wind =  wind
        self.time = {'start':gridLossTime[0],'end':gridLossTime[1],'step':gridLossTime[2]}
        self.outputFolder = outputFolder
        self.toLog = toLog
        # some fixed path
        self.__outputPath = os.path.expanduser(
                                     '~/Eolien/Parameters/NREL_5MW_Onshore/Output/DLC2.3')
        self.__fstPath = os.path.expanduser('~/Eolien/Parameters/NREL_5MW_Onshore')
        self.__prefix = '/DLC2.3_'
        self.__servodyn = os.path.expanduser(
                            '~/Eolien/Parameters/NREL_5MW_Onshore/WT/ServoDyn_DLC2.3.dat')

    def run(self, loop=False):
        if loop:
            for t in numpy.arange(self.time['start'], self.time['end']+self.time['step'],
                                  self.time['step']):
                print("|- Simulating loss of grid at", t,"s ...")
                self.change_gridloss(t)
                self.__fast(False)
                print(os.getcwd())
                # self.move_and_rename(t)
                print("|- [ OK ] Output file has been moved to {} folder !"
                      .format(self.outputFolder))
        else:
            self.__fast()


    def move_and_rename(self, time):
        shutil.move(self.__fstPath+self.__prefix+self.wind+'.out',
                   self.__outputPath+self.outputFolder+'/'+self.wind+'/'+str(time)+'.out')

    def change_gridloss(self, time):
        with fileinput.input(self.__servodyn, inplace=True, backup='.bak') as f:
            for line in f:                
                if "TPitManS" in line:                    
                    print(self.__replace(line, "TPitManS", time+0.2), end="")
                elif "TimGenOf" in line:
                    print(self.__replace(line, "TimGenOf", time), end="")
                else:
                    print(line, end="")

    def __replace(self, string, keyword, value):
        position = string.find(keyword)
        substring = string[:position]
        # replace float number (e.g. )
        newtime = re.sub('[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)', str(value), substring)
        newline = newtime + string[position:]
        return newline

    def __fast(self, silence=False):            
        with cd('~/Eolien/FAST'):
            # command = 'fast {}{}{}.fst'.format(self.__fstPath, self.__prefix, self.wind)
            command = './FAST_gdar64 {}{}{}.fst'.format(self.__fstPath, self.__prefix, self.wind)
            if silence:
                # print("|- Running FAST in silence mode ...")
                subprocess.check_output([os.getenv('SHELL'), '-i', '-c', command])
            else:
                print("|- Running FAST ...")
                # a = subprocess.check_output([os.getenv('SHELL'), '-i', '-c', command])
                # print(a)
                print(os.getcwd())
                subprocess.call([command], shell=True)
                subprocess.call([command], shell=True)
                #When shell=False, args[:] is a command line to execute
                #When shell=True, args[0] is a command line to execute and args[1:] is arguments to sh

                # subprocess.call([os.getenv('SHELL'), '-i', '-c', 'exit'])
                # subprocess.call([command])


                
#-----------------------------------------------------------------------------------------
#                                  FUNCTION DEFINITION
#-----------------------------------------------------------------------------------------



#-----------------------------------------------------------------------------------------
#                                     MAIN FUNCTION
#-----------------------------------------------------------------------------------------
def main():
    simu1 = DLC(wind='EOGR', gridLossTime=[110, 140.5, 20], outputFolder='/withoutTRD')
    simu1.run(True)
    # simu1.change_gridloss()


#-----------------------------------------------------------------------------------------
#                                      RUNNING TEST
#-----------------------------------------------------------------------------------------
if __name__ == '__main__':
        main()
