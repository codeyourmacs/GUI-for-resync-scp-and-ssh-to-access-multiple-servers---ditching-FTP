#!/usr/bin/env perl
use strict;
use warnings;

# Project Name: POEM-HOPKY V1.0
# Description: HTML GUI for SSH/SCP/rsync
# Author: CodeMacs.com (Web Design Co.)
# License: GNU General Public License v3.0
# 
# Copyright (C) 2024 CodeMacs.com/wd-co.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

## Adjust PATH according to your local server settings
$ENV{'PATH'} = '/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin:/http/bin';

use File::Basename qw();
my($name, $path, $suffix) = File::Basename::fileparse($0);	$path =~ s/\/+$//;

my($title,$sitesel,$memd,$tpmess);
print "Content-type: text/html\n\n";

our %in;
if($ENV{QUERY_STRING}) {
	if(-f "$path/cgi-lib.pl") {eval {require "$path/cgi-lib.pl"};
	unless($@) {ReadParse();}
	} ## INPUT LIBRARY
} ## END IF DATA PRESENT

eval {use Cache::Memcached};
unless($@) {
	$memd = new Cache::Memcached {'servers' => ['localhost:11211'],'debug' => 0,'compress_threshold' => 10_000,};
	if($memd->get("siteselected$ENV{'REMOTE_ADDR'}")) {
		unless($in{site}) {$in{site}=$memd->get("siteselected$ENV{'REMOTE_ADDR'}");}
	}
} ## END GOOD EVAL

my %sites;
getsites();


print <<EOH;
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>POEM-HOPKY V1.0 Non-FTP HTML ssh/scp/sync</title>
<meta http-equiv="cache-control" content="no-cache" />
<meta http-equiv="expires" content="0" />
<meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />
<meta http-equiv="pragma" content="no-cache" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="stylesheet" href="/site/css/font-awesome.min.css" />
<link rel="stylesheet" href="css/page.css" media="screen" />
<script src="/site/js/work.js"></script>
</head>
<body>
<div class="head" id="head">
<div class="htitle"><form><b>Select site:</b> <select class="sitesel" id="sitetouse" name="site" onchange="siteconnect();return false;">$sitesel</select>$tpmess</form>
<span class="center small"><a target="_blank" href="https://www.codemacs.com/coding/other/ditching-ftp-embracing-scp-rsync-and-ssh-for-safer-file-transfers.2073751.htm">POEM-HOPKY V1.0</a></span>
<span class="right"><a href="#" onclick="settings();return false;"><i class="fa fa-gear fa-lg"></i></a>
<a href="#" onclick="help();return false;"><i class="fa fa-question-circle-o fa-lg"></i></a></span></div>
</div>
<div class="content" id="condata">
<div class="filebox" id="localfiles">
	<div class="headbox">
	<span id="locntr"><i title="Local Computer" class="locahead fa fa-desktop"></i>
	<i title="Upload" class="fa fa-upload doitem na"></i>
	<a href="#" class="doitem" onclick="refresh('local');return false;"><i title="Refresh" class="fa fa-refresh"></i></a>
	<i title="View" class="fa fa-eye doitem na"></i>
	<i title="Info" class="fa fa-info doitem na"></i>
	<i title="Rename" class="fa fa-sliders doitem na"></i>
	<i title="Delete" class="fa fa-trash-o na"></i>
	<span class="fa-stack"><i title="Create New Folder" class="fa fa-folder-o fa-stack-1x na"></i><span class="fa fa-stack-1x na letter">+</span></span></span>
	<div id="locdir" class="topdir"></div>
	</div>
	<div class="files" id="locfilelist">
		<form>
		<div class="frmr">
		<input id="1" class="ckb" type="checkbox" value="">
		<label for="1" class="ckl">Select a Site and click Refresh to see files here <span></span></label>
		</div>
		</form>
	</div>
<input type="checkbox" class="ckbhd" name="localall" id="localall" value="1">
</div>
<div class="filebox" id="remotefiles">
        <div class="headbox">
        <span id="remcntr"><i title="Remote Server" class="locahead fa fa-server"></i>
        <i title="Download" class="fa fa-download doitem na"></i>
        <a href="#" class="doitem" onclick="refresh('remote');return false;"><i title="Refresh" class="fa fa-refresh"></i></a>
	<i title="View" class="fa fa-eye doitem na"></i>
	<i title="Info" class="fa fa-info doitem na"></i>
	<i title="Rename" class="fa fa-sliders doitem na"></i>
	<i title="Delete" class="fa fa-trash-o na"></i>
	<span class="fa-stack"><i title="Create New Folder" class="fa fa-folder-o fa-stack-1x na"></i><span class="fa fa-stack-1x na letter">+</span></span></span>
	<div id="remdir" class="topdir"></div>
        </div>
	<div class="files" id="remfilelist">
		<form>
		<div class="frmr">
		<input id="1" class="ckb" type="checkbox" value="">
		<label for="1" class="ckl">Select a Site and click Refresh to see files here <span></span></label>
		</div>
		</form>
	</div>
<input type="checkbox" class="ckbhd" name="remoteall" id="remoteall" value="1">
</div>
</div>
<div class="nobox boxposition" id="tempbox">
<div class="boxcontent" id="bcontent"></div>
<div class="cnrlbx"><a href="#" onclick="hidebox();return false;"><button type="submit" class="closebutton">Close</button></a></div>
</div>
<div id="barcontent">
<div class="barnotes" id="notesprog">1%</div>
<div class="barprogress" id="progbar"></div>
</div>
</body>
</html>
EOH
exit(0);

sub getsites {
	my ($f,$d);
	our %settings;
	if($memd->get("allsitessel$ENV{'REMOTE_ADDR'}")) {
		$d = $memd->get("allsitessel$ENV{'REMOTE_ADDR'}");
		if($memd->get("initdir$ENV{'REMOTE_ADDR'}")) {$settings{initdir}=$memd->get("initdir$ENV{'REMOTE_ADDR'}");}
	} else {
		my $pr=$ENV{SCRIPT_FILENAME};	my @spf=split(/\//,$pr);	pop(@spf);	$pr = join '/',@spf;
		if(-f "$pr/datasettings.cgi") {
			eval {require "$pr/datasettings.cgi"};
			unless($@) {$f = $settings{sitefile};}
		}
		if(-f $f) {
			$d = `cat $f`;
			if($memd) {
				$memd->set("allsitessel$ENV{'REMOTE_ADDR'}",$d,43200);
				$memd->set("settingdata$ENV{'REMOTE_ADDR'}",$f,86400);
				if($settings{initdir}) {$memd->set("initdir$ENV{'REMOTE_ADDR'}",$settings{initdir},86400);}
			}
		} else {
			$tpmess=' &nbsp; <a href="#" class="right" onclick="settings();return false;">Open Settings to Add a Site</a>';
			if($memd) {
				if($settings{initdir}) {$memd->set("initdir$ENV{'REMOTE_ADDR'}",$settings{initdir},86400);}
			}
		}
	}
	my @lns = split(/\n/,$d);
	$sitesel = "<option value=\"\">Select a Site</option>\n";
	foreach my $l (@lns) {
		$l =~ s#(.*?)\t(.*?)\t(.*)##;
		my($site,$usr,$ip) = ($1,$2,$3);
		if($site && $usr && $ip) {$sites{$site}{$usr}=$ip;}
	}
	foreach my $s (sort keys (%sites)) {
		foreach my $u (keys %{$sites{$s}}) {
			my $selected='';
			if($in{site} && $in{site} eq "$u $sites{$s}{$u}") {$selected=' selected';}
			$sitesel .= "<option value=\"$u $sites{$s}{$u}\"$selected>$s ($u)</option>\n";
		}
	}
	chomp $sitesel;
} ## END SUB GET SITES
