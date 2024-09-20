// Project Name: POEM-HOPKY V1.0
// Description: HTML GUI for SSH/SCP/rsync
// Author: CodeMacs.com (Web Design Co.)
// License: GNU General Public License v3.0
// 
// Copyright (C) 2024 CodeMacs.com/wd-co.com
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see <https://www.gnu.org/licenses/>.

function help() {
    let formfields = 'do=help';
    sendformdata(formfields,'','');
}
function initialdir() {
    let locDir=document.getElementById('initdir').value;
    let formfields = 'do=dirinit&initdir=' + encodeURIComponent(locDir);
    sendformdata(formfields,'','');
}

function sitesubmit(nmb) {
    let siteName='s' + nmb;
    siteName=document.getElementById(siteName).value;
    let siteUser='u' + nmb;
    siteUser=document.getElementById(siteUser).value;
    let siteIP='ip' + nmb;
    siteIP=document.getElementById(siteIP).value;
    let formfields = 'do=sitesubmit&sname=' + encodeURIComponent(siteName) + '&suser=' + encodeURIComponent(siteUser) + '&sip=' + encodeURIComponent(siteIP);
    sendformdata(formfields,'','');
}
function sitedelete(nmb) {
    let siteName='s' + nmb;
    siteName=document.getElementById(siteName).value;
    let formfields = 'do=sitedelete&sname=' + encodeURIComponent(siteName);
    sendformdata(formfields,'','');
}
function setsitefile() {
    let fileName=document.getElementById('sitefile').value;
    let formfields = 'do=writesitefile&sitefile=' + encodeURIComponent(fileName);
    sendformdata(formfields,'','');
}
function clearsession() {
    let formfields = 'do=clearsess';
    sendformdata(formfields,'','');
}
function settings() {
    let formfields = 'do=settings';
    sendformdata(formfields,'','');
}
function showprogress () {
    let visbox = document.getElementById('barcontent');
    visbox.style.display='block';
}
function hideprogress () {
    let visbox = document.getElementById('barcontent');
    visbox.style.display='none';
}

function upldownl (flds,whichSide) {
    let url = '/site/form.cgi?' + flds;
    request = new XMLHttpRequest();
    try {
        //console.log('trying first - URL: ' + url);
       request.onreadystatechange = function() {
           if (request.readyState == 4) {
               let val = request.responseText;
               //console.log('Response 1: ' + val);
                //   document.getElementById('bcontent').innerHTML = val + ' first';
                //   document.getElementById('tempbox').classList.remove('nobox');
                //   document.getElementById('tempbox').classList.add('visbox');
           }
       }
       request.open("GET", url, true);
       request.send();
    }
    catch (e) {
       alert("Unable to connect to server:" + url);
    }
}

function progress (whichSide) {
    let oppSide;
    if(whichSide === 'lcl') {oppSide='remote';} else {oppSide='local';}
    //console.log('Running progress bar');
    showprogress();
    let width='0';
    let bar = document.getElementById('progbar');
    let barTitle = document.getElementById('notesprog');
    bar.style.width = width + '%';
    barTitle.innerHTML = width + '%';
    let sePar = ' __ ';
    let fTotal = '';
    let fDone = '';
    let fileName='';
    let intervId;
    setTimeout(requSite, 2000);

    function requSite () {
        if(!intervId) {
            //console.log('Started interval');
            intervId = setInterval(readActPage, 2000);
        }
    }
    function stopWork () {
        //console.log('Stopped interval');
        clearInterval(intervId);
        intervId=null;
    }
    function readActPage () {
            url = '/site/forep.cgi';
            req = new XMLHttpRequest();
            try {
                req.onreadystatechange = function() {
                    if (req.readyState == 4) {
                        let doPrint='';
                        var val = req.responseText;
                        //console.log('Response 2: ' + val);
                        if(val === 'No data') {
                            //console.log('Stopped by No Data');
                            clearInterval(intervId);
                            intervId=null;
                            doPrint=1;
                            unselectall(whichSide);
                            refresh(oppSide);
                        }
                        if(val === 'Memcached Error') {
                            //console.log('Stopped by Memcached Error');
                            clearInterval(intervId);
                            intervId=null;
                            doPrint=1;
                        }
                        if(val.includes(sePar)) {
                            var array = val.split(sePar);
                            fTotal = array[0];
                            fDone = array[1];
                            fileName = array[2];
                            doPrint=1;
                        }
                        if(fTotal !== '' && fDone !== '') {
                            width = fDone / fTotal;
                            width *= 100;
                            width = Math.round(width);
                            bar.style.width = width + '%';
                            barTitle.innerHTML = width + '%  &nbsp; - &nbsp; ' + fileName + '';
                            //console.log('Writing width value: "' + width + '"');
                        }
                        if(doPrint === '') {
                            if(val !== 'Downloading') {
                                document.getElementById('bcontent').innerHTML = val;
                                document.getElementById('tempbox').classList.remove('nobox');
                                document.getElementById('tempbox').classList.add('visbox');
                            }
                        }
                    }
                }
                req.open("GET", url, true);
                req.send();
            }
            catch (e) {
                alert("Unable to connect to server:" + url);
            }
        //hideprogress();
        //unselectall(whichSide);
        }
}

function filesel(side) {
    let bxName='';
    if(side === 'lcl') {
        bxName='localall';
    } else {
        bxName='remoteall';
    }
    let ischkChecked=document.getElementsByName(bxName);
        if (ischkChecked['0'].checked) {
            ischkChecked['0'].checked=false;
            unselectall(side);
        } else {
            ischkChecked['0'].checked=true;
            selectall(side);
        }
}

function selectall(type){
    let [hdrId, codeIncl, naCode] = getsidedata(type);
    let ele=document.getElementsByName(type);
    for(let i=0; i<ele.length; i++) {
        if(ele[i].type=='checkbox') {
            if(ele[i].value !== '..|d') {
                ele[i].checked=true;
            }
        }
    }
    document.getElementById(hdrId).innerHTML = codeIncl;
}

function unselectall(type){
    let [hdrId, codeIncl, naCode] = getsidedata(type);
    let ele=document.getElementsByName(type);
    for(let i=0; i<ele.length; i++) {
        if(ele[i].type=='checkbox') {
            ele[i].checked=false;
        }
    }
    document.getElementById(hdrId).innerHTML = naCode;
}

function newfolderdo (type) {
    let fileName=document.getElementById('file').value;
    let formfields = 'do=foldercreate&side=' + type + '&file=' + encodeURIComponent(fileName);
    sendformdata(formfields,'','');
}
function newfolder (type) {
    let formfields = 'do=newfolder&side=' + type;
    sendformdata(formfields,'','');
}
function trashit (type) {
    let fileName=document.getElementById('file').value;
    let formfields = 'do=trashdo&side=' + type + '&file=' + encodeURIComponent(fileName);
    sendformdata(formfields,'dotrash',type);
    hidebox();
}
function trash (type) {
    create(type,'trash');
}
function changethatmode (type) {
    let newMode=document.getElementById('filemode').value;
    let oldMode=document.getElementById('oldmode').value;
    if(oldMode === newMode) {
        alert('File/Dir Mode has to be changed by this form');
    }
    let fileName=document.getElementById('filename').value;
    let reCurse = getValue(name);
    reCurse = "&recursive=" + encodeURIComponent(reCurse);
    hidebox();
    let formfields = 'do=changemode&side=' + type + '&file=' + encodeURIComponent(fileName) + '&om=' + encodeURIComponent(oldMode) + '&nm=' + encodeURIComponent(newMode) + reCurse;
    sendformdata(formfields,'','');
    //console.log(formfields);
}
function renamefile (type) {
    hidebox();
    let oldFile=document.getElementById('oldname').value;
    let newFile=document.getElementById('newname').value;
    let formfields = 'do=changename&side=' + type + '&oldfile=' + encodeURIComponent(oldFile) + '&newfile=' + newFile;
    sendformdata(formfields,'dotrash',type);
}
function rename (type) {
    create(type,'rename');
}

function info (type) {
    create(type,'info');
}
function view (type) {
    create(type,'view');
}

function create (type,doing) {
    let doIt='';
    if(doing === 'view') {doIt='View';}
    if(doing === 'info') {doIt='Get Information';}
    if(doing === 'rename') {doIt='Rename';}
    let name='';
    if(type === 'local') {
        name='lcl';
    } else {
        name='rmt';
    }
    let checked = getValue(name);
    let vspr=' __ ';
    if(checked.includes(vspr)) {
        let formfields = 'do=' + doing + '&side=' + type + '&file=' + encodeURIComponent(checked);
        //console.log('Fields: ' + formfields);
        sendformdata(formfields,'','');
    } else {
        alert('No file to ' + doIt + ' is selected');
    }
}

function upd () {
    let name = 'lcl';
    let checked = getValue(name);
    let vspr=' __ ';
    if(checked.includes(vspr)) {
        let formfields = 'do=upload&files=' + encodeURIComponent(checked);
        upldownl(formfields, name);
    } else {
        alert('No files selected to Upload');
    }
}

function dnl () {
    let name='rmt';
    let checked = getValue(name);
    let vspr=' __ ';
    if(checked.includes(vspr)) {
        let formfields = 'do=download&files=' + encodeURIComponent(checked);
        upldownl(formfields, name);
    } else {
        alert('No files selected to Download');
    }
}
function chdirs(drc, whToId) {
    let dirName = encodeURIComponent(document.getElementById(drc).value);
    let mnDir = encodeURIComponent(document.getElementById(whToId).innerHTML);
    //console.log('Dir: "' + dirName + '" Top ID: "' + whToId + '" Main Dir: "' + mnDir + '"');
    let formfields = 'do=changedir&dirname=' + dirName + '&mvfrom=' + mnDir + '&dirtp=' + whToId;
    sendformdata(formfields,'','');
}
function siteconnect() {
    //console.log('siteconnect');
    let nameOfSite = document.querySelector('[name="site"]');
    let site = encodeURIComponent(nameOfSite.value);
    //console.log('Value is: "' + site + '"');
    let formDataSend = 'do=setsite&sitename=' + site;
    sendformdata(formDataSend,'','');
}

function refresh (tp) {
    let formfields = 'do=refresh&which=' + tp + '';
    sendformdata(formfields,'','');
}

function hidebox() {
    document.getElementById('tempbox').classList.remove('visbox');
    document.getElementById('tempbox').classList.add('nobox');
    document.getElementById('barcontent').style.display='none';
}

function sendformdata (flds,isRefresh,rfrSide) {
     var url = '/site/form.cgi?' + flds;
    request = new XMLHttpRequest();
    try {
        request.onreadystatechange = function() {
            if (request.readyState == 4) {
                var val = request.responseText;
                //console.log('Response: ' + val);
                let sePar = ' --- ';
                let htmlcode = '';
                let idUpd = '';
                let tpCode = '';
                let toIds = '';
                let doPrint='';
                if(val.includes(sePar)) {
                    var array = val.split(sePar);
                    htmlcode = array[0];
                    idUpd = array[1];
                    tpCode = array[2];
                    toIds = array[3];
                    doPrint=1;
                }
                    //console.log('HTML: ' + htmlcode);
                    //console.log('Field: ' + idUpd);
                if(idUpd !== '' && htmlcode !== '') {
                    document.getElementById(idUpd).innerHTML = htmlcode;
                }
                if(tpCode !== '' && toIds !== '') {
                    document.getElementById(toIds).innerHTML = tpCode;
                }
                //document.getElementById(img).style.display="inline-block";
                if(doPrint === '') {
                    document.getElementById('bcontent').innerHTML = val;
                    document.getElementById('tempbox').classList.remove('nobox');
                    document.getElementById('tempbox').classList.add('visbox');
                }
                if(isRefresh === 'dotrash' && rfrSide !== '') {
                    refresh(rfrSide);
                }
            }
        }
        request.open("GET", url, true);
        request.send();
    }
    catch (e) {
        alert("Unable to connect to server:" + url);
    }
}

function getsidedata(sdact) {
    let hdrId='';
    let codeIncl='';
    let naCode='';
    if(sdact === 'lcl') {
        hdrId='locntr';
        codeIncl=`<a href="#" class="doitem" onclick="filesel('lcl');return false;"><i title="Local Computer" class="locahead fa fa-desktop"></i></a>
    <a href="#" class="doitem" onclick="upd(); progress('lcl');return false;"><i title="Upload" class="fa fa-upload"></i></a>
	<a href="#" class="doitem" onclick="refresh('local');return false;"><i title="Refresh" class="fa fa-refresh"></i></a>
	<a href="#" class="doitem" onclick="view('local');return false;"><i title="View" class="fa fa-eye"></i></a>
    <a href="#" class="doitem" onclick="info('local');return false;"><i title="Info" class="fa fa-info"></i></a>
    <a href="#" class="doitem" onclick="rename('local');return false;"><i title="Rename" class="fa fa-sliders"></i></a>
    <a href="#" onclick="trash('local');return false;"><i title="Delete" class="fa fa-trash-o"></i></a>
	<a href="#" title="Create New Folder" onclick="newfolder('local');return false;"><span class="fa-stack"><i class="fa fa-folder-o fa-stack-1x"></i><span class="fa fa-stack-1x letter">+</span></span></a>`;
        naCode = `<a href="#" class="doitem" onclick="filesel('lcl');return false;"><i title="Local Computer" class="locahead fa fa-desktop"></i></a>
    <i title="Upload" class="fa fa-upload doitem na"></i>
	<a href="#" class="doitem" onclick="refresh('local');return false;"><i title="Refresh" class="fa fa-refresh"></i></a>
	<i title="View" class="fa fa-eye doitem na"></i>
    <i title="Info" class="fa fa-info doitem na"></i>
	<i title="Rename" class="fa fa-sliders doitem na"></i>
	<i title="Delete" class="fa fa-trash-o na"></i>
    <a href="#" title="Create New Folder" onclick="newfolder('local');return false;"><span class="fa-stack"><i class="fa fa-folder-o fa-stack-1x"></i><span class="fa fa-stack-1x letter">+</span></span></a>`;
    } else {
        hdrId='remcntr';
        codeIncl=`<a href="#" class="doitem" onclick="filesel('rmt');return false;"><i title="Remote Server" class="locahead fa fa-server"></i></a>
    <a href="#" class="doitem" onclick="dnl(); progress('rmt');return false;"><i title="Download" class="fa fa-download"></i></a>
    <a href="#" class="doitem" onclick="refresh('remote');return false;"><i title="Refresh" class="fa fa-refresh"></i></a>
	<a href="#" class="doitem" onclick="view('remote');return false;"><i title="View" class="fa fa-eye"></i></a>
    <a href="#" class="doitem" onclick="info('remote');return false;"><i title="Info" class="fa fa-info"></i></a>
    <a href="#" class="doitem" onclick="rename('remote');return false;"><i title="Rename" class="fa fa-sliders"></i></a>
	<a href="#" onclick="trash('remote');return false;"><i title="Delete" class="fa fa-trash-o"></i></a>
	<a href="#" title="Create New Folder" class="doitem" onclick="newfolder('remote');return false;"><span class="fa-stack"><i class="fa fa-folder-o fa-stack-1x"></i><span class="fa fa-stack-1x letter">+</span></span></a>`;
        naCode = `<a href="#" class="doitem" onclick="filesel('rmt');return false;"><i title="Remote Server" class="locahead fa fa-server"></i></a>
    <i title="Download" class="fa fa-download doitem na"></i>
    <a href="#" class="doitem" onclick="refresh('remote');return false;"><i title="Refresh" class="fa fa-refresh"></i></a>
	<i title="View" class="fa fa-eye doitem na"></i>
    <i title="Info" class="fa fa-info doitem na"></i>
	<i title="Rename" class="fa fa-sliders doitem na"></i>
	<i title="Delete" class="fa fa-trash-o na"></i>
	<a href="#" title="Create New Folder" onclick="newfolder('remote');return false;"><span class="fa-stack doitem"><i class="fa fa-folder-o fa-stack-1x"></i><span class="fa fa-stack-1x letter">+</span></span></a>`;
    }
    return [hdrId, codeIncl, naCode];
}

function vr(clickedon, side) {
    let [hdrId, codeIncl, naCode] = getsidedata(side);

    let checked = getValue(side);
    //console.log('Result: ' + checked);
    let vspr=' __ ';
    if(checked.includes(vspr)) {
        document.getElementById(hdrId).innerHTML = codeIncl;
    } else {
        document.getElementById(hdrId).innerHTML = naCode;
    }
}

function getValue(nm) {
    //console.log('Getting value ' + nm);
    let checkboxes = document.getElementsByName(nm);
    //console.log('Checkboxes: ' + checkboxes);
    //let chblngth=checkboxes.length;
    //console.log('Number of checked: ' + chblngth);
    let result = "";
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            result += checkboxes[i].value + " __ ";
        }
    }
    return result;
}