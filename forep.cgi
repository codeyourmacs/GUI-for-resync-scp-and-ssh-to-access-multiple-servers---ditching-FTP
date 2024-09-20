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

my($title,$sitesel,$memd);

our %in;
if($ENV{QUERY_STRING}) {
	if(-f "/http/web/cgi-lib.pl") {eval {require "/http/web/cgi-lib.pl"};
	unless($@) {ReadParse();}
	} ## INPUT LIBRARY
} ## END IF DATA PRESENT

print "Content-type: text/txt\n\n";
eval {use Cache::Memcached};
unless($@) {
	$memd = new Cache::Memcached {'servers' => ['localhost:11211'],'debug' => 0,'compress_threshold' => 10_000,};
	if($memd->get("movingfiles$ENV{'REMOTE_ADDR'}")) {
		print $memd->get("movingfiles$ENV{'REMOTE_ADDR'}");
	}
	else {
		unless($memd->get("startedfiles$ENV{'REMOTE_ADDR'}")) {
			print "No data";
		} else {
			print "Downloading";
		}
	}
} ## END GOOD EVAL
else {
print "Memcached Error";
}

exit(0);