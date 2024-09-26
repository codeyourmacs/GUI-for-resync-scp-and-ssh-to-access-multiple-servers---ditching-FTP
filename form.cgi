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

my($memd,$siteuse,$remdir,$locdir,$servr,$locdirsh,$remdirsh,$fmode);
our %settings;
my %digmn = ('Jan','01','Feb','02','Mar','03','Apr','04','May','05','Jun','06','Jul','07','Aug','08','Sep','09','Oct','10','Nov','11','Dec','12');
my $localtime = `date`;	chop $localtime;	$localtime =~ tr/  //s;	my($wd,$mo,$da,$ti,$sh,$yr) = split(/\s/,$localtime);
our %in;
if($ENV{QUERY_STRING}) {
	if(-f "$path/cgi-lib.pl") {
		eval {require "$path/cgi-lib.pl"};
		unless($@) {ReadParse();}
	} ## INPUT LIBRARY
}

#unless($in{do}) {printerrsm("<h3>No task</h3>\n<p>No task for processing submitted.</p>");}

eval {use Cache::Memcached};
unless($@) {
	$memd = new Cache::Memcached {'servers' => ['localhost:11211'],'debug' => 0,'compress_threshold' => 10_000,};
	unless($memd->get("clearedtempsscp")) {
		$memd->set("clearedtempsscp",1,7200);
		unless(-d "$path/temp") {`mkdir -p $path/temp`;}
		`rm -rf $path/temp/*`;
		createindex('$path/index.cgi');
	}
} ## END GOOD EVAL

if($in{do} eq 'help') {helpshow();			exit(0);}
if($in{do} eq 'dirinit') {setinitdir();			exit(0);}
if($in{do} eq 'sitesubmit') {writeasite();		exit(0);}
if($in{do} eq 'sitedelete') {sitedelete();		exit(0);}
if($in{do} eq 'writesitefile') {writesitefile();	exit(0);}
if($in{do} eq 'clearsess') {clearmemd();		exit(0);}
if($in{do} eq 'refresh') {dorefresh();			exit(0);}
if($in{do} eq 'setsite') {setwebsite();			exit(0);}
if($in{do} eq 'view') {prepfile();			exit(0);}
if($in{do} eq 'info') {prepfile();			exit(0);}
if($in{do} eq 'trash') {prepfile();			exit(0);}
if($in{do} eq 'trashdo') {prepfile();			exit(0);}
if($in{do} eq 'rename') {renamepre();			exit(0);}
if($in{do} eq 'newfolder') {folderget();		exit(0);}
if($in{do} eq 'foldercreate') {folderwrite();		exit(0);}
if($in{do} eq 'changename') {changename();		exit(0);}
if($in{do} eq 'changemode') {changemode();		exit(0);}
if($in{do} eq 'changedir') {changedir();		exit(0);}
if($in{do} eq 'settings') {settings();			exit(0);}

if($in{do} eq 'download' || $in{do} eq 'upload') {
	movefiles();					exit(0);
}
if($in{do} eq 'upload') {upload();			exit(0);}

printerrsm("<h3>No task</h3>\n<p>No task for processing submitted.</p>");

sub setinitdir {
	my($file,$didwrite,$d);
	unless($in{initdir}) {
		printerrsm("<h3>No Input</h3>\n<p>Initial Local Directory has to be filled.</p>");
	}
	unless(-d $in{initdir}) {
		printerrsm("<h3>Directory error</h3>\n<p>Directory \"$in{initdir}\" was not found.</p>");
	}

	my $pr=$ENV{SCRIPT_FILENAME};	my @spf=split(/\//,$pr);	pop(@spf);	$pr = join '/',@spf;
	if(-f "$pr/datasettings.cgi") {
		eval {require "$pr/datasettings.cgi"};
	}

	foreach my $k (keys (%in)) {$in{$k} =~ s/\t//g;}
	$settings{initdir}="$in{initdir}";
	writetpsettings("$pr/datasettings.cgi"); ## WRITE SETTINGS FILE
	if($memd) {
		$memd->set("allsitessel$ENV{'REMOTE_ADDR'}",$d,43200);
		$memd->set("settingdata$ENV{'REMOTE_ADDR'}",$file,86400);
		$memd->set("initdir$ENV{'REMOTE_ADDR'}",$settings{initdir},86400);
	}
	printerrsm("<h3>Record updated</h3>\n<p>Initial local directory set to: \"$in{initdir}\"</p>");
} ## END INIT LOCAL DIR SET

sub sitedelete {
	my($file,$didwrite,$d);
	unless($in{sname}) {
		printerrsm("<h3>No Input</h3>\n<p>In order to delete Site data all fields have to be filled.</p>");
	}
	if($memd->get("settingdata$ENV{'REMOTE_ADDR'}")) {
		$file=$memd->get("settingdata$ENV{'REMOTE_ADDR'}");
	} else {
		my $pr=$ENV{SCRIPT_FILENAME};	my @spf=split(/\//,$pr);	pop(@spf);	$pr = join '/',@spf;
		if(-f "$pr/datasettings.cgi") {
			eval {require "$pr/datasettings.cgi"};
			$file = $settings{sitefile};
		}
	}
	unless($file) {
		printerrsm("<h3>File error</h3>\n<p>Un-known file location to write Site Data.<br />Try submitting a file name first.</p>");
	}
	foreach my $k (keys (%in)) {$in{$k} =~ s/\t//g;}
	my %siteswr;
	if(-f $file) {
		$d = `cat $file`;	my @lns = split(/\n/,$d);
		foreach my $l (@lns) {
			$l =~ s#(.*?)\t(.*?)\t(.*)##;
			$siteswr{$1}="$2\t$3";
		} ## FOREACH END
	} ## END FILE PRESENT
	if($siteswr{$in{sname}}) {delete $siteswr{$in{sname}};}
	else {
		printerrsm("<h3>Nothing to delete</h3>\n<p>Site \"$in{sname}\" was not found - nothing to delete.</p>");
	}
	my $norecsleft=keys (%siteswr);
	$d='';
	if($norecsleft > 0) {
		open(STF,">$file");
		foreach my $l (sort keys (%siteswr)) {
			if($l && $siteswr{$l}) {
				$d .= "$l\t$siteswr{$l}\n";
				$didwrite=1;
				print STF "$l\t$siteswr{$l}\n";
			}
		}
		close(STF);
		if($memd) {
			$memd->set("allsitessel$ENV{'REMOTE_ADDR'}",$d,43200);
			$memd->set("settingdata$ENV{'REMOTE_ADDR'}",$file,86400);
			if($settings{initdir}) {$memd->set("initdir$ENV{'REMOTE_ADDR'}",$settings{initdir},86400);}
		}
		printerrsm("<h3>Record deleted</h3>\n<p>Record \"$in{sname}\" was deleted and Site file was updated.</p>");
	} ## END RECORDS LEFT
	else {
		if($memd) {
			$memd->set("allsitessel$ENV{'REMOTE_ADDR'}",$d,1);
			$memd->set("settingdata$ENV{'REMOTE_ADDR'}",$file,1);
		}
		`rm $file`;
		printerrsm("<h3>Record deleted</h3>\n<p>Record \"$in{sname}\" was deleted and Site file was removed as no more records remaining.</p>");
	}
} ## SITE DELETE END

sub writeasite {
	my($file,$didwrite,$d);
	unless($in{sname} && $in{suser} && $in{sip}) {
		printerrsm("<h3>No Input</h3>\n<p>In order to submit Site data all fields have to be filled.</p>");
	}
	if($memd->get("settingdata$ENV{'REMOTE_ADDR'}")) {
		$file=$memd->get("settingdata$ENV{'REMOTE_ADDR'}");
	} else {
		my $pr=$ENV{SCRIPT_FILENAME};	my @spf=split(/\//,$pr);	pop(@spf);	$pr = join '/',@spf;
		if(-f "$pr/datasettings.cgi") {
			eval {require "$pr/datasettings.cgi"};
			$file = $settings{sitefile};
		}
	}
	unless($file) {
		printerrsm("<h3>File error</h3>\n<p>Un-known file location to write Site Data.<br />Try submitting a file name first.</p>");
	}
	my %siteswr;
	if(-f $file) {
		$d = `cat $file`;	my @lns = split(/\n/,$d);	$d='';
		foreach my $l (@lns) {
			$l =~ s#(.*?)\t(.*?)\t(.*)##;
			$siteswr{$1}="$2\t$3";
		} ## FOREACH END
	} ## END FILE PRESENT
	$d='';
	foreach my $k (keys (%in)) {$in{$k} =~ s/\t//g;}
	$siteswr{$in{sname}} = "$in{suser}\t$in{sip}";
	open(STF,">$file");
	foreach my $l (sort keys (%siteswr)) {
		if($l && $siteswr{$l}) {
			$didwrite=1;
			print STF "$l\t$siteswr{$l}\n";
			$d .= "$l\t$siteswr{$l}\n";
		}
	}
	close(STF);

	if($didwrite) {
		if($memd) {
			$memd->set("allsitessel$ENV{'REMOTE_ADDR'}",$d,43200);
			$memd->set("settingdata$ENV{'REMOTE_ADDR'}",$file,43200);
			if($settings{initdir}) {$memd->set("initdir$ENV{'REMOTE_ADDR'}",$settings{initdir},86400);}
		}
		printerrsm("<h3>Data submitted</h3>\n<p>Sites file was written.</p>");
	} else {
		printerrsm("<h3>Data NOT submitted</h3>\n<p>No proper data was submitted thus nothing was written.</p>");
	}
} ## END SUB WRITE A SITE

sub writesitefile {
	unless($in{sitefile}) {
		printerrsm("<h3>File error</h3>\n<p>No file was provided.</p>");
	}
	my @archk = split(/\//,$in{sitefile});	pop(@archk);	my $dir=join '/', @archk;
	unless(-d $dir) {
		printerrsm("<h3>File writing error</h3>\n<p>No directory \"$dir\" available to write a Sites file.</p>");
	}
	my $pr=$ENV{SCRIPT_FILENAME};	my @spf=split(/\//,$pr);	pop(@spf);	$pr = join '/',@spf;
	if(-f "$pr/datasettings.cgi") {
		eval {require "$pr/datasettings.cgi"};
	}
	$settings{sitefile}=$in{sitefile};
		writetpsettings("$pr/datasettings.cgi"); ## WRITE SETTINGS FILE

	if($memd) {
		if($settings{initdir}) {$memd->set("initdir$ENV{'REMOTE_ADDR'}",$settings{initdir},86400);}
	}
	printerrsm("<h3>Data written</h3>\n<p>Record for Sites file location updated:<br />File: $in{sitefile}</p>");
} ## END WRITE SITE DATA FILE

sub clearmemd {
	if($memd) {
		$memd->flush_all;
		printerrsm("<h3>Session cleared</h3>\n<p>All data was removed as far as session opened Directories and a Site accessed.</p>");
	} else {
		printerrsm("<h3>Session NOT cleared</h3>\n<p>Something went wrong as access to Memcached was not available.</p>");
	}
} ## END CLEAR MEMCACHED DATA

sub settings {
	my($settingsdata,$file,$d,$wrf,$initdirf);
	if($memd->get("settingdata$ENV{'REMOTE_ADDR'}")) {
		$file=$memd->get("settingdata$ENV{'REMOTE_ADDR'}");
		$initdirf=$memd->get("initdir$ENV{'REMOTE_ADDR'}");
	} else {
		my $pr=$ENV{SCRIPT_FILENAME};	my @spf=split(/\//,$pr);	pop(@spf);	$pr = join '/',@spf;
		if(-f "$pr/datasettings.cgi") {
			eval {require "$pr/datasettings.cgi"};
			unless($@) {$file = $settings{sitefile};	$initdirf=$settings{initdir};}
		}
	}
	if($file) {
		if($memd) {
			$memd->set("settingdata$ENV{'REMOTE_ADDR'}",$file,86400);
			if($settings{initdir}) {$memd->set("initdir$ENV{'REMOTE_ADDR'}",$settings{initdir},86400);}
		}
	}
	$settingsdata = "<div class=\"formrow sett\"><label for=\"sitefile\" class=\"setform\"><span title=\"File where data for all Sites are kept. Enter a full path.\">Access Sites file</span>:</label>
<input type=\"text\" name=\"sitefile\" id=\"sitefile\" value=\"$file\">
<button onclick=\"setsitefile();return false;\" class=\"setupbutton\">Set</button></div>\n";
	if($file && -f $file) {
		$d = `cat $file`;	my @lns = split(/\n/,$d);	$d=0;
		foreach my $l (@lns) {
			$wrf .= "$l\n";
			$l =~ s#(.*?)\t(.*?)\t(.*)##;
			my($site,$usr,$ip) = ($1,$2,$3);
			if($site && $usr && $ip) {$d++;
$settingsdata .= "<div class=\"formrow sett\"><label for=\"s$d\" class=\"setform\">Site $d:</label>
<input type=\"text\" name=\"s$d\" id=\"s$d\" value=\"$site\" placeholder=\"Site Name\">
<input type=\"text\" name=\"u$d\" id=\"u$d\" value=\"$usr\" placeholder=\"SSH User\">
<input type=\"text\" name=\"ip$d\" id=\"ip$d\" value=\"$ip\" placeholder=\"IP or Domain\">
<button onclick=\"sitesubmit('$d');return false;\" class=\"setupbutton\">Update</button>
<button onclick=\"sitedelete('$d');return false;\" class=\"setupbutton bred\">Delete</button></div>\n";
			}
		}
		if($memd) {$memd->set("allsitessel$ENV{'REMOTE_ADDR'}",$wrf,43200);}
	}
$d++;
$settingsdata .= "<div class=\"formrow sett\"><label for=\"s$d\" class=\"setform\">Site $d:</label>
<input type=\"text\" name=\"s$d\" id=\"s$d\" placeholder=\"Site Name\">
<input type=\"text\" name=\"u$d\" id=\"u$d\" placeholder=\"SSH User\">
<input type=\"text\" name=\"ip$d\" id=\"ip$d\" placeholder=\"IP or Domain\">
<button onclick=\"sitesubmit('$d');return false;\" class=\"setupbutton\">Create</button></div>\n";

$settingsdata .= "<div class=\"formrow sett\"><label for=\"initdir\" class=\"setform\"><span title=\"Local directory initially opened on Refresh\">Initial Local Directory</span>:</label>
<input type=\"text\" name=\"initdir\" id=\"initdir\" placeholder=\"/home/user\" value=\"$initdirf\">
<button onclick=\"initialdir();return false;\" class=\"setupbutton\">Set</button></div>\n";

	$settingsdata .= "<div class=\"formrow\"><a href=\"#\" onclick=\"clearsession();return false;\"><span title=\"Removes all saved data for this session.\">Clear Cache for this <b>Session</b></span></a></div>\n";

	printerrsm("<h3>Settings</h3>\n<p><form>$settingsdata</form></p>");
} ## END SETTINGS

sub folderwrite {
	$in{file} =~ s# #\_#g;
	unless($in{file}) {printerrsm("<h3>No File selected</h3>\n<p>No Directory Name provided.</p>");}
	unless($in{side}) {printerrsm("<h3>Location Missing</h3>\n<p>Where to create new Directory is not specified. I.e. Local or on a Server</p>");}
	readdirs();
	unless($remdir && $locdir) {
printerrsm("<h3>Directory Error</h3>\n<p>Local and Remote Directories has to be selected for this operation to work.<br />Refresh both sides Home and Server.</p>");
	}
	if($in{side} eq 'local') {
		`mkdir -p '$locdir/$in{file}'`;
	} else { ## END LOCAL
		unless($memd) {printerrsm('<h3>Memd Error</h3><p>Server credentials not available. Can not continue!</p>');}
		$servr=$memd->get("siteby$ENV{'REMOTE_ADDR'}");
		unless($servr) {printerrsm('<h3>No Server Address</h3><p>Server Login is not present. Can not continue!</p>');}
			`ssh $servr "mkdir -p '$remdir/$in{file}'"`;
	} ## END REMOTE
	printerrsm("<h3>Directory created</h3><p>Directory \"<b>$in{file}</b>\" was created.</p>");
}

sub folderget {
		my $info = "<h3>Create Directory</h3>
<p><input type=\"text\" class=\"inptxt\" name=\"file\" id=\"file\" placeholder=\"Type Name here\">
<button class=\"flbtn\" style=\"margin-right: 1rem;\" onclick=\"newfolderdo('$in{side}')\">Create</button>\n</p>";
	printerrsm($info);
}

sub actualtrash {
	unless($memd) {printerrsm('<h3>Memd Error</h3><p>Server credentials not available. Can not continue!</p>');}
	$servr=$memd->get("siteby$ENV{'REMOTE_ADDR'}");
	unless($servr) {printerrsm('<h3>No Server Address</h3><p>Server Login is not present. Can not continue!</p>');}
	my $spr=' __ ';				my $printres;
	my @rd = split(/$spr/,$in{file});	delete $in{file};
	foreach my $fr (@rd) {
		my $isdir;					my $ffhtml='File';
		if($fr =~ m/\|d$/) {$isdir=' -rf';	$fr =~ s#\|d$##;	$ffhtml='Directory';}
		if($in{side} eq 'local') {
			`rm$isdir '$locdir/$fr'`;
		} else { ## END LOCAL
			`ssh $servr "rm$isdir '$remdir/$fr'"`;
		} ## END REMOTE
		$printres .= "<li>$ffhtml\: <b>$fr</b</li>\n";
	} ## FOREACH FILE END
	chomp $printres;
	printerrsm("<h3>Removed the following items</h3>\n<p><ul>$printres</ul></p>");
} ## END ACTUAL TRASH

sub pretrash {
	my $spr=' __ ';				$in{file} =~ s#$spr$##;
	my @rd = split(/$spr/,$in{file});	delete $in{file};
	my $printfile;
	my $nofl=0;
	foreach my $fr (@rd) {
		unless($fr) {next;}
		$nofl++;
		$fr =~ s#\|m(\d+)##;	$fmode=$1;
		if($fmode eq '000') {next;}
		my $fprnt=$fr;
		my $rnmwhat='file';
		if($fr =~ m/\|d/) {$rnmwhat='directory';	$fprnt =~ s/\|d$//;}
		$printfile .= "<li><b>$fprnt</b> &nbsp; \[$rnmwhat $fmode\]</li>\n";
		$in{file} .= "$fr\n";
	} ## FOREACH FILE END
	chomp $printfile;	chomp $in{file};	$in{file} =~ s#\n#$spr#g;
	my $info = "<h3>Check before proceeding</h3>
<p>Removing:<ul>$printfile</ul></p>
<p><input type=\"hidden\" name=\"file\" id=\"file\" value=\"$in{file}\">
<button class=\"flbtn\" style=\"margin-right: 1rem;\" onclick=\"trashit('$in{side}')\">Remove</button>\n
<a href=\"#\" onclick=\"hidebox();return false;\"><button type=\"submit\" class=\"flbtn greyb\">Cancel</button></a></p>";
	printerrsm($info);
} ## END PRE-TRASH

sub changemode {
	my($isdir,$info,$ffhtml,$recsv);
	$in{recursive} =~ s/\D//g;
	if($in{file} eq '..|d') {$in{file}='';}
	unless($in{file}) {printerrsm("<h3>Mode change error</h3>\n<p>Filename/Directory has to be provided.</p>");}
	unless($in{side}) {printerrsm("<h3>Location Missing</h3>\n<p>Where file located not specified. I.e. Local or on a Server</p>");}
	readdirs();
	unless($remdir && $locdir) {
printerrsm("<h3>Directory Error</h3>\n<p>Local and Remote Directories has to be selected for File View to work.<br />Refresh both sides Home and Server.</p>");
	}
	if($in{om} eq $in{nm}) {
		printerrsm("<h3>No mode change</h3>\n<p><b>$in{om}</b> equal <b>$in{nm}</b><br />- no mode changes found.</p>");
	}
	$in{nm} =~ s/\D//g;
	if(length($in{nm}) != 3) {
		printerrsm("<h3>Bad Mode</h3>\n<p><b>$in{nm}</b> mode is <b>$in{nm}</b><br />Mode accepted in digits only.</p>");
	}
	$in{nm} =~ s#(\d{1})(\d{1})(\d{1})#$1$2$3#;	my($mt1,$mt2,$mt3) = ($1,$2,$3);
	if(($mt1 > 7 || $mt2 > 7 || $mt3 > 7) ||
	($mt1 == 2 || $mt2 == 2 || $mt3 == 2) || ($mt1 == 3 || $mt2 == 3 || $mt3 == 3)) {
		printerrsm("<h3>Invalid Mode</h3>\n<p>Mode: <b>$in{nm}</b> is not valid.</p>");
	}

	if($in{file} =~ m/\|d/) {$isdir=1;	$in{file} =~ s#\|d$##;	$ffhtml='Directory';}
	if($in{recursive}) {$recsv=' -R';}
	if($in{side} eq 'local') {
		`chmod$recsv 0$in{nm} '$locdir/$in{file}'`;
	} else { ## END LOCAL
		unless($memd) {printerrsm('<h3>Memd Error</h3><p>Server credentials not available. Can not continue!</p>');}
		$servr=$memd->get("siteby$ENV{'REMOTE_ADDR'}");
		unless($servr) {printerrsm('<h3>No Server Address</h3><p>Server Login is not present. Can not continue!</p>');}
			`ssh $servr "chmod$recsv 0$in{nm} '$remdir/$in{file}'"`;
	} ## END REMOTE
	printerrsm("<h3>$ffhtml mode changed</h3><p>$ffhtml \"<b>$in{file}</b>\" mode now: \"<b>$in{nm}</b>\"</p>");
} ## END CHANGE MODE

sub changename {
	my($isdir,$info,$ffhtml);
	if($in{oldfile} eq '..|d') {$in{oldfile}='';}
	unless($in{oldfile} && $in{newfile}) {printerrsm("<h3>File change error</h3>\n<p>New and Old filenames has to be submitted.</p>");}
	unless($in{side}) {printerrsm("<h3>Location Missing</h3>\n<p>Where file located not specified. I.e. Local or on a Server</p>");}
	readdirs();
	unless($remdir && $locdir) {
printerrsm("<h3>Directory Error</h3>\n<p>Local and Remote Directories has to be selected to rename file/directory.<br />Refresh both sides Home and Server.</p>");
	}
	if($in{oldfile} eq $in{newfile}) {
		printerrsm("<h3>Identical names</h3>\n<p><b>$in{oldfile}</b> equal <b>$in{newfile}</b><br />- no changes found in name.</p>");
	}
	$ffhtml='File';
	if($in{oldfile} =~ m/\|d/) {$isdir=1;	$in{oldfile} =~ s#\|d$##;	$ffhtml='Directory';}
	if($in{side} eq 'local') {
		$info = `ls -la "$locdir/$in{oldfile}"`;
		unless($info =~ m/no such/i) {
			`mv '$locdir/$in{oldfile}' '$locdir/$in{newfile}'`;
			$info = `ls -la '$locdir/$in{newfile}'`;
		} else { ## END FILE/DIR PRESENT
			printerrsm("<h3>$ffhtml Error</h3><p>$ffhtml \"$in{oldfile}\" not found. Can not change name!</p>");
		} ## END NO FILE
	} else { ## END LOCAL
		unless($memd) {printerrsm('<h3>Memd Error</h3><p>Server credentials not available. Can not continue!</p>');}
		$servr=$memd->get("siteby$ENV{'REMOTE_ADDR'}");
		unless($servr) {printerrsm('<h3>No Server Address</h3><p>Server Login is not present. Can not continue!</p>');}
		$info = `ssh $servr "ls -la '$remdir/$in{oldfile}'"`;
		unless($info =~ m/no such/i) {
			`ssh $servr "mv '$remdir/$in{oldfile}' '$remdir/$in{newfile}'"`;
			$info = `ssh $servr "ls -la '$remdir/$in{newfile}'"`;
		} else { ## END FILE/DIR PRESENT
			printerrsm("<h3>$ffhtml Error</h3><p>$ffhtml \"$in{oldfile}\" not found. Can not change name!</p>");
		}
	} ## END REMOTE
	if($info =~ m/no such/i) {
		printerrsm("<h3>$ffhtml renaming error</h3><p>$ffhtml \"$in{oldfile}\" was not renamed</p>");
	}
	printerrsm("<h3>$ffhtml renamed</h3><p>$ffhtml \"$in{oldfile}\" renamed: \"$in{newfile}\"</p>");
} ## END SUB CHANGE NAME

sub prepfile {
	unless($in{file}) {printerrsm("<h3>No File selected</h3>\n<p>No file/directory selected.</p>");}
	unless($in{side}) {printerrsm("<h3>Location Missing</h3>\n<p>Where file/directory located is not specified. I.e. Local or on a Server</p>");}
	readdirs();
	unless($remdir && $locdir) {
printerrsm("<h3>Directory Error</h3>\n<p>Local and Remote Directories has to be selected for this operation to work.<br />Refresh both sides Home and Server.</p>");
	}
	if($in{do} eq 'trash') {pretrash();}
	elsif($in{do} eq 'trashdo') {actualtrash();}
	my $spr=' __ ';		$in{file} =~ s#$spr$##;
	my @rd = split(/$spr/,$in{file});	delete $in{file};
	my $fr = shift(@rd);	@rd=();		$fr =~ s#\|m(\d+)##;	$fmode=$1;
	if($in{do} eq 'view') {viewfile($fr);}
	elsif($in{do} eq 'info') {getfileinfo($fr);}
	elsif($in{do} eq 'rename') {renaming($fr);}
} ## END PREP FILE SUB

sub renamepre {
	my $spr=' __ ';
	my @rd = split(/$spr/,$in{file});	delete $in{file};
	$in{file} = shift(@rd);	@rd=();		my $rnmwhat='File';
	$in{file} =~ s#$spr$##;			$in{file} =~ s#\|m(\d+)##;	$fmode=$1;
	if($in{file} =~ m/\|d/) {$rnmwhat='Directory';}
	my $oldflpr=$in{file};	$oldflpr =~ s#\|d$##;
	my $info = "<h3>Rename $rnmwhat</h3>\n<p>\n<input type=\"hidden\" name=\"oldname\" id=\"oldname\" value=\"$in{file}\">
<span class=\"frmlbl\">New Name:</span> <input class=\"inptxt\" type=\"text\" id=\"newname\" name=\"newname\" value=\"$oldflpr\">
<button class=\"flbtn\" style=\"margin-left: .6rem;\" onclick=\"renamefile('$in{side}')\">Rename</button>\n</p>";
	printerrsm($info);
} ## END SUB RENAME PRE

sub readfileinfo {
	my $frread=shift;	my($info,$exif);
	$info = `file "$frread"`;
	$exif = `exiftool "$frread"`;
	if($exif) {chomp $info;	$info .= "\n\nExif:\n$exif\n";}
	return $info;
}

sub getfileinfo {
	my $fr=shift;	my $frhtm=$fr;
	my($isdir,$info);
	if($fr =~ m/\|d$/) {
		$fr =~ s#\|d##;	$isdir=1;
	} ## END DIR
	my $frsvd=$fr;		$frsvd =~ s/^\.+//;	$frsvd =~ s/ /\_/g;
	my $frsh=$fr;		$frsh =~ s# #\\ #g;

	if($in{side} eq 'local') {
		if($isdir) {
			$info = `ls -la "$locdir/$fr" | wc -l`;			$info =~ s/ //g;
			$info = "Items in Directory: $info";
		} else { ## END DIR
			if(-f "$locdirsh/$fr") {$info=readfileinfo("$locdirsh/$fr");}
		} ## END FILE
	} else { ## END LOCAL
		unless($memd) {printerrsm('<h3>Memd Error</h3><p>Server credentials not available. Can not continue!</p>');}
		$servr=$memd->get("siteby$ENV{'REMOTE_ADDR'}");
		unless($servr) {printerrsm('<h3>No Server Address</h3><p>Server Login is not present. Can not continue!</p>');}
		if($isdir) {
			$info = `ssh $servr ls -la "$remdirsh/$frsh" | wc -l`;	$info =~ s/ //g;
			$info = "Items in Directory: $info";
		} else {
			`scp $servr:"$remdirsh/$frsh" $path/temp/$frsvd`;
			$info=readfileinfo("$path/temp/$frsvd");
		}		
	} ## END REMOTE
	my $recurs;
	if($isdir) {$recurs = "\n<span class=\"smchkb\">Recursively: <input type=\"checkbox\" name=\"recurs\" id=\"recurs\" value=\"1\"></span>";}
	my $form="\n<p>
<input type=\"hidden\" name=\"filename\" id=\"filename\" value=\"$frhtm\">
<input type=\"hidden\" name=\"oldmode\" id=\"oldmode\" value=\"$fmode\">
<div class=\"rawline\"><span class=\"frmlbl\">Mode:</span> <span><input class=\"inpsmtx\" type=\"text\" name=\"filemode\" id=\"filemode\" value=\"$fmode\"></span>$recurs
<span><button class=\"flbtn\" style=\"margin-left: .6rem;\" onclick=\"changethatmode('$in{side}')\">Change Mode</button></span></div>\n</p>";
	printerrsm("<h3>$fr (mode: $fmode)</h3>$form\n<p><pre><tt>$info</tt></pre></p>");

} ## END SUB GET FILE INFO

sub viewfile {
	my $fr=shift;
	if($fr =~ m/\|d$/) {
		$fr =~ s#\|d##;
		printerrsm("<h3>Folder Selected</h3>\n<p>Can not View Folder:<br />\n<b>$fr</b></p>");
	}
	my $frsvd=$fr;		$frsvd =~ s/^\.+//;	$frsvd =~ s/ /\_/g;
	my $frsh=$fr;		$frsh =~ s# #\\ #g;
	if($in{side} eq 'local') {
		if(-f "$locdir/$fr") {
			`cp "$locdirsh/$fr" $path/temp/$frsvd`;
		}
	} else { ## END LOCAL
		unless($memd) {printerrsm('<h3>Memd Error</h3><p>Server credentials not available. Can not continue!</p>');}
		$servr=$memd->get("siteby$ENV{'REMOTE_ADDR'}");
		unless($servr) {printerrsm('<h3>No Server Address</h3><p>Server Login is not present. Can not continue!</p>');}
		`scp $servr:"$remdirsh/$frsh" $path/temp/$frsvd`;
	} ## END REMOTE
	unless(-f "$path/temp/$frsvd") {
		printerrsm("<h3>File not found</h3>\n<p>File \"$frsvd\" was not found for display.<br />\nPlease try again.</p>");
	}
	`chmod 777 $path/temp/$frsvd`;
	my $ftype = `file $path/temp/$frsvd`;
	
	if($frsvd =~ m/\.(txt|cgi|pl|conf|xml|json|log)$/i || $frsvd =~ m/_(log)$/i || $ftype =~ m/\btext\b|ACCII|SQLite/i) {
		my $rdtext = `cat $path/temp/$frsvd`;
		$rdtext =~ s#<#\&lt;#g;		$rdtext =~ s#>#\&gt;#g;
		printerrsm("<h3>$fr</h3>\n<p><pre><tt>$rdtext</tt></pre></p>\n<p>File Info: $ftype</p>");
	} ## END TEXT
	if($frsvd =~ m/\.(jpg|jpeg|gif|png|webp)$/i) {
		printerrsm("<h3>$fr</h3>\n<p><img src=\"/site/temp/$frsvd\"></p>\n<p>File Info: $ftype</p>");
	} else { ## END IMAGE
		printerrsm("<h3>$fr</h3>\n<p><a target=\"_blank\" href=\"/site/temp/$frsvd\">Download $fr</a></p>\n<p>File Info: $ftype</p>");
	} ## END ANYTHING ELSE
} ## END VIEW FILE SUB

sub movefiles {
$|++;
	unless($in{files}) {
		printerrsm("<h3>File(s) Missing</h3>\n<p>No file(s) selected for $in{do}.</p>");
	}
	readdirs();
	unless($remdir && $locdir) {
		printerrsm("<h3>Directory Error</h3>\n<p>Local and Remote Directories has to be selected for Upload to work.</p>");
	}
	unless($memd) {printerrsm('<h3>Memd Error</h3><p>Server credentials not available. Can not continue!</p>');}
	$servr=$memd->get("siteby$ENV{'REMOTE_ADDR'}");
	unless($servr) {printerrsm('<h3>No Server Address</h3><p>Server Login is not present. Can not continue!</p>');}
	my $spr=' __ ';		$in{files} =~ s#$spr$##;
	my @files = split(/$spr/,$in{files});
	my $totFiles=@files;
	my $report;
	my $hdrhtm=$in{do};	$hdrhtm =~ s/\b\w/\u$&/g;
	if($in{do} eq 'upload') {
		$report='<h3>Uploaded:</h3><ol>';
	} else {
		$report='<h3>Downloaded:</h3><ol>';
	}
	my($bld,$blde);
	my $flcnt=0;
	foreach my $file (@files) {
		$flcnt++;
		my $filewr=$file;	$filewr =~ s#\|d$##;	$filewr =~ s#\|m\d{3}##;
		if($memd) {
			$memd->set("movingfiles$ENV{'REMOTE_ADDR'}","$totFiles$spr$flcnt$spr Downloading: $filewr",5);
			$memd->set("startedfiles$ENV{'REMOTE_ADDR'}",1,7200);
		}
		if($flcnt < 2) {sleep(2);}
		if($bld) {$bld='';	$blde='';} else {$bld='<b>';	$blde='</b>';}
		$file =~ s#\|m\d{3}##;
		if($file =~ m/\|d$/) {
			$file =~ s#\|d$##;
			if($in{do} eq 'upload') {
				`ssh $servr "mkdir -p '$remdir/$file'"`;
				`rsync -az --stats -e ssh "$locdir/$file" $servr:"$remdir"`;
				$report .= "<li>$bld$locdir/$file/ -&gt;\n$remdir/$file$blde</li>\n";
			} else {
				$report .= "<li>$bld$remdir/$file/\* -&gt;\n$locdir/$file$blde</li>\n";
				`rsync -az -e ssh $servr:"$remdir/$file" "$locdir"`;
			}
		} ## END DIR
		else {
			if($in{do} eq 'upload') {
				$report .= "<li>$bld$locdir/$file -&gt;\n$remdir/$file$blde</li>\n";
				`scp "$locdir/$file" $servr:"$remdir/$file"`;
			} else {
				$report .= "<li>$bld$remdir/$file -&gt;\n$locdir/$file$blde</li>\n";
				`scp $servr:"$remdir/$file" "$locdir/$file"`;
			}
		}
	}
	$report .= "</ol></p>";
	if($memd) {
		$memd->set("movingfiles$ENV{'REMOTE_ADDR'}","$report",5);
		$memd->set("startedfiles$ENV{'REMOTE_ADDR'}",1,1); ## KILL THE RECORD
	}
#	printerrsm($report);

} ## END SUB UPLOAD

sub changedir {
	$in{dirname} =~ s#\|d$##;
	$in{dirname} =~ s#\|m(\d+)##;
	$in{mvfrom} =~ s#\|d$##;
	$in{mvfrom} =~ s#\|m(\d+)##;
	if($in{dirname} eq '..') {
		my @ct = split(/\//,$in{mvfrom});		pop(@ct);
		if($in{dirtp} =~ m/^rem/) {
			my $nmblft = @ct;
			if($nmblft > 1) {
				$in{mvfrom} = join '/', @ct;
			}
		} else {
			$in{mvfrom} = join '/', @ct;
		}
		$in{mvfrom} =~ s/\/+$//;
	} ## END UP DIR
	else {
		$in{mvfrom} =~ s/\/+$//;	$in{mvfrom} =~ s/\s+$//;
		$in{dirname} =~ s/\s+$//;
		$in{mvfrom} .= "/$in{dirname}";
	} ## END NEXT DIR
	if($memd) {$in{which}=writedir($in{dirtp},$in{mvfrom});}
#print "Content-type: text/txt\n\n";
#print "<p>Which: $in{which}</p>\n<p>New Dir: $in{mvfrom}<br />Dir: $in{dirname}<br />Which: $in{which}<br />Site: $siteuse</p>";	exit(0);
	if($in{which}) {
		dorefresh();
	} else {
		printerrsm("<h3>Server Missing</h3><p>Where to write (server) not defined</p>
<p>Try to <a href=\"#\" onclick=\"clearsession();return false;\">Clear Cache for this session</a></p>");
	}
} ## END CHANGE DIR SUB

sub dorefresh {
	my($idn,$topdata,$idtp,$click,$remdirread,$locdirread,$oncl,$chname);
	if($memd) {
		unless($remdir && $locdir) {readdirs();}
	}
	if($remdir) {$remdirread=" $remdirsh";}
	unless($locdir) {
		if($memd->get("initdir$ENV{'REMOTE_ADDR'}")) {$locdir=$memd->get("initdir$ENV{'REMOTE_ADDR'}");}
	}
	unless($locdir) {
		unless(%settings) {
			my $pr=$ENV{SCRIPT_FILENAME};	my @spf=split(/\//,$pr);	pop(@spf);	$pr = join '/',@spf;
			if(-f "$pr/datasettings.cgi") {
				eval {require "$pr/datasettings.cgi"};
			}
		}
		if($settings{initdir}) {
			$locdir=$settings{initdir};
		} else {
			$locdir='/home'; ## FALL TO UNIX DEFAULT HOME DIRECTORY CHANGE ACCORDINGLY
		}
	} ## END NO LOCAL DIR
	$locdirread=" $locdir";
	print "Content-type: text/txt\n\n";
	writedir('anything',$locdir);
	my $idname;	my $cnt=0;	my $src="<form>";	my @lnz;
	if($in{which} eq 'local') {
		$chname='lcl';
		$idname='locfilelist';		$idn='lc';	$idtp='locdir';
		my $res = `ls -la$locdirread`;	@lnz = split(/\n/,$res);	shift(@lnz);	shift(@lnz);
		$topdata = $locdir;
	}
	elsif($in{which} eq 'remote') {
		$chname='rmt';
		$idname='remfilelist';		$idn='rm';	$idtp='remdir';
		unless($memd->get("siteby$ENV{'REMOTE_ADDR'}")) {
			printerrsm('<h3>Website Error</h3><p>No Website selected</p>');
		}
		$servr=$memd->get("siteby$ENV{'REMOTE_ADDR'}");
		my $res = `ssh $servr 'ls -la$remdirread'`;	@lnz = split(/\n/,$res);	shift(@lnz);	shift(@lnz);
		unless($remdir) {
			$topdata = `ssh $servr 'pwd'`;
			$remdir=$topdata;
			if($siteuse) {
				my $siteusewr=$siteuse;		$siteusewr =~ s/\W//g;
				$memd->set("curdrrem$siteusewr$ENV{'REMOTE_ADDR'}",$remdir,43400);
			}
		} else {
			$topdata=$remdir;
		}
	}
	else {printerrsm('<h3>Request Error</h3><p>Did not receive a proper request, nothing to do.</p>');}
	my $dircnt=0;	my $filecnt=0;
	my %cnv=('r','4','w','2','x','1','-','0');
	foreach my $l (@lnz) {
		$click='';	$oncl='';
		my($kb,$dcls,$tdr,$mdprnt);
		$l =~ tr/  //s;
		$l =~ s#(.*?) (.*?) (.*?) (.*?) (.*?) (.*?) (.*?) (.*?) (.*)##;
		my($ft,$nm,$usr,$grp,$sz,$mo,$da,$yt,$fn)=($1,$2,$3,$4,$5,$6,$7,$8,$9);
		$fn =~ s/\s+$//;	my $year=$yr;	my $ftime=' 00:00';
		my($filetime,$cmode,$dr);
		if($fn =~ m/DS_Store/) {next;}
		unless($fn eq '..') {
			$mo=$digmn{$mo};
			if(length($da) < 2) {$da="0$da";}
			unless($yt =~ m/\:/) {
				$year=$yt;
			} else {
				$ftime=" $yt";
			}
			$filetime="<f>$mo/$da/$year$ftime</f>";
$ft =~ s#([\w|\-]{1})([\w|\-]{1})([\w|\-]{1})([\w|\-]{1})([\w|\-]{1})([\w|\-]{1})([\w|\-]{1})([\w|\-]{1})([\w|\-]{1})([\w|\-]{1})#$1$2$3$4$5$6$7$8$9$10#;
			my($dr1,$u1,$u2,$u3,$g1,$g2,$g3,$a1,$a2,$a3) = ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10);
			$dr=$dr1;
			my $usr = ($cnv{$u1} + $cnv{$u2}) + $cnv{$u3};
			my $grp = ($cnv{$g1} + $cnv{$g2}) + $cnv{$g3};
			my $alu = ($cnv{$a1} + $cnv{$a2}) + $cnv{$a3};
			$mdprnt="\|m$usr$grp$alu";
			$cmode="<c>$usr$grp$alu</c>";
#			if($cmode =~ m/1/) {$cmode="&nbsp;$cmode";}
#			if($filetime =~ m/1/) {$filetime="&nbsp;$filetime";}
		} else {
			if($ft =~ m/^d/) {$dr='d';}
		}
		$sz /= 1024;	$kb=' Kb';
		if($sz > 1000) {$sz /= 1024;	$kb=' Mb';}
		$sz = sprintf("%0.2f",$sz);	$sz .= $kb;
		$cnt++;
		$oncl=' onchange="vr(\''.$idn.$cnt.'\', \''.$chname.'\');return false;"';
		if($dr eq 'd') {
			$tdr='|d';
			$dircnt++;
			$dcls=' itdr';
			$click=' ondblclick="chdirs(\''.$idn.$cnt.'\', \''.$idtp.'\');return false;"';
		} else {
			$filecnt++;
		}
		if($fn eq '..') {
			$sz='<i class="fa fa-reply-all fa-rotate-90"></i>';
			$dcls=' tpbld';
			$oncl='';
		}
	my $fnprint=$fn;
	if(length($fnprint) > 45) {my $dts='..';	$fnprint =~ s#(.{21})(.*?)(.{22})$#$1$dts$3#;}
	$src .= "<div class=\"frmr\">
<input id=\"$idn$cnt\" class=\"ckb\" type=\"checkbox\" name=\"$chname\" value=\"$fn$mdprnt$tdr\"$oncl>
<label for=\"$idn$cnt\" class=\"ckl$dcls\"$click>$fnprint<span>$sz$filetime$cmode</span></label>\n</div>\n";
	} ## FOREACH END

	$dircnt--;
	my $dircntht='';
	if($dircnt > 0) {$dircntht = " &nbsp; Directories: $dircnt";}
	$cnt--;
	$src .= "<div class=\"frmr\">\n<div class=\"btmhd\">Items: $cnt &nbsp; Files: $filecnt $dircntht</div>\n</div>\n";

	$src.="</form>";
	print $src.' --- '.$idname.' --- '.$topdata.' --- '.$idtp;
} ## END REFRESH

sub setwebsite {
unless($in{sitename}) {printerrsm('<h3>Website Error</h3><p>No site name was provided - nothing to add</p>');}
print "Content-type: text/txt\n\n";
my($user,$stip) = split(/ /,$in{sitename});
my $login="$user\@$stip";
my $selted="$user $stip";
if($memd) {
	$memd->set("siteby$ENV{'REMOTE_ADDR'}",$login,86400);
	$memd->set("siteselected$ENV{'REMOTE_ADDR'}",$selted,86400);
	print "<h1>Site Selected</h1>\n<p>Site is set to: <b>$login</b></p>";
} else {
	print "<h1>Memcached Error</h1><p>No site was set.</p>";
}
exit(0);
} ## END SET WEBSITE

sub writedir {
	my($writewich,$newdir)=@_;	my $written='';
	$writewich =~ s#\|d$##;
	$newdir =~ s#\|d$##;
	if($newdir) {
		$siteuse=$memd->get("siteselected$ENV{'REMOTE_ADDR'}");		my $siteusewr=$siteuse;		$siteusewr =~ s/\W//g;
		if($writewich =~ m/^rem/) {
			$written = 'remote';
			$memd->set("curdrrem$siteusewr$ENV{'REMOTE_ADDR'}",$newdir,43400);
		} else {
			$written = 'local';
			$memd->set("curdrloc$siteusewr$ENV{'REMOTE_ADDR'}",$newdir,43400);
		}
#my $test = $memd->get("curdrrem$siteusewr$ENV{'REMOTE_ADDR'}");
#print "Content-type: text/txt\n\n";
#print "<h3>Writing</h3>\n<p>Where: $writewich/$written<br />Dir: $newdir<br />Site Rec: $siteuse<br />
#Site Use: $siteusewr<br />\nResult: $test</p>";	exit(0);
		return $written;
	} else {
		return;
	}
} ## END WRITE DIR SUB

sub readdirs {
	$siteuse=$memd->get("siteselected$ENV{'REMOTE_ADDR'}");
	my $siteusewr=$siteuse;		$siteusewr =~ s/\W//g;
	if($memd->get("curdrrem$siteusewr$ENV{'REMOTE_ADDR'}")) {
		$remdir=$memd->get("curdrrem$siteusewr$ENV{'REMOTE_ADDR'}");
	}
	if($memd->get("curdrloc$siteusewr$ENV{'REMOTE_ADDR'}")) {
		$locdir=$memd->get("curdrloc$siteusewr$ENV{'REMOTE_ADDR'}");
	}
	$remdir =~ s#\s+$##;	$remdir =~ s#\/+$##;	$remdir =~ s#\s+$##;
	$locdir =~ s#\s+$##;	$locdir =~ s#\/+$##;	$locdir =~ s#\s+$##;
	$remdirsh=$remdir;	$remdirsh =~ s# #\\ #g;
	$locdirsh=$locdir;	$locdirsh =~ s# #\\ #g;
} ## END GET DIRS

sub printerrsm {
	my $err=shift;
	print "Content-type: text/txt\n\n$err";
	exit(0);
} ## END SUB PRINT SMALL ERROR

sub createindex {
	my $file=shift;
	open(IND,">$file");
	print IND <<EOH;
#!/usr/bin/env perl
use strict;
use warnings;
print "Content-type: text/html\\n\\n<p>Nothing to show</p>\\n";	exit(0);
EOH
	close(IND);
	`chmod 711 $file`;
} ## END CREATE INDEX FILE

sub writetpsettings {
	my $fw=shift;
	open(TXF,">$fw");	print TXF "\%settings=(\n";	my $cma="\t";
	foreach my $k (sort keys (%settings)) {
		$settings{$k} =~ s/\'/\\\'/g;
		print TXF "$cma'$k','$settings{$k}'";	$cma=",\n\t";
	}
	print TXF "\n);\n";	close(TXF);
}

sub helpshow {
	my $text="<p><b>First things first</b><ul>
<li>This program works only with servers with established Password-less access VIA SSH Keys</li>
<li>Prerequisites:
	<ul>
	<li>Mamcached</li>
	<li>Web Server on your LAN machine.</li>
	<li>Scripting language. This version written in Perl</li>
	<li>Adjust \$PATH in all .cgi files according to your local server settings</li>
	</ul>
</li>
</ul></p>
<p><b>Settings</b><ul>
<li>Click on &nbsp;<i class=\"fa fa-gear\"></i>&nbsp; to create/edit basic Settings.
<ul>
<li><u>Access Sites file</u> -- file where Remote server credentials are kept. Best if file is not accessible by browser.</li>
<li><u>Site 1, Site 2 ..</u> -- Enter credentials for every server you need to access.</li>
<li><u>Initial Local Directory</u> -- this directory will be accessed on your local machine when &nbsp;<i class=\"fa fa-refresh\"></i>&nbsp; icon clicked.</li>
<li><u>Clear Cache for this Session</u> -- use this link when remote or local directory can not be refreshed.</li>
</ul></li>
<li>Hover over icons to see what it does.</li>
<li>To change directory - just double-click on directory.<br />
to go \"Up\" directory tree - double-click on &nbsp;<i class=\"fa fa-reply-all fa-rotate-90\"></i></li>
</ul></p>
<p>Report any errors or <a target=\"_blank\" href=\"https:/www.codemacs.com/contact/\">contact us here</a></p>";
	printerrsm("<h3>POEM-HOPKY V1.0 -- Getting started</h3>\n$text");
} ## END SHOW HELP
