#!/bin/bash
#
# Script to run C2E scenarios
#
# Usage:
#      ./run-c2e-scenario-cgroup1.sh
#

#=============================================================
# Initialization
#=============================================================

# Traffic
config_file="./share-conf.cfg"

# Simulation and traffic duration
duration=150
traffic_start=30
let traffic_end=$duration-30
let traffic_duration=$traffic_end-$traffic_start 

# Save NetAnim file
anim=1

# Scenario parameters
# 250 * M_IN_NAUTICAL_MILE = 250 * 1852
range=463000
num_nodes=4
mobility="LineMobilityModel"
link_estimation_period="1000000"    
fullpath=$( cd $(dirname $0) ; pwd -P )
trace_file=$fullpath"/scenarios/c2e-scenarios/traces/scen_t600_i1/scen_cgroup_7_s1.tcl"
num_waveform1=$num_nodes
num_waveform2=0
rng_seed=1
rng_run=1
# Use simple-wireless
#scenario="share-test-sw"
simple_wireless_data_rate=1000000000
simple_wireless_error_rate=0.0
simple_wireless_contention_range=0
#`expr $range + $range`

# Use 802.11
scenario="share-test-sw"
capacity_80211="DsssRate11Mbps"

# Output files
tag="sim"
now=$(date +"%m%d%Y_%H%M%S")
plot_file_prefix="output/plot_"$now"_"$pattern"_"$mobility_type
analysis_file="output/analysis_"$now"_"$pattern"_"$mobility_type".txt"      
trace_dir="output/results_sim_$now"
pcap_file="$trace_dir/trace-all-$tag.pcap"

#=============================================================
# Run Simulation
#=============================================================
/home/rrosales/PROJECTS/BUA/SHARE/Software/Tuscarora/Src/Patterns/Share/Sandbox/runsim -n $num_nodes -r $range -s $scenario -d $duration -a $anim \
	-m $mobility -f $trace_file -l $link_estimation_period -c $config_file \
        -w $num_waveform1 -u $num_waveform2 -q $simple_wireless_contention_range \
        -e $simple_wireless_error_rate -b $simple_wireless_data_rate -o $capacity_80211 \
        -g $rng_seed -j $rng_run

#=============================================================
# Analysis
#=============================================================

/home/rrosales/PROJECTS/BUA/SHARE/Software/Tuscarora/Src/Patterns/Share/Sandbox/analysis/share-analysis.sh $num_nodes $analysis_file $pcap_file $trace_dir 

#=============================================================
# Plotting
#=============================================================

#R --no-save --quiet --args $analysis_file $plot_file_prefix $traffic_duration < plotting/plot_bps.R  > /dev/null
