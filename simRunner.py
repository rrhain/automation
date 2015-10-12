import config
import argparse
import json
import sys
import os
import re
import logging
import shutil
import glob

version = 1.0
sysVarDB=dict()
traffVarDB=dict()

def genTrafficFiles():

    numToGenForTraffic = 1

    for key,val in config.trafficVars.items():
#        print "{} = {}".format(key, val)
        numToGenForTraffic *= len(val)

    config.numToGenForTraffic = numToGenForTraffic

    step = 1  
    for key, val in config.trafficVars.items():
        toIterate = numToGenForTraffic/(len(val) * step)
        myIndex = 0;

        for x in range(0, toIterate):
            for v in val:
                for s in range(0, step):
                    kindex = myIndex + s; 
                    kstring = str(key) + "|" + str(kindex)
                    traffVarDB[kstring] = v
#                    print ("%s: %s" % (kstring, v))

                myIndex += step; 

        step *= len(val)


def fixTraffic(traffFile, traffSet):

    if(config.debug):
        print("using traffic set %s" % str(traffSet))

    for key, val in sorted(traffVarDB.items()):
        splitVars = key.split("|")

        if(int(splitVars[1]) == int(traffSet)):
            count = 0;
            for line in traffFile:
                if(re.search(splitVars[0], line)):
                    m = re.search("=\s*\{?\s*((MEAN)?\s*=?\s*(?P<mean>\d+)(L?))", traffFile[count])
                    if(m):

                        n = re.match(str(m.group(2)), 'MEAN')
                        if(n):
                            q = re.search("(MEAN\s*=+\s*(?P<mean>\d+)(L?))", traffFile[count])
                            if(q):
                                newMeanString = q.group(0)
                                newMeanString = re.sub(q.groupdict()['mean'], str(val[0]), newMeanString)
                                traffFile[count] = re.sub(q.group(0), newMeanString, traffFile[count])

                            z = re.search("(RANGE\s*=+\s*(?P<range>\d+)(L?))", traffFile[count])
                            if(z):
                                newRangeString = z.group(0)
                                newRangeString = re.sub(z.groupdict()['range'], str(val[1]), newRangeString)
                                traffFile[count] = re.sub(z.group(0), newRangeString, traffFile[count])

                            if(config.debug):
                                print("MEAN/RANGE pair %s" % splitVars[0])



                        else:
                            if(config.debug):
                                print("NOT MEAN/RANGE pair %s" % splitVars[0])
                            traffFile[count] = re.sub(m.groupdict()['mean'], str(val), traffFile[count])


                count = count + 1






def buildScriptDB():
    
    numToGenForVariables = 1

    #figure out how many permutations we need
    for key,val in config.sysVars.items():
#        print "{} = {}".format(key, val)
        for nkey, nval in val.items():
            numToGenForVariables *= len(nval)
    
#    print ("numToGen %s" % numToGenForVariables)
    config.numToGenForVariables = numToGenForVariables

    step = 1;  
    for groupKey, groupVal in config.sysVars.items():

        for simVarKey, simVal in groupVal.items():

            toIterate = numToGenForVariables/(len(simVal) * step)
            index = 0
            myIndex = 0;

#            print ("simVarKey %s" % simVarKey)
            if re.match("(\w+)::(\w+)", simVarKey):
                splitVars = simVarKey.split("::")
 #               print ("MATCHED")
#                print splitVars

                for x in range(0, toIterate):
                    for v in simVal:
                        for s in range(0, step):
                            kindex = myIndex + s; 
                            varIndex = 0
                            for j in splitVars:
                                kstring = str(groupKey) + "|" + str(j) + "|pos"
                                sysVarDB[kstring] = 0
                                kstring = str(groupKey) + "|" + str(j) + "|" + str(kindex)
                                sysVarDB[kstring] = v[varIndex]
#                                print ("%s: %s" % (kstring, v[varIndex]))
                                varIndex = varIndex + 1

                        myIndex = myIndex + step; 
            else:
                for x in range(0, toIterate):
                    for v in simVal:
                        #print ("simVal %s" % v)
                        for s in range(0, step):
                            kindex = myIndex + s; 
                            kstring = str(groupKey) + "|" + str(simVarKey) + "|pos"
                            sysVarDB[kstring] = 0
                            kstring = str(groupKey) + "|" + str(simVarKey) + "|" + str(kindex)
                            sysVarDB[kstring] = v
#                            print ("%s: %s" % (kstring, v))

                        myIndex += step; 

            step *= len(simVal)

def dumpScriptDB():

    print ("\nDUMPING Sys Vars\n")
    for sysKey, sysVal in sorted(sysVarDB.items()):
        print "{} = {}".format(sysKey, sysVal)


def dumpTraffDB():

    print ("\nDUMPING Traff Vars\n")
    for sysKey, sysVal in sorted(traffVarDB.items()):
        print "{} = {}".format(sysKey, sysVal)

def findSimVariablesInShell():

    f = open(config.shellTemplate, "r")
    shakes = f.readlines()
    
    for val in config.sysVars['simShell']:
        if re.match("(\w+)::(\w+)", val):
            splitVars = val.split("::")
#            print ("MATCHED")
#            print splitVars
            for j in splitVars:
                strToMatch = "^" + str(j);
                count=0;
                for line in shakes:
                    if re.match(strToMatch, line):
#                        print line
                        kstring = "simShell" + "|" + str(j) + "|pos"
                        sysVarDB[kstring] = count

                    count = count + 1
        else:
#            print val
            strToMatch = "^" + str(val);
            count = 0
            for line in shakes:
                if re.match(strToMatch, line):
#                    print line
                    kstring = "simShell" + "|" + str(val) + "|pos"
                    sysVarDB[kstring] = count

                count = count + 1


def findSimVariablesInConfig():

    f = open(config.confTemplate, "r")
    shakes = f.readlines()

    for val in config.sysVars['config']:
        if re.match("(\w+)::(\w+)", val):
            splitVars = val.split("::")
#            print ("MATCHED")
#            print splitVars
            for j in splitVars:
                strToMatch = "^" + str(j);
                count=0;
                for line in shakes:
                    if re.match(strToMatch, line):
#                        print line
                        kstring = "config" + "|" + str(j) + "|pos"
                        sysVarDB[kstring] = count

                    count = count + 1
        else:
#            print val
            strToMatch = "^\s*" + str(val) + "\s*=";
            count = 0
            for line in shakes:
                if re.match(strToMatch, line):
#                    print line
                    kstring = "config" + "|" + str(val) + "|pos"
                    sysVarDB[kstring] = count

                count = count + 1
    

    
def printSimFiles():

    f = open(config.shellTemplate, "r")
    shellFile = f.readlines()
    f = open(config.confTemplate, "r")
    cfgFile = f.readlines()

    k = 0;

    for t in range(0, config.numToGenForTraffic):

        if(config.debug):
            print ("using traff %s" % str(t))

        for x in range(0, config.numToGenForVariables):
            k = k + 1
            print ("mkdir run%s" % str(k))

            if(config.debug):
                print ("using parm %s" % str(x))

            curDir = config.outputDir + "/run" + str(k)
            config.logger.debug("populating directory %s" % curDir)
            createSimDirs(curDir, False)
            os.chdir(curDir);
            
            newShFile = open(curDir + "/callSim.sh", "w")
            os.chmod(curDir + "/callSim.sh", 0744)
            
            newCfFile = open(curDir + "/share-conf.cfg", "w")

            for sysKey, sysVal in sorted(sysVarDB.items()):
                
                if(re.match(".*pos$", sysKey)):
                    linePos = sysVal
                    varNames = sysKey.split("|");
                    newKey = sysKey;
                    newKey = newKey.replace("pos", str(x))
#                    print ("Found Position %s " % newKey)
                    
                    if(re.match("simShell", sysKey)):
                        #                    print("Shell Var")
                        #                    print shellFile[linePos]
                        if(isinstance(sysVarDB[newKey], (int, long, float))):
                            m = re.search("=\s*(\d+)", shellFile[linePos])
                            if m:
                                shellFile[linePos] = re.sub(m.group(1), str(sysVarDB[newKey]), shellFile[linePos])

                        elif (isinstance(sysVarDB[newKey], unicode)):
                            m = re.search("=\s*\"(\w+)\s*\"", shellFile[linePos])
                            if m:
                                shellFile[linePos] = re.sub(m.group(1), sysVarDB[newKey], shellFile[linePos])

                        else:
                            print("do not know what kind of variable this is - it is not a string or an integer %s:%s" % newKey, sysVarDB[newKey])
                            sys.exit(0)

                    #                    print shellFile[linePos]
                    


                    elif(re.match("config", sysKey)): 
#                    print("Config")
#                    print cfgFile[linePos]


                        #we really only want to match numbers so list of numbers - we do not deal with list of strings
                        if(isinstance(sysVarDB[newKey], (int, long, float, list))):
                        #matching one of these -         GEM_SRC_INITIAL_INTERVAL = { MEAN = 10000L; RANGE = 5000L };
                            m = re.search("=\s*\{?\s*((MEAN)?\s*=?\s*(?P<mean>\d+)(L?))", cfgFile[linePos])
                            
                            if(m):

                                n = re.match(str(m.group(2)), 'MEAN')
                                if(n):
                                    q = re.search("(MEAN\s*=+\s*(?P<mean>\d+)(L?))", cfgFile[linePos])
                                    if(q):
                                        newMeanString = q.group(0)
                                        newMeanString = re.sub(q.groupdict()['mean'], str(sysVarDB[newKey][0]), newMeanString)
                                        cfgFile[linePos] = re.sub(q.group(0), newMeanString, cfgFile[linePos])

                                    z = re.search("(RANGE\s*=+\s*(?P<range>\d+)(L?))", cfgFile[linePos])
                                    if(z):
                                        newRangeString = z.group(0)
                                        newRangeString = re.sub(z.groupdict()['range'], str(sysVarDB[newKey][1]), newRangeString)
                                        cfgFile[linePos] = re.sub(z.group(0), newRangeString, cfgFile[linePos])

                                    if(config.debug):
                                        print("MEAN/RANGE pair %s" % newKey)

                                else:
                                    cfgFile[linePos] = re.sub(m.groupdict()['mean'], str(sysVarDB[newKey]), cfgFile[linePos])

                        #single substitution for strings
                        elif (isinstance(sysVarDB[newKey], unicode)):
                            m = re.search("=\s*\"(\w+)\s*\"", shellFile[linePos])
                            if m:
                                cfgFile[linePos] = re.sub(m.group(1), sysVarDB[newKey], cfgFile[linePos])


                        else:
                            print("do not know what kind of variable this is - it is not a string or an integer %s:%s" % newKey, sysVarDB[newKey])
                            sys.exit(0)

#                    print cfgFile[linePos]

            newShFile.writelines( "%s" % item for item in shellFile)

            #fix traffic here - may want to deal with traffic differently for other simulations - but here we  edit the cfg

            fixTraffic(cfgFile, t)

            newCfFile.writelines( "%s" % item for item in cfgFile)
        



def genScriptFiles(doSetup):

#    print ("Current date & time = %s" % config.now)
    buildScriptDB()

    findSimVariablesInShell()
    findSimVariablesInConfig()

    if(config.debug):
        dumpScriptDB()

    genTrafficFiles()

    if(config.debug):
        dumpTraffDB()

    #now we look at topologies and script files

    #if($trafficFlag =~ /existsMulticast/)
    #{
#	getMcastTrafficFiles();
#    }
#    elsif ($trafficFlag =~ /existsUnicast/)
#    {
#	getUniTrafficFiles();
#    }
#    elsif ($trafficFlag =~ /genMulticast/)
#    {
#	genMcastTrafficFiles();
#    }
#    elsif ($trafficFlag =~ /genUnicast/)
#    {
#	genUniTrafficFiles();
#    }
#    elsif ($trafficFlag =~ /scenarios/)
#    {
#	getScenarioTrafficFiles();
#    }
#    elsif ($trafficFlag =~ /templateUnicast/)
#    {
#	genUniTrafficFilesFromTemplate();
#    }

#    if($topoFlag =~ /exists/)
#    {
#	getPathLossFiles();
#    }
#    elsif($topoFlag =~ /scenarios/)
#    {
#	getScenarioTopoFiles();
#    }
#    elsif($topoFlag =~ /generate/)
#    {
#	genPathLossFiles();
#    }

    if(doSetup):
        print("setting up")
        printSimFiles()


def createSimDirs(curDir, interactive):

    regex = re.compile(r'y(es)?$', flags=re.IGNORECASE)

    if(interactive):
        print("%s does not exist." % curDir)
        resp = raw_input("Create it? <y or n>")
    else:
        resp = "y"
    
    if regex.match(resp):
        try:
            os.makedirs(curDir, mode=0775)
        except OSError:
            if os.path.isdir(curDir):
                # We are nearly safe
                pass
            else:
                # There was an error on creation, so make sure we know about it
                raise
    else:
        sys.exit(0)




def checkInput():

    print("Checking input and existence of directories");

    if os.path.isdir(config.simulationsRoot):

        print("%s exists. No need to create." % config.simulationsRoot)

    else:
        createSimDirs(config.simulationsRoot, True)


    if os.path.isdir(config.outputDir):

        print("%s exists. No need to create." % config.outputDir)

    else:
        createSimDirs(config.outputDir, True)


    if os.path.isfile(config.simInfoFile):
        print("%s exists. No need to create." % config.simInfoFile)
        config.doSetup = False

    else:
        fh = logging.FileHandler(config.simInfoFile)
        fh.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        config.logger.addHandler(fh)

        config.logger.setLevel(logging.DEBUG)
        config.logger.debug('Setting up sim')

    if not os.path.isfile(config.shellTemplate):
        print("%s does not exist. Please provide a valid one." % config.shellTemplate)
        sys.exit(0)


    if not os.path.isfile(config.confTemplate):
        print("%s does not exist. Please provide a valid one." % config.confTemplate)
        sys.exit(0)


#    if not os.path.isfile(config.simExecutable):
#        print("%s does not exist. Please provide a valid one." % config.simExecutable)
#        sys.exit(0)


def runAggregateResult():
    #run it on config.outputDir
    if(config.debug):
        print("in runAggregateResult running over %s" % config.outputDir)

    #create emtpy header
    runOneFile = open(config.outputDir + "/run1/resLine", "r")
    resFile = runOneFile.readlines()
    aggFile = config.outputDir + "/aggSimResults"

    f = open(aggFile, "w")
    f.writelines(resFile[0])

    allNames = glob.glob(config.outputDir + "/run*/resLine")    

    for resF in allNames:
        a = open(resF, "r")
        resFile = a.readlines()
        f.writelines(resFile[-1])

def runResult(curDir):
    inVarDB=dict()

    f = open("./callSim.sh", "r")
    shellFile = f.readlines()
    f = open("./share-conf.cfg", "r")
    cfgFile = f.readlines()

    aName = glob.glob("./output/analysis*.txt")
    f = open(aName[0], "r")
    anFile = f.readlines()

    if(config.debug):
        print("in runResult %s" % curDir)


    resFile = curDir + "/resLine"
    res = open(resFile, "w")

    hdrLine = ""
    valLine = ""
    for key, val in config.plotVars.items():
        for nkey, nval in val.items():
            posKey = key + "|" + nkey + "|pos"

            if(config.debug):
                print posKey
                print "value is ", sysVarDB[posKey]

            if(re.match(key, "simShell")):
                #print shellFile[sysVarDB[posKey]]
                m = re.search("=\s*(?P<inVal>\d+)", shellFile[sysVarDB[posKey]])
            else:
                #print cfgFile[sysVarDB[posKey]]
                m = re.search("=\s*\{?\s*((MEAN)?\s*=?\s*(?P<inVal>\d+)(L?))", cfgFile[sysVarDB[posKey]])

            inVarDB[nval] = 0
            if (m):
                inVarDB[nval] = m.groupdict()['inVal']


    if(config.debug):
        print ("\nDUMPING In Vars\n")
        for sysKey, sysVal in sorted(inVarDB.items()):
            print "{} = {}".format(sysKey, sysVal)

    for h in config.plotInHdr:
        hdrLine = hdrLine + h + "\t"
        valLine = valLine + str(inVarDB[h]) + "\t"

    for h in config.plotOutHdr:
        hdrLine = hdrLine + h + "\t"

    hdrLine = hdrLine + "\n"
    anFile[-1] = re.sub("\s+", "\t", anFile[-1])
    valLine = valLine + anFile[-1]
    valLine = valLine + "\n"

    if(config.debug):
        print hdrLine
    res.writelines(hdrLine)


    if(config.debug):
        print valLine
    res.writelines(valLine)

def runSims():
    numberSims = 0

    for f in os.listdir(config.outputDir):
        if(re.match("run", f)):
            numberSims = numberSims + 1

    config.numberSims = numberSims

    if(numberSims > 0):  #just making sure there is something to run

        for i in range(1, numberSims+1):
            curDir = config.outputDir + "/run" + str(i)
            os.chdir(curDir)

            #not generic - but needed for this simulation framework
            for d in ["analysis", "scenarios", "stats", "wireshark"]:
                #print config.srcRoot + "/" + d
                os.symlink(config.srcRoot + "/" + d, curDir + "/" + d)

            
            print("running sim %s" % curDir)
            cmdString = "./callSim.sh"

            os.system(cmdString)

            runResult(curDir)

            if(config.keep == False):
                if(config.debug):
                    print("deleting files")

                try:
                    os.remove("last/out");
                    os.remove("last/output.tgz");
                    os.remove("last/trace-all-sim.pcap");
                except OSError as e:
                    print "OSError [%d]: %s at %s" % (e.errno, e.strerror, e.filename)
                    pass
                except:
                    raise()
            else:
                if(config.debug):
                    print("keeping files")


if __name__ == "__main__":


    parser = argparse.ArgumentParser(description='reads input configuration file, generates topologies, traffic files, customized runsim.sh and config files')
    parser.add_argument('-s', '--setup', action='store_true', help='setup directories and run files' )
    parser.add_argument('-r', '--runsims', action='store_true', help='run the simulations')
    parser.add_argument('-p', '--plot', action='store_true', help='plot graphs based on these sims' )
    parser.add_argument('-d', '--debug', action='store_true', help='debug mode' )
    parser.add_argument('-k', '--keep', action='store_true', help='keep large output files - default is to delete them' )
#    parser.add_argument('-o', '--outfile', action='store', dest='o', help='Results - output file name')
#    parser.add_argument('-a', '--all', action='store_true', help='turn on plotting and degrees flags when tStamp = -1' )

    parser.add_argument('configFile', help='Configuration file for simulation run')

    args = parser.parse_args()

    #get the present working directory
    currentDir = os.getcwd()

    siminfoFile = "$outputDir/siminfo";

    config.initialize(args.configFile)

    config.doSetup = args.setup
    config.debug = args.debug
    config.keep = args.keep

    checkInput()


    genScriptFiles(args.setup)

    runSims()

    runAggregateResult()


