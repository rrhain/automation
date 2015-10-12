#!/usr/bin/perl5

# initialize application specific variables
# locations of files and directories

#USER - modify these variables to get started
#pirana_root, simDir (top-level place for sims), outputDir
#PIRANA root directory
$pirana_root = "/home/rrosales/PIRANA-current";

#OPNET root directory
$opnet_root = "$pirana_root/pirana-opnet";

#sandbox directory
$sandbox = "$opnet_root/sandbox";

#place to put simulation runs
$simDir = "/wand/rrosales/army-test-sims";

#place to put simulation runs and scripts
$scriptDir = "$opnet_root/scripts";

#simulation executable you want to run 
$simExecutable = "$sandbox/runpirana.sh";

#executable to run in each directory for result
$dirResultsExecutable = "$scriptDir/analyze.pl";

#executable to run to aggregate results for all directories
$allResultsExecutable = "$scriptDir/doGenPlot.pl";

#template pctl file to base the simulation run on
$pctlTemplate = "./pirana-config.pctl";

#opnet ef template file to base the simulation run on
$efTemplate = "./opnet-config.ef";

#reasoner policy file - gets copied into directory by runpirana.sh itself
#$policyFile = "$pirana_root/dsa/policies/opnet20.owl";

#NUMBER OF NODES FOR SIMS
@nodes = (4);

#SIMULATION DIRECTORY and DESCRIPTION
@useDate = localtime(time);

#uncomment and use date if too lazy to come up with a name
#$outputDir = $simDir."/".($useDate[5]+1900)."-".($useDate[4] + 1)."-".$useDate[3]."-".$useDate[2]."-".$useDate[1];

#or give something more understandable
$outputDir = "$simDir/n4_test4";

#and give a description of the reason for the simulation stored in file siminfo
$simDescription = "Running army test cases - Test Case 0";

$testCartelPrefix = "\$PIRANA_BUILD";

#Files for TOPOLOGY AND TRAFFIC need to have a number in its name
#Optionally, file names have a convention of having pairs of TOKEN-VAL
#delimited by _.  The TOKEN-VAL is to identify important parameters 
#about the file
#n10_S-0_BB-223_D-0.000200_0.mo --> Speed=0, BoundingBox = 223x223, 
#                                   Density =0.00200
#n10m_L-1_G-10_P-100_NG-2.gdf--> Load=1, GroupSize=10, PacketSize=100, 
#                                  NumberGroups=2
#The token is passed to analyze.pl with its value in case we wanted 
#these input values for plotting
#i.e.analyze.pl out -s --nameVal Speed=0 --nameVal Load=1 --nameVal TopoGroup=8 

##############################################################
#TOPOLOGY SPECIFICATION
#place to put or find pathloss files
$pathLossDir = "$opnet_root/pathloss_army";

#You can specify how to get topology in 3 different ways
#topoFlag = {generate, exists, scenarios} 

#Below is a section with parameters for each method
#Uncomment the topoFlag you want to use and make sure
#that the parameter block corresponding to the method
#has valid parameters

#$topoFlag = 'generate';
$topoFlag = 'exists';
#$topoFlag = 'scenarios';

#1 - generate the pathloss files, can do R4, R2, and FixedDropoff
#    If generating, all you need is to uncomment generate and fill in the
#    params

#topoFlag = 'generate';
#parms for generating topologies
#pathloss_model = {R4, FixedDropoff, R2} 
@pathloss_model = (FixedDropoff);
@density = (30);
@duration = (660);
@speed = (0);
#need to specify different seeds if you want a number of samples
#@psamples = (123445, 20120, 322223);
@pseeds = (rand());


#2 - exists
#    If you have pathloss files that exist which you want to use
#@topoFiles = ("n250_S-0_BB-1118_D-0.000200_1.mo");
#@topoFiles = ("n40_S-0_BB-447_D-0.000200_0.mo");
@topoFiles = ("n4_circle_army4_Y-0.mo", "n4_circle_army4_Y-1.mo", "n4_circle_army4_Y-2.mo", "n4_circle_army4_Y-3.mo");


#3 - scenario style
#directory for a scenario you may want to run parameter study for
#if $topoFlag == scenarios || $trafficFlag == scenarios
#this is for running with trajectory files rather than pathloss files
#really geared for running simulations for demo scenarios
#the expectation is all files for the scenario live in a directory
#different mode of operation than with multicast, here you can run more than
#one traffic file from the directory
#expectation is to be running topo and traffic from scenario, but it doesn't 
#have to be run that way
#topoFlag = 'scenarios';
$scenarioDir = "$opnet_root/scenarios/oct2009-10nodes";


#TOPOLOGY SPECIFICATION END
##############################################################

##############################################################
#TRAFFIC SPECIFICATION
#You can specify how to get traffic files in 4 different ways
#trafficFlag = {existsUnicast, existsMulticast, genUnicast, genMulticast, 
#scenarios } 

#Below is a section with parameters for each method
#Uncomment the topoFlag you want to use and make sure
#that the parameter block corresponding to the method
#has valid parameters

#for these multicast runs, we only have traffic files and don't need pctl node files
#multicast group information is covered in the pirana-config.pctl - all nodes belong
#to 1 group - so run it as if unicast traffic is what we need
$trafficFlag = 'existsUnicast';
#$trafficFlag = 'existsMulticast';
#$trafficFlag = 'genUnicast';
#$trafficFlag = 'genMulticast';
#$trafficFlag = 'scenarios';


#1 - existsUnicast
#trafficFlag = 'existsUnicast';
#directory to get or put generated unicast traffic files
$trafficDir = "$opnet_root/traffic_army";
#unicast files and scenario files if $trafficFlag == existsUnicast 
@utraffFiles = (
"n4m_L-25_G-4_PS-64_T-0.gdf",
"n4m_L-25_G-4_PS-250_T-0.gdf",
"n4m_L-25_G-4_PS-576_T-0.gdf",
"n4m_L-25_G-4_PS-1300_T-0.gdf",
"n4m_L-50_G-4_PS-64_T-0.gdf",
"n4m_L-50_G-4_PS-250_T-0.gdf",
"n4m_L-50_G-4_PS-576_T-0.gdf",
"n4m_L-50_G-4_PS-1300_T-0.gdf",
"n4m_L-75_G-4_PS-64_T-0.gdf",
"n4m_L-75_G-4_PS-250_T-0.gdf",
"n4m_L-75_G-4_PS-576_T-0.gdf",
"n4m_L-75_G-4_PS-1300_T-0.gdf",
"n4m_L-100_G-4_PS-64_T-0.gdf",
"n4m_L-100_G-4_PS-250_T-0.gdf",
"n4m_L-100_G-4_PS-576_T-0.gdf",
"n4m_L-100_G-4_PS-1300_T-0.gdf",
"n4m_L-150_G-4_PS-64_T-0.gdf",
"n4m_L-150_G-4_PS-250_T-0.gdf",
"n4m_L-150_G-4_PS-576_T-0.gdf",
"n4m_L-150_G-4_PS-1300_T-0.gdf",
"n4m_L-200_G-4_PS-64_T-0.gdf",
"n4m_L-200_G-4_PS-250_T-0.gdf",
"n4m_L-200_G-4_PS-576_T-0.gdf",
"n4m_L-200_G-4_PS-1300_T-0.gdf",
"n4m_L-300_G-4_PS-64_T-0.gdf",
"n4m_L-300_G-4_PS-250_T-0.gdf",
"n4m_L-300_G-4_PS-576_T-0.gdf",
"n4m_L-300_G-4_PS-1300_T-0.gdf",
"n4m_L-400_G-4_PS-64_T-0.gdf",
"n4m_L-400_G-4_PS-250_T-0.gdf",
"n4m_L-400_G-4_PS-576_T-0.gdf",
"n4m_L-400_G-4_PS-1300_T-0.gdf",
"n4m_L-500_G-4_PS-64_T-0.gdf",
"n4m_L-500_G-4_PS-250_T-0.gdf",
"n4m_L-500_G-4_PS-576_T-0.gdf",
"n4m_L-500_G-4_PS-1300_T-0.gdf",
"n4m_L-600_G-4_PS-64_T-0.gdf",
"n4m_L-600_G-4_PS-250_T-0.gdf",
"n4m_L-600_G-4_PS-576_T-0.gdf",
"n4m_L-600_G-4_PS-1300_T-0.gdf",
"n4m_L-700_G-4_PS-64_T-0.gdf",
"n4m_L-700_G-4_PS-250_T-0.gdf",
"n4m_L-700_G-4_PS-576_T-0.gdf",
"n4m_L-700_G-4_PS-1300_T-0.gdf",
);


#2 - existsMulticast
#trafficFlag = 'existsMulticast';
#multicast traffic directories if $trafficFlag == existsMulticast
#@mtraffDirs = ("$opnet_root/automation/sims/test-4/traff0");
@mtraffDirs = ("/wand/rrosales/pirana-sims/n5_h_md/traff0");
#should be 1 file per directory specified
@mtraffFiles = ("n5m_L-10_G-5_P-260_FL-30.gdf");


#3 - generating: genUnicast or genMulticast
#trafficFlag = 'genUnicast';
#trafficFlag = 'genMulticast';

#traffic parameters if generating multicast and unicast
#seconds
$startTime = 300;
$endTime = 600;
$simDuration = 660;
#kbps
@loads = (25, 50, 75, 100, 150, 200, 300, 400, 500, 600, 700); 
#bytes
@packetSize = (64, 250, 576, 1300);

#unicast specific template
$transport = 'UDP';
$traffType = 'unicast';
@tseeds = (1);

#gen_ivox multicast params
#number in multicast group
@groupSize = (2);
#number of multicast groups
$numGroups = 25;
#kbps
$multicastRate = 6.25;
#seconds
@flowLength = (30);
$trafficTOS = 0;


#4 - scenarios
#trafficFlag = 'scenarios'
#scenarioDir = SEE SPECIFIED IN TOPOLOGY SECTION
#all traffic files to be run for the scenarios
@traffFiles = ("n10u_L-1_PS-100.gdf", "n10u_L-100_PS-100.gdf");
#TRAFFIC SPECIFICATION END
##############################################################


#some way to limit the header names for the plotter
#only directory entries here are included in the --nameVal output
#of analyze.pl  
#value on the left is mapped to name on the right
#left hand values are tokens from names of the pathloss file or traffic file
#or from the variables we are iterating over
%wantedPlotVars = (
		   "L" => "Load",
		   "PS" => "Size",
		   "S" => "Speed",
                   "G" => "GrpSize",
                   "NG" => "NumGrps",
                   "C" => "C",
                   "D" => "Dens",
                   "T" => "TOS",
		   "LMFAUseBlanketAssignment" => "BlnkOn",
		   "LMHBInterval" => "HBs",
		   "DSA_DoSensing" => "DSAs",
 		   "PktMgmtRTSThresholdBytes" => "RTSTh",
#                   "AcessDataCWMin" => "CWMin",
#                   "AccessDataCWMax" => "CWMax",
#                   "AccessCWMultIncreaseNumerator" => "Numr",
#                   "AccessCWBcastAddDecrease" => "Decr",                   
#                   "RRIgnoreRPFCheckForLocalDelivery" => "RFCck",
#                   "LMFAAssignedFreqSeparationKHz" => "sep",
#                   "PktMgmtMaxReliableMcastXmitAtts" => "XReps",
#	           "LMFAAllowedNumOneHopNbrsPerChannel" => "ClkSize",
		   "TMRGMcastTxBcastBranchThreshold" => "BR",
		   "TMRGTosDefaultFwdTable" => "FT",
		   "SYSMGR_MACNumXcvrs" => "NXcvrs",
		   "SYSMGR_MACPhyDataRateKbs" => "Rate",
		   "SYSMGR_MACPhyCCADelayTicks" => "CCADelay");


#sys_vars is defined to be arrays within arrays
#in the sys.scr files, variables of the form group.var should
#be specified inside the array as 
#    group => {
#       var => [....., ....],
#    },
#variables that should be grouped should be defined var1::var2....
#	pctl => {
#	    SYSMGR_MACNumXcvrs => [1, 2, 3, 4],
#            SYSMGR_MACPhyDataRateKbs::SYSMGR_MACMacPhyDelayTicks::SYSMGR_MACPhy
#MacDelayTicks::SYSMGR_MACPhyCCADelayTicks::SYSMGR_MACFrameHdrSizeBytes =>[[2000, 100, 100, 20, 16], [10000, 5, 5, 5, 16], [2000, 400, 400, 100, 16]],
#	},
#	opnet => {
#	    PCTLPeriodicQueryRate => [250],
#	},
#

#Variables you are modifying need to exist in your pirana-config.pctl file
#and in your opnet-config.ef file - you can leave opnet commented if you aren't
#using it, but the functionality is supported
%sys_vars = (
	pctl => {
#	    SYSMGR_MACPhyDataRateKbs::SYSMGR_MACMacPhyDelayTicks::SYSMGR_MACPhyMacDelayTicks::SYSMGR_MACPhyCCADelayTicks::SYSMGR_MACFrameHdrSizeBytes =>[[10000, 5, 5, 5, 16]],
#	    LMFAAllowedNumOneHopNbrsPerChannel => [50, 6],
#	    SYSMGR_MACPhyDataRateKbs => [1181],
	    SYSMGR_MACNumXcvrs => [1, 2],
	    PktMgmtRTSThresholdBytes => [1, 1000, 1600],
#	    DSA_DoSensing => [0, 1],
#	    LMHBInterval => [1000, 2000, 3000],
#	    TMRGMcastTxBcastBranchThreshold => [0, 1], 
#	    TMRGTosDefaultFwdTable => [1, 2],
#	    AccessDataCWMin::AccessDataCWMax => [[50,400]],      
#	    AccessCWMultIncreaseNumerator => [3,4,5],
#	    AccessCWBcastAddDecrease => [1,10000],
#           PktMgmtMaxReliableMcastXmitAtts => [1,2,3],
#           LMFAAssignedFreqSeparationKHz => [0],
#	   AccessAdaptCWMaxToNbrHoodSize => [0],
	},
	opnet => {
	    PCTLPeriodicQueryRate => [50],
	},
);



