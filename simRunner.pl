#!/usr/bin/perl

use Sys::Hostname;
use POSIX qw/strftime/;

$host = hostname();

$configFile = shift(@ARGV);

#program version number
$version = "1.0";

# Establish some default values in case these are not set in the
# config file

# should we generate the files/directories for all of the runs?
$doSetup = 1;

# should we actually run simulations?
$doSims = 1;

#ENV variables to change
#$mypath = $ENV{'PATH'};
#$ENV{'PATH'} = '$mypath:';

@description="    reads input configuration file, generates topologies, " .
	     "traffic files,\n    customized pirana-config.pctl, ". 
             "and opnet-config.ef\n    and runs the simulations.";

if($configFile eq "" || ! -e $configFile)
{
    printf("simRunner.pl: Invalid arguments ($configFile)\n");
    usage();
}

@plotArgs = ();
#get the present working directory
$cdir = $ENV{'PWD'};

#read in configuration file
$@ = '';
do("$configFile");
$@ && die "$0: Bad configuration in $configFile: $@\n";

$siminfoFile = "$outputDir/siminfo";

#check that input is sane
checkInput();

#generate the Script files and directories for the runs
genScriptFiles();

if($doSims)
{
    #run the simulations
    runSimulations();
}

#getResults if run at the end
#currently running after each sim - so called
#at the end of runSimulations
#runResultScripts();

logMsg("SUCCESS");

#go back to what was the pwd 
chdir("$cdir");

sub logMsg
{
    my($msgArg) = shift;

    # add timestamp and hostname at the beginning of the message
    my($t) = strftime('%d-%b-%Y %T', localtime);
    my($msg) = "$t $host: $msgArg\n";

    # Log msg to the siminfo file.  Since multiple machines may be
    # logging to this file, we open it for append, log to it, and
    # close it.  The alternative would be to keep it open, and always
    # seek to the end before writing.  I'm guessing that the former
    # method plays nicer with NFS, but I'm not really sure.
    open(SIMINFO, ">>$siminfoFile") || die("could not open $siminfoFile: $!");
    print SIMINFO $msg;
    close(SIMINFO);

    # log to stdout
    print $msg;

    # if CLAIM is a valid file handle, log there too
    fileno(CLAIM) && print CLAIM $msg;
}

#Generate the script files
#We build the variable database stating which variable should be 
#what value for each run, look for the variables to modify in the
#script file, and then print the script files
sub genScriptFiles
{

    buildScriptDB();

    findSimVariablesInPctl();
    findSimVariablesInEf();

    if($trafficFlag =~ /existsMulticast/)
    {
	getMcastTrafficFiles();
    }
    elsif ($trafficFlag =~ /existsUnicast/)
    {
	getUniTrafficFiles();
    }
    elsif ($trafficFlag =~ /genMulticast/)
    {
	genMcastTrafficFiles();
    }
    elsif ($trafficFlag =~ /genUnicast/)
    {
	genUniTrafficFiles();
    }
    elsif ($trafficFlag =~ /scenarios/)
    {
	getScenarioTrafficFiles();
    }
    elsif ($trafficFlag =~ /templateUnicast/)
    {
	genUniTrafficFilesFromTemplate();
    }

    if($topoFlag =~ /exists/)
    {
	getPathLossFiles();
    }
    elsif($topoFlag =~ /scenarios/)
    {
	getScenarioTopoFiles();
    }
    elsif($topoFlag =~ /generate/)
    {
	genPathLossFiles();
    }

#    all debugging things
#    &printSimVariableDatabase;

#    &printTopoDatabase;

#    &printLinesToModify;

#this creates the directories and files
    if($doSetup)
    {
	printScriptFiles();
    }
    else
    {
	dupScriptFiles();
    }
}

#Build the variable database stating which variable should be what
#value for each run
sub buildScriptDB
{
    $numToGenForVariables = 1;

    foreach $groupVar (keys %sys_vars)
    {
	foreach $sysVar (keys %{$sys_vars{$groupVar}})
	{
#            print("group = $groupVar,  sysVar = $sysVar \n"); 
	    @valueArrays = @{$sys_vars{$groupVar}{$sysVar}};
	    $numToGenForVariables *= @valueArrays;
	}
    }
#    print ("num to generate $numToGenForVariables\n");
    
    $step = 1;  
    foreach $groupVar (keys %sys_vars)
    {
	foreach $sysVar (keys %{$sys_vars{$groupVar}})
	{
	    @valueArrays = @{$sys_vars{$groupVar}{$sysVar}};
            $valueArraysLength = @valueArrays;
            $toIterate = $numToGenForVariables/($valueArraysLength * $step) ;
            $myIndex = 0;
            if($sysVar =~ /::/)
	    #means we have variables that are meant to be run as a group
	    #per simulation
	    {
		@varNames = split(/::/, $sysVar);
		for($k = 0; $k < $toIterate; $k++) 
		{
		    for($i = 0 ; $i < $valueArraysLength; $i++) 
		    {
			@valueArraySet = @{$valueArrays[$i]};
                        for($s = 0; $s < $step; $s++)
                        {
                            $kindex = $myIndex + $s; 
			    for($j = 0 ; $j < @varNames; $j++)
			    {
#			       print("$groupVar|$varNames[$j]: $valueArraySet[$j], kindex=$kindex\n");
			       $sysVarDB{$groupVar."|".$varNames[$j]."|pos"} = "";
			       $sysVarDB{$groupVar."|".$varNames[$j]."|$kindex"} = 
				   $valueArraySet[$j];
			    }
                         }
                         $myIndex += $step; 
		    }
		}
	    }
	    else
	    {
                for($k = 0; $k < $toIterate; $k++) 
                {
                    foreach $sysVal (@valueArrays)
                    {
                        for($s = 0; $s < $step; $s++) 
                        {
                            $kindex = $myIndex + $s;  
#                            print ("$groupVar|$sysVar = $sysVal, kindex = $kindex\n");
                            $sysVarDB{$groupVar."|".$sysVar."|pos"} = "";
                            $sysVarDB{$groupVar."|".$sysVar."|$kindex"} = $sysVal;
                         }  
                         $myIndex += $step;  
                    }    
                }   
	    }
            $step *= $valueArraysLength; 
	}
    }
}

#search the script file and store all the variable locations to
#be changed 
sub findSimVariablesInPctl
{
    open(INFO, "<$pctlTemplate");       # Open the file
    @scrLines = <INFO> ;                     # Read it into an array
    close(INFO);
    $pctlLines = scalar(@scrLines);

    #checking if in the file, otherwise we throw the line at the end
    $i = $pctlLines + 1;
    foreach $kword (keys %{$sys_vars{pctl}})
    {
	if($kword =~ /::/) 
	{
	    @varNames = split(/::/, $kword);
	    foreach $v (@varNames) 
	    {
		$nstring = "pctl|".$v."|pos";
		$sysVarDB{$nstring} = $i;
		$i++;
	    }
	}
	else 
	{
	    $nstring = "pctl|".$kword."|pos";
	    $sysVarDB{$nstring} = $i;
	    $i++;
	}
    }

    $i = 0;
    foreach $line (@scrLines) 
    {
	foreach $kword (keys %{$sys_vars{pctl}})
	{
	    #print ("t-$kword\n");
	    if($kword =~ /::/) 
	    {
		@varNames = split(/::/, $kword);
		foreach $v (@varNames) 
		{
		    if($line =~ /^set.*$v/)
		    {
#			print ("IN PCTL - $v at line:$i\n");
			$nstring = "pctl|".$v."|pos";
			$sysVarDB{$nstring} = $i;
		    }
		}
	    }
	    else 
	    {
		if($line =~ /^set.*$kword/)
		{
#		    print ("IN PCTL - $kword at line:$i\n");
		    $nstring = "pctl|".$kword."|pos";
		    $sysVarDB{$nstring} = $i;
		}
	    }

	}
	$i++;
    }
}

sub findSimVariablesInEf
{
    open(INFO, "<$efTemplate");       # Open the file
    @scrLines = <INFO> ;                     # Read it into an array
    close(INFO);

    $pctlLines = scalar(@scrLines);

    #checking if in the file, otherwise we throw the line at the end
    $i = $pctlLines + 1;
    foreach $kword (keys %{$sys_vars{opnet}})
    {
	if($kword =~ /::/) 
	{
	    @varNames = split(/::/, $kword);
	    foreach $v (@varNames) 
	    {
		$nstring = "opnet|".$v."|pos";
		$sysVarDB{$nstring} = $i;
		$i++;
	    }
	}
	else 
	{
	    $nstring = "opnet|".$kword."|pos";
	    $sysVarDB{$nstring} = $i;
	    $i++;
	}
    }

    $i = 0;
    foreach $line (@scrLines) 
    {
	foreach $kword (keys %{$sys_vars{opnet}})
	{
	    #print ("t-$kword\n");
	    if($kword =~ /::/) 
	    {			
		@varNames = split(/::/, $kword);
		foreach $v (@varNames) 
		{
		    if($line =~ /^$v\s*:/)
		    {
#			print ("IN OPNET - $v at line:$i\n");
			$nstring = "opnet|".$v."|pos";
			$sysVarDB{$nstring} = $i;
		    }
		}
	    }
	    else
	    {
		if($line =~ /^$kword/)
		{
#		    print ("IN OPNET - $kword at line:$i\n");
		    $nstring = "opnet|".$kword."|pos";
		    $sysVarDB{$nstring} = $i;
		}
	    }
	}
	$i++;
    }
}

sub genPathLossFiles
{

    logMsg("Generating PathLoss Files");

    #generate_pathloss actually does its own random seed based on time
    #so for now lseed is a sample number
    $curTopoCount = 0;
    $topoDB{"topo_num"} = @pathloss_model * @density * @nodes * @duration * @speed * @pseeds;
    for($m = 0; $m < @pathloss_model; $m++)  
    {
	for ($d = 0; $d < @density; $d++) 
	{
	    for($n = 0; $n < @nodes; $n++) {
		
		#conver to m^2 because it's what gen pathloss expects
		$size = int(sqrt($nodes[$n]/($density[$d]*0.000001)));

		for($l = 0; $l < @duration; $l++) 
		{

		    for ($s=0; $s< @speed; $s++) 
		    {

			for($sd = 0; $sd < @pseeds; $sd++) 
			{
			    #print "$n, $s";
			    $fdens = sprintf("%.1f", $density[$d]);
			    $fstring = 
				join("", "n", "$nodes[$n]", "_S-", "$speed[$s]", "_BB-", "$size", "_D-", "$fdens", "_", "$sd", ".mo");

			    if($doSetup) 
			    {
				logMsg("$pirana_root/framework/opnet/tools/generate_pathloss -$pathloss_model[$m] $nodes[$n] $duration[$l] 0 0 0 $size $size 0 $speed[$s] 0 0 0 $pseeds[$sd] > $pathLossDir/$fstring");
				`$pirana_root/framework/opnet/tools/generate_pathloss -$pathloss_model[$m] $nodes[$n] $duration[$l] 0 0 0 $size $size 0 $speed[$s] 0 0 0 $pseeds[$sd] > $pathLossDir/$fstring`;
			    }

			    $topoDB{"topo_".$curTopoCount} = $fstring;

			    parsePlotToken($fstring);
			    $curTopoCount++;

			}
		    }
		}
	    }
	}
    }
}

sub getPathLossFiles
{
    $curTopoCount = 0;
    $topoDB{"topo_num"} = scalar(@topoFiles);

    for ($l =0; $l < $topoDB{"topo_num"}; $l++) 
    {
	$topoDB{"topo_".$curTopoCount} = $topoFiles[$l];
	#should say files are n15_S-2_BB-866_D-0.0002_1.mo
	#$plotVars{$fstring} = "--nameVal Speed=$speed[$s] --nameVal BB=$size --nameVal Density=$fdens";
	parsePlotToken($topoFiles[$l]);
	$curTopoCount++;
    }
}


sub genUniTrafficFiles
{
    #not really dependent on number of nodes
    logMsg("Generating Unicast Traffic");
    $traffDB{"traff_num"} = @loads * @packetSize * @nodes;
    $curTraffCount = 0;
    for ($n =0; $n < @nodes; $n++) 
    {
	for ($l =0; $l < @loads; $l++) 
	{
	    for($p = 0; $p < @packetSize; $p++) 
	    {
		$psize_bits = $packetSize[$p] * 8;
		$interarrival = $psize_bits/$loads[$l]/1000;

		mkdir("$outputDir/traff$curTraffCount", 0775);
		
		$fstring = 
		    join("", "n$nodes[$n]u", "_L-", "$loads[$l]", "_PS-", "$packetSize[$p]", "_T-", "$trafficTOS", ".gdf");

		if($doSetup) 
		{		
		    $cstring = join("", "echo $startTime:$endTime:$transport:$traffType:exponential,$interarrival,0:uniform,1,N:uniform,1,N:constant,$psize_bits:constant,$trafficTOS > $fstring");
		
		    logMsg($cstring);
		    $dstring = $outputDir."/traff".$curTraffCount."/".$fstring;
		    open(TFILE, ">$dstring");       # Open the file
		    print TFILE "$startTime:$endTime:$transport:$traffType:exponential,$interarrival,0:uniform,1,N:uniform,1,N:constant,$psize_bits:constant,$trafficTOS\n";
		    close(TFILE);

		    $dstring = $trafficDir."/".$fstring;
		    open(TFILE, ">$dstring");       # Open the file
		    print TFILE "$startTime:$endTime:$transport:$traffType:exponential,$interarrival,0:uniform,1,N:uniform,1,N:constant,$psize_bits:constant,$trafficTOS\n";
		    close(TFILE);
		}

		$traffDB{"traff_".$curTraffCount} = $fstring;
		
		$vstring = "traff".$curTraffCount;
		
		parsePlotToken($fstring);
		$curTraffCount++;
	    }
	}
    }
}

sub genUniTrafficFilesFromTemplate
{
    logMsg("Generating Unicast Traffic from Template");
    $traffDB{"traff_num"} = @templateFiles * @templateLoads * 
	@templatePacketSizes;
    logMsg("traff_num for template is ".$traffDB{"traff_num"});
    $curTraffCount = 0;
    for($n = 0; $n < @nodes; $n++){
	for($tf = 0; $tf < @templateFiles; $tf++){
	    for($l = 0; $l < @templateLoads; $l++){
		for($p = 0; $p < @templatePacketSizes; $p++){
		    $fstring = "n".$nodes[$n]."_T-".$tf."_PS-".
			$templatePacketSizes[$p]."_L-".$templateLoads[$l].".gdf";
		    $traffDB{"traff_".$curTraffCount} = $fstring;
		    print "fstring is $fstring \n";
		    parsePlotToken($fstring);
		    if($doSetup)
		    {
			$interarrival_time = $templatePacketSizes[$p]/
			    ($templateLoads[$l] * 1000);
			$t_bits = $templatePacketSizes[$p] * 8;
			mkdir("$outputDir/traff$curTraffCount", 0775);
			
			open(TEMPLATE, "$trafficDir/$templateFiles[$tf]") or die 
			    "Couldn't open template $trafficDir/$templateFiles[$tf]". 
			    ": $!";
			open(SIMTRAFFIC, ">$trafficDir/$fstring"); #used by sim
			open(OUTPUT_TRAFFIC, ">$outputDir"."/traff".$curTraffCount.
			     "/".$fstring); #backup to output dir          
			while(<TEMPLATE>){
			    s/runner_template_iatime/$interarrival_time/g;
			    s/runner_template_psize/$t_bits/g; 
			    #turn to bits from bytes.
			    #print "writing ".$_." to disk.\n";
			    print SIMTRAFFIC $_;
			    print OUTPUT_TRAFFIC $_;
			}
			
			close(TEMPLATE);
			close(SIMTRAFFIC);
			close(OUTPUT_TRAFFIC);
		    }
		    $curTraffCount++;
		}
	    }
	}
    }
}

sub getUniTrafficFiles
{
    logMsg("Getting Unicast Traffic Files");
    $traffDB{"traff_num"} = scalar(@utraffFiles);
    $curTraffCount = 0;
    for ($l = 0; $l < $traffDB{"traff_num"}; $l++) 
    {
	if($doSetup)
	{
	    mkdir("$outputDir/traff$curTraffCount", 0775);
	    logMsg("cp $trafficDir/$utraffFiles[$l] $outputDir/traff$curTraffCount");
	    `cp $trafficDir/$utraffFiles[$l] $outputDir/traff$curTraffCount`;
	    
	    #find the *.gdf 
	}
	$traffDB{"traff_".$curTraffCount} = $utraffFiles[$l];
	parsePlotToken($utraffFiles[$l]);
	$curTraffCount++;
    }

}

#will only support conf file with 1 node spec - because we independently
#generate traffic and pathloss
#can make it support more nodes, but I am not sure it is worthwhile to do so
sub genMcastTrafficFiles
{
    logMsg("Generating Multicast Traffic");
    $traffDB{"traff_num"} =  @nodes * @loads * @groupSize * @packetSize  * @flowLength;
    $curTraffCount = 0;
    for ($n =0; $n < @nodes; $n++) 
    {
	for ($l =0; $l < @loads; $l++) 
	{
	    for($g = 0; $g < @groupSize; $g++) 
	    {
		for($p = 0; $p < @packetSize; $p++) 
		{
		    for($fl = 0; $fl < @flowLength; $fl++) 
		    {
			$fstring = "n".$nodes[$n]."m_L-".$loads[$l]."_G-".$groupSize[$g]."_P-".$packetSize[$p]."_FL-".$flowLength[$fl].".gdf";

			if($doSetup)
			{
			    mkdir("$outputDir/traff$curTraffCount", 0775);
#-l 1 -s 300 -e 600 -g 10 -c 2 -n 40 -f 10 -R 13.0 -t 0 -S 260 -p pirana-config.pctl -o /home/rrhain/w-scripts/run1/tmp-rrh.gdf -d /home/rrhain/w-scripts/run1
			    $cstring = join(" ", "$scriptDir/gen_ivox -l", $loads[$l], "-s", $startTime, "-e", $endTime, "-g", $groupSize[$g], "-c", $numGroups, "-n", $nodes[$n], "-f", $flowLength[$fl], "-R", $multicastRate, "-t", $trafficTOS, "-S", $packetSize[$p], "-p pirana-config.pctl", "-r", rand(1000), "-o $outputDir/traff$curTraffCount/$fstring", "-d $outputDir/traff$curTraffCount");
			
			    print "$cstring\n";
			    `$cstring`;
			}
			
			$vstring = "traff".$curTraffCount;
		
			parsePlotToken($fstring);	    
			$traffDB{"traff_".$curTraffCount} = $fstring;
		
			$curTraffCount++;
		    }
		}
	    }
	}
    }
}


sub getMcastTrafficFiles
{
    logMsg("Getting Multicast Traffic Files");
    $traffDB{"traff_num"} = scalar(@mtraffDirs);
    $curTraffCount = 0;
    for ($l = 0; $l < $traffDB{"traff_num"}; $l++) 
    {
	if($doSetup)
	{
	    mkdir("$outputDir/traff$curTraffCount", 0775);
	    print "cp $mtraffDirs[$l]/* $outputDir/traff$curTraffCount\n";
	    `cp $mtraffDirs[$l]/* $outputDir/traff$curTraffCount`;
	}
	#find the *.gdf 
	$traffDB{"traff_".$curTraffCount} = $mtraffFiles[$l];
	parsePlotToken($mtraffFiles[$l]);	    
	$curTraffCount++;
    }
}

sub getScenarioTopoFiles
{
    logMsg("Getting Scenario Topo Files");
    $curTopoCount = 0;
    $topoDB{"topo_num"} = scalar(@topoFiles);

    for ($l =0; $l < $topoDB{"topo_num"}; $l++) 
    {
	$topoDB{"topo_".$curTopoCount} = $topoFiles[$l];
	#should say files are n10_oct2009_demo.ef
	#$plotVars{$fstring} = "--nameVal Speed=$speed[$s] --nameVal BB=$size --nameVal Density=$fdens";
	parsePlotToken($topoFiles[$l]);	    
	$curTopoCount++;

    }

}


sub getScenarioTrafficFiles
{
    logMsg("Getting Scenario Traffic Files");
    $traffDB{"traff_num"} = scalar(@traffFiles);
    $curTraffCount = 0;
    for ($l = 0; $l < $traffDB{"traff_num"}; $l++) 
    {
	if($doSetup)
	{
	    mkdir("$outputDir/traff$curTraffCount", 0775);
	    `cp $scenarioDir/*.ef $outputDir/traff$curTraffCount`;
	    `cp $scenarioDir/$traffFiles[$l] $outputDir/traff$curTraffCount`;
	    `cp $scenarioDir/pirana-config.pctl_* $outputDir/traff$curTraffCount`;
	}

	#find the *.gdf 
	$traffDB{"traff_".$curTraffCount} = $traffFiles[$l];
	parsePlotToken($traffFiles[$l]);	    
	$curTraffCount++;
    }
}



#actually run the simulations
sub runSimulations
{
    logMsg("Starting to run simulations");

    # figure out how many simulations to run by counting the runXXX
    # directories
    $numberSims = 0;
    opendir(DIR, $outputDir) || die("Could not open dir $outputDir: $!");
    while ( ($dir = readdir(DIR)))
    {
	if(-d "$outputDir/$dir" && ($dir =~ /^run\d+/) )
	{
	    $numberSims++;
	}
    }
    closedir(DIR);

    if($numberSims > 0)  #just making sure there is something to run
    {
	logMsg("$numberSims simulations are configured");

	for($index = 1; 
	    $index <= $numberSims; 
	    $index++)
	{
	    chdir("$outputDir/run$index") || die("could not cd to $outputDir/run$index: $!");

	    # Try to make a directory called "claimed" in the current
            # runXXX dir.  If it succeeds, go ahead and run this
            # simulation.  However, if the directory already exists,
            # the mkdir fails.  In that case, we assume this means
            # some other instantiation of this script has created the
            # directory and is running the simulation, so go on to the
            # next sim index.  If the outputDir is on an NFS-mounted
            # filesystem, this allows multiple machines to cooperate
            # in running this batch of sims without requiring the user
            # to preallocate certain machines to certain sims.

	    if( ! mkdir("claimed") ) 
	    {
		# mkdir error; assume directory exists.
		# There should only be one file in the claimed
		# directory, and its name is the hostname of the
		# machine that claimed this run

		opendir(DIR, "claimed") || die("could not open claimed directory: $!");
		while ($claimhost = readdir(DIR))
		{
		    # skip . and ..
		    last if ( ! ($claimhost =~ m/^\./))
		}
		closedir(DIR);
		logMsg("skipping run$index because it is already claimed by $claimhost");
		next;
	    }
	    
	    open(CLAIM, ">claimed/$host") || die("couldn't open claimed/$host: $!");

	    logMsg("running simulation $index out of $numberSims");

	    # get the simulation command line for this directory
	    open(CMDFILE, "<runsim.sh")  || die("couldn't open runsim.sh: $!");
	    $cmdstring = <CMDFILE>;
	    close(CMDFILE);

	    chomp($cmdstring);
	    logMsg($cmdstring);

	    # Finally, run a simulation!
	    `$cmdstring > out 2>err`;

	    runResult($index);

	    `gzip out *.viz`;

	    close(CLAIM);
	}
    }
    else 
    {
	logMsg("NO VALID SIMS TO RUN");
    }
}

sub runResultScripts
{
    for($index = 1; 
	$index <= ($topoDB{"topo_num"} * $traffDB{"traff_num"} * $numToGenForVariables); 
	$index++)
    {
	chdir("$outputDir/run$index");


	$newString = $plotArgs[($index-1)];
	$newString =~ s/\s+//g;

	@me = split(/--nameVal/, $newString);
	
	$newPlotString = '';

	foreach $val (@me) {
	    if($val =~ /=/)
	    {
		@words = split(/=/, $val);

		if (defined $wantedPlotVars{$words[0]})
		{
		    $newVal = $wantedPlotVars{$words[0]};
		    $newPlotString = join(" ", $newPlotString, "--nameVal $newVal=$words[1]");
		}
	    }
	}
	#can filter out plotting args you don't want
	#and also substitute shorter names before calling the plotter
	#keeping track of the run number
	logMsg("$dirResultsExecutable run$index/out -s $newPlotString --nameVal RunIdx=$index --matout=$outputDir/matrix.txt");
	`$dirResultsExecutable out -s $newPlotString --nameVal RunIdx=$index --matout=$outputDir/matrix.txt`;
    }

    #would call the plotter here
}

#assumes you are in the directory you just ran a sim
sub runResult
{
    #run$index - is directory we are in
    $index = shift;

    $newString = $plotArgs[($index-1)];
    $newString =~ s/\s+//g;

    @me = split(/--nameVal/, $newString);
	
    $newPlotString = '';

    foreach $val (@me) {
	if($val =~ /=/)
	{
	    @words = split(/=/, $val);
	    
	    if (defined $wantedPlotVars{$words[0]})
	    {
		$newVal = $wantedPlotVars{$words[0]};
		$newPlotString = join(" ", $newPlotString, "--nameVal $newVal=$words[1]");
	    }
	}
    }
    #can filter out plotting args you don't want
    #and also substitute shorter names before calling the plotter
    #keeping track of the run number
    $analyzeString = "$dirResultsExecutable out -s $newPlotString --nameVal RunIdx=$index --matout=$outputDir/matrix.txt";

    logMsg("in run$index: $analyzeString");

    `$analyzeString`;

    $teststring = "$dirResultsExecutable \$1 -s $newPlotString --nameVal RunIdx=$index --matout=\$2";

    #assumes that the executable is somewhere under pirana-opnet
    $teststring =~ s/.*\/pirana-opnet/$testCartelPrefix\/pirana-opnet/;

    open(C1FILE, ">ana.sh");       # Open the file for testing info
    print C1FILE $teststring."\n";
    close(C1ILE);
}

#print usage for the perl script
sub usage
{   
    printf ("\nUsage:\n");
    printf ("    simRunner.pl <configFile>\n");
    printf ("    where: <configFile> input specifying simulation parms\n");
    printf ("\nDescription:\n");
    printf ("@description\n");
    exit(1);
}

#check that key directories and files actually exist
sub checkInput
{
    print("Checking input and retrieve svn and simulation information\n");
    if(-d "$simDir")
    {
	print("$simDir exists, no need to create\n");
    }
    else
    {
	print("$simDir does not exist.\nCreate it? <y or n> ");
	$yesOrNo = <STDIN>; 
	if($yesOrNo =~ "y")
	{
	    mkdir("$simDir", 0775) || die ("could not make $simDir: $!");
	}
	else
	{
	    exit(1);
	}
    }

    mkdir("$outputDir", 0775);

    # If simulations are already set up, don't do it all again.  We
    # take the existence of the siminfo file as evidence that the sims
    # are set up.

    if(-e $siminfoFile)
    {
	logMsg("$siminfoFile already exists; assuming simulation setup is already done");
	$doSetup = 0;
    }

    logMsg("$simDescription");

    #save conf file
    `cp $configFile $outputDir`;

    #get svn information
    if(! -d "$pirana_root")
    {
	logMsg("Exiting .......");
	logMsg("    Big problem: $pirana_root missing");
	exit(1);
    }
    
    if(! -e "$outputDir/svn-info")
    {
	logMsg("Recording svn info and local diffs");
	opendir (DIR, $pirana_root) || die "Error in opening dir $pirana_root: $!";
	while( ($rfilename = readdir(DIR)))
	{
	    my $fname = $pirana_root."/".$rfilename;
	    if(-d $fname)
	    {
		my $svnName = $fname."/".".svn";
		if(-e $svnName)
		{
		    `svn info $fname >> $outputDir/svn-info`;
		    `svn diff $fname >> $outputDir/svn-diff`;
		}
	    }
	}
	closedir(DIR);
    }

    if(-d "$pathLossDir")
    {
	logMsg("$pathLossDir exists, no need to create");
    }
    else
    {
	print("$pathLossDir does not exist.\nCreate it? <y or n> ");
	$yesOrNo = <STDIN>; 
	if($yesOrNo =~ "y")
	{
	    mkdir("$pathLossDir", 0775) || die ("could not make $pathLossDir: $!");
	}
	else
	{
	    logMsg("Exiting .......");
	    logMsg("   Could not create $pathLossDir");
	    exit(1);
	}
    }

    if(-d "$trafficDir")
    {
	logMsg("$trafficDir exists, no need to create");
    }
    else
    {
	print("$trafficDir does not exist.\nCreate it? <y or n> ");
	$yesOrNo = <STDIN>; 
	if($yesOrNo =~ "y")
	{
	    mkdir("$trafficDir", 0775) || die ("could not make $trafficDir: $!");
	}
	else
	{
	    logMsg("Exiting .......");
	    logMsg("   Could not create $trafficDir");
	    exit(1);
	}
    }


    unless(-e "$efTemplate")
    {
	logMsg("Exiting .......");
	logMsg("   You need to provide an opnet template: $efTemplate");
	exit(1);
    }

    unless(-e "$pctlTemplate")
    {
	logMsg("Exiting .......");
	logMsg("   You need to provide a pctl template: $pctlTemplate");
	exit(1);
    }

    unless(-e "$simExecutable")
    {
	logMsg("Exiting .......");
	logMsg("   You need to provide a simulation executable: $simExecutable");
	exit(1);
    }

    if(($topoFlag =~ /scenarios/) || ($trafficFlag =~ /scenarios/))
    {
	unless(-d "$scenarioDir")
	{
	    logMsg("Exiting .......");
	    logMsg("   You need to provide a valid scenario directory: $scenarioDir");
	    exit(1);
	}
    }
}

#print the variable database
sub printSimVariableDatabase
{

    print("Simulation Variable Database:\n");
    foreach $kword (sort (keys (%sysVarDB)))
    {
	print("$kword: $sysVarDB{$kword}\n");
    }
}

#print the topology database
sub printTopoDatabase
{

    print("Topology Database:\n");
    foreach $kword (sort(keys (%topoDB)))
    {
	print("$kword: $topoDB{$kword}\n");
    }
}

sub printLinesToModify
{
    open(INFO, "<$pctlTemplate");       # Open the file
    @scrLines = <INFO> ;                     # Read it into an array
    close(INFO);
    foreach $kword (keys (%sysVarDB))
    {
	if ($kword =~ /pos/ && $kword =~ /pctl/)
	{
            print "$kword: ";
	    print ("$sysVarDB{$kword}\n");
	    $val = $sysVarDB{$kword};
	    print ("$scrLines[$val]");
	}
    }
}


#print all the script files for the runs based on how
#many topologies and variables
sub printScriptFiles
{
    open(INFO, "<$pctlTemplate");       # Open the file
    @scrLines = <INFO> ;                     # Read it into an array
    close(INFO);
    $pctlLines = scalar(@scrLines);
    $scrLines[($pctlLines-1)] =~ s/$/\n/;

    open(INFO, "<$efTemplate");       # Open the file
    @efLines = <INFO> ;                     # Read it into an array
    close(INFO);
    $opnetLines = scalar(@efLines);
    $efLines[($opnetLines - 1)] =~ s/$/\n/;

    $k = 0;
    for($j = 0; $j < $topoDB{"topo_num"}; $j++)
    {
	$topoFileName = $topoDB{"topo_".$j};
	$topoFileName =~ /\W*?(\d+)/;
	$topoNumNodes = $1; 
	#accounting for topology

	#if we want to support multiple nodes per conf file
	#we need some naming convention that says that topo and traffic
	#are for the same number of nodes, if not, we skip out of the loop
	#at the end of this subroutine, we'd need to know how many runs
	#we have
	for($l = 0; $l < $traffDB{"traff_num"}; $l++)
	{
	    $traffFileName = $traffDB{"traff_".$l};
	    $traffFileName =~ /\W*?(\d+)/;
	    $traffNumNodes = $1; 
	    if($traffNumNodes != $topoNumNodes)
	    {
		next;
	    }
	   

	    for ($i = 0; $i < $numToGenForVariables; $i++)
	    {
		$k +=  1;
		$pstring = '';

		logMsg("populating directory $outputDir/run$k");
		mkdir("$outputDir/run$k", 0775);
		chdir("$outputDir/run$k");

		if($topoFlag =~ /scenarios/)
		{
		    if($topoSymlink)
		    {
			symlink($scenarioDir . "/" . $topoDB{"topo_".$j}, $topoDB{"topo_".$j});
		    }
		    else
		    {
			`cp $scenarioDir/$topoDB{"topo_".$j} .`;
		    }
		    `cp $scenarioDir/*.trj .`;
		}
		else
		{
		    if($topoSymlink)
		    {
			symlink($pathLossDir . "/" . $topoDB{"topo_".$j}, $topoDB{"topo_".$j});
		    }
		    else
		    {
			`cp $pathLossDir/$topoDB{"topo_".$j} .`
		    }
		}

		$pstring = join(" ", $pstring, "$plotVars{$topoFileName}");

		if($trafficFlag =~ /scenarios/)
		{
		    #have to be careful with multicast as you need to copy all the pctl files also
		    `cp $outputDir/traff$l/pirana-config.pctl_* .`;
		    `cp $outputDir/traff$l/*.ef .`;
		    `cp $outputDir/traff$l/$traffDB{"traff_".$l} .`;
		}
		elsif($trafficFlag =~ /Multicast/)
		{
		    #have to be careful with multicast as you need to copy all the pctl files also
		    `cp $outputDir/traff$l/pirana-config.pctl_* .`;
		    `cp $outputDir/traff$l/$traffDB{"traff_".$l} .`;
		}
		else
		{
		    #copy unicast traffic files
		    `cp $outputDir/traff$l/$traffDB{"traff_".$l} .`;
		}
		$pstring = join(" ", $pstring, "$plotVars{$traffFileName}");

		if($topoFlag =~ /scenarios/)
		{
		    $cmdstring = join(" ", $simExecutable, "-n", $topoNumNodes, "-m", $topoFileName, "-t", $traffFileName, "-d", $simDuration);
		}
		else
		{
		    $cmdstring = join(" ", $simExecutable, "-n", $topoNumNodes, "-p", $topoFileName, "-t", $traffFileName, "-d", $simDuration);
		}

		#just to make it backward compatible - people don't have to fix conf
		if(defined $policyFile)
		{
		    $cmdstring = join(" ", $cmdstring, "-P", $policyFile);
		}

		# create file to hold simulation command line
		open(CMDFILE, ">runsim.sh");       
		print CMDFILE $cmdstring."\n";
		close(CMDFILE);

		#substitute parts of $simExecutable for test cartel needs
		$teststring = $cmdstring;
		$teststring =~ s/.*\/pirana-opnet/$testCartelPrefix\/pirana-opnet/;
		open(CMDFILE, ">run.sh");       # Open the file for testing info
		print CMDFILE $teststring."\n";
		close(CMDILE);

		open(RES, ">pirana-config.pctl");
		open(REF, ">opnet-config.ef");

		open(CRES, ">pirana-config.pctl_ovl");
		#by virtue of th opnet-config.ef file being empty, it is 
		#an overlay
		#open(CREF, ">opnet-config.ef_ovl");

		foreach $kword (sort (keys (%sysVarDB)))
		{
		    if ($kword =~ /pos/) 

		    {
#			print ("$kword:$sysVarDB{$kword}\n");
			$val = $sysVarDB{$kword};
			@varNames = split(/\|/, $kword);		    
			
			$newkword = $kword;
			$newkword =~ s/pos/$i/;
			$pstring = join(" ", $pstring, "--nameVal $varNames[1]=$sysVarDB{$newkword}");

#			print ("$kword, $newkword\n");

			if($kword =~ /pctl/)
			{
			    if($val < $pctlLines)
			    {
				$scrLines[$val] =~ /(\d[ \d]*)$/;
				$scrLines[$val] =~ s/$1/$sysVarDB{$newkword}/;
			    }
			    else
			    {
				$scrLines[$val] = "set $varNames[1] $sysVarDB{$newkword}\n";
			    }
			    print CRES $scrLines[$val];
			}
			elsif ($kword =~ /opnet/) 
			{
			    if($val < $opnetLines)
			    {
				$efLines[$val] =~ /(\d[ \d]*)$/;
				$efLines[$val] =~ s/$1/$sysVarDB{$newkword}/;
			    }
			    else 
			    {
				$efLines[$val] = "$varNames[1]: $sysVarDB{$newkword}\n";
			    }
			    #see comment above
			    #print CREF $efLines[$val];
			}

		    }
		}
#		print $pstring."\n";
		#used for the python plotter
		push(@plotArgs, $pstring);
		
		#print the pirana-config.pctl files
		print RES @scrLines;
		close(RES);
		close(CRES);

		#print the opnet files
		print REF @efLines;
		close(REF);
                #see comment above
		#close(CREF);
	    }
	}
    }

    logMsg("$k simulation directories are all set to go!");
}


sub parsePlotToken
{
    $actToken = shift;
    $curToken = $actToken;
    $curToken =~ s/\.gdf$//;
    $curToken =~ s/\.mo$//;

    @plotParts = split(/_/, $curToken);
	
    #skip first token - user specified
    $pString = '';
    for($i = 1; $i < scalar(@plotParts); $i++)
    {
	if($plotParts[$i] =~ /-/)
	{
	    @pTokens = split(/-/, $plotParts[$i]);
	
	    #check for at least 2 tokens, else drop it
	    if(scalar(@pTokens) == 2)
	    {
		$pString = join("", $pString, "--nameVal ", $pTokens[0], "=", 
				$pTokens[1], " ");
	    }
	}

    }
    $plotVars{$actToken} = $pString;
}


sub dupScriptFiles
{
    $k = 0;
    for($j = 0; $j < $topoDB{"topo_num"}; $j++)
    {
	$topoFileName = $topoDB{"topo_".$j};
	$topoFileName =~ /\W*?(\d+)/;
	$topoNumNodes = $1; 
	#accounting for topology

	#if we want to support multiple nodes per conf file
	#we need some naming convention that says that topo and traffic
	#are for the same number of nodes, if not, we skip out of the loop
	#at the end of this subroutine, we'd need to know how many runs
	#we have
	for($l = 0; $l < $traffDB{"traff_num"}; $l++)
	{
	    $traffFileName = $traffDB{"traff_".$l};
	    $traffFileName =~ /\W*?(\d+)/;
	    $traffNumNodes = $1; 
	    if($traffNumNodes != $topoNumNodes)
	    {
		next;
	    }
	   

	    for ($i = 0; $i < $numToGenForVariables; $i++)
	    {
		$k +=  1;
		$pstring = '';

		$pstring = join(" ", $pstring, "$plotVars{$topoFileName}");

		$pstring = join(" ", $pstring, "$plotVars{$traffFileName}");

		foreach $kword (sort (keys (%sysVarDB)))
		{
		    if ($kword =~ /pos/) 

		    {
#			print ("$kword:$sysVarDB{$kword}\n");
			$val = $sysVarDB{$kword};
			@varNames = split(/\|/, $kword);		    
			
			$newkword = $kword;
			$newkword =~ s/pos/$i/;
			$pstring = join(" ", $pstring, "--nameVal $varNames[1]=$sysVarDB{$newkword}");
		    }
		}
#		print $pstring."\n";
		#used for the python plotter
		push(@plotArgs, $pstring);
		
	    }
	}
    }
    logMsg("$k simulation directories are all set to go!");
}
