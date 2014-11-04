<title>Croatian Meteor Network - Stream search</title>
<link rel="stylesheet" type="text/css" href="my.css">

<h1>Croatian Meteor Network - Stream search</h1>
<p>Easy stream search in the <a href="http://www.ta3.sk/IAUC22DB/MDC2007/index.php">IAU Meteor Center</a> Database. Leave the field empty to exclude it from filtering.</p>
<form>
<p>
<?php
  ini_set ("display_errors", "1");
  error_reporting(E_ALL);
 if (isset($_REQUEST["sol0"])) $sol0=$_REQUEST["sol0"]; else $sol0="";
 if (isset($_REQUEST["sol1"])) $sol1=$_REQUEST["sol1"]; else $sol1="";
 if (isset($_REQUEST["ra0"])) $ra0=$_REQUEST["ra0"]; else $ra0="";
 if (isset($_REQUEST["ra1"])) $ra1=$_REQUEST["ra1"]; else $ra1="";
 if (isset($_REQUEST["de0"])) $de0=$_REQUEST["de0"]; else $de0="";
 if (isset($_REQUEST["de1"])) $de1=$_REQUEST["de1"]; else $de1="";
 if (isset($_REQUEST["vg0"])) $vg0=$_REQUEST["vg0"]; else $vg0="";
 if (isset($_REQUEST["vg1"])) $vg1=$_REQUEST["vg1"]; else $vg1=""; 
 if (isset($_REQUEST["a0"])) $a0=$_REQUEST["a0"]; else $a0="";
 if (isset($_REQUEST["a1"])) $a1=$_REQUEST["a1"]; else $a1="";
 if (isset($_REQUEST["q0"])) $q0=$_REQUEST["q0"]; else $q0="";
 if (isset($_REQUEST["q1"])) $q1=$_REQUEST["q1"]; else $q1="";
 if (isset($_REQUEST["e0"])) $e0=$_REQUEST["e0"]; else $e0="";
 if (isset($_REQUEST["e1"])) $e1=$_REQUEST["e1"]; else $e1="";
 if (isset($_REQUEST["peri0"])) $peri0=$_REQUEST["peri0"]; else $peri0="";
 if (isset($_REQUEST["peri1"])) $peri1=$_REQUEST["peri1"]; else $peri1="";
 if (isset($_REQUEST["node0"])) $node0=$_REQUEST["node0"]; else $node0="";
 if (isset($_REQUEST["node1"])) $node1=$_REQUEST["node1"]; else $node1="";
 if (isset($_REQUEST["incl0"])) $incl0=$_REQUEST["incl0"]; else $incl0="";
 if (isset($_REQUEST["incl1"])) $incl1=$_REQUEST["incl1"]; else $incl1="";
 
 if (isset($_REQUEST["str"])) $str=$_REQUEST["str"]; else $str="";

 
 echo '<label>Sol. lng. min:</label> <input type="number" name="sol0" value='.$sol0.'>';
 echo '<label>max:</label> <input type="number" name="sol1" value='.$sol1.'><br />';
 echo '<label>R.A. min:</label> <input type="number" name="ra0" value='.$ra0.'>';
 echo '<label>max:</label> <input type="number" name="ra1" value='.$ra1.'><br />';
 echo '<label>Dec. min:</label> <input type="number" name="de0" value='.$de0.'>'; 
 echo '<label>max:</label> <input type="number" name="de1" value='.$de1.'><br />';
 echo '<label>Vg min:</label> <input type="number" name="vg0" value='.$vg0.'>'; 
 echo '<label>max:</label> <input type="number" name="vg1" value='.$vg1.'><br />';
 
 echo '<label>a min:</label> <input type="number" name="a0" value='.$a0.'>'; 
 echo '<label>max:</label> <input type="number" name="a1" value='.$a1.'><br />';
 echo '<label>q min:</label> <input type="number" name="q0" value='.$q0.'>'; 
 echo '<label>max:</label> <input type="number" name="q1" value='.$q1.'><br />'; 
 echo '<label>e min:</label> <input type="number" name="e0" value='.$e0.'>'; 
 echo '<label>max:</label> <input type="number" name="e1" value='.$e1.'><br />';
 echo '<label>Peri. min:</label> <input type="number" name="peri0" value='.$peri0.'>'; 
 echo '<label>max:</label> <input type="number" name="peri1" value='.$peri1.'><br />';
 echo '<label>Node min:</label> <input type="number" name="node0" value='.$node0.'>'; 
 echo '<label>max:</label> <input type="number" name="node1" value='.$node1.'><br />';
 echo '<label>Incl. min:</label> <input type="number" name="incl0" value='.$incl0.'>'; 
 echo '<label>max:</label> <input type="number" name="incl1" value='.$incl1.'><br />';
 
 echo '<label>Contains string:</label> <input type="text" name="str" value='.$str.'><br />';
 ?></p> 
 <p><input type="submit" value="Submit"></p>
</form>


<?php
    $url='http://www.ta3.sk/IAUC22DB/MDC2007/Etc/streamfulldata.csv';   
    $filename = 'streamworkingdata.csv';
    echo "<p>";    
    echo "Checking file... ";    
    if (file_exists($filename)) {
       $todays_date = date("Y-m-d"); 
       $filedate = date ("Y-m-d", filemtime($filename));
       if (strtotime($todays_date)>strtotime($filedate)) {
          if (copy($url, $filename)) {
            echo "copied $url to $filename.";
          } else {
            echo "failed to copy $url to $filename.";
          }
       } else {
         echo "local file is up to date.";
       }  
    } else {
      if (!copy($url, $filename)) {
        echo "failed to copy $filename.";
      } else {
        echo "copied $url to $filename.";     
      } 
    } 

    echo "<br />Applying filter... ";
    $lines = file($filename);
    $i=0;
    $filtered = array();

    foreach ($lines as $line_num => $line) {
      if (strpos($line,'"')===0){      
         $stream = explode('|',str_replace('"',"",$line));
         list($LP,$IAUNo,$AdNo,$Code,$shower_name,$activity,$s,$LaSun,$Ra,$De,$dRa,$dDe,$Vg,$a,$q,$e,$peri,$node,$incl,$N,$Group,$CG,$Parent_body,$Remarks,$Reference)=$stream;
         $ok = 1;

         // check sol lng
         if ($sol0<>"") {
           if (($sol0-$LaSun)>0) $ok = 0;
         }
         if ($sol1<>"") {
           if (($sol1-$LaSun)<0) $ok = 0;
         }


         // check RA
         if ($ra0<>"") {
           if (($ra0-$Ra)>0) $ok = 0;
         }
         if ($ra1<>"") {
           if (($ra1-$Ra)<0) $ok = 0;
         }

         // check Dec
         if ($de0<>"") {
           if (($de0-$De)>0) $ok = 0;
         }
         if ($de1<>"") {
           if (($de1-$De)<0) $ok = 0;
         }

         // check Vg
         if ($vg0<>"") {
           if (($vg0-$Vg)>0) $ok = 0;
         }
         if ($vg1<>"") {
           if (($vg1-$Vg)<0) $ok = 0;
         }

         // check a
         if ($a0<>"") {
           if (($a0-$a)>0) $ok = 0;
         }
         if ($a1<>"") {
           if (($a1-$a)<0) $ok = 0;
         }
         
         // check q
         if ($q0<>"") {
           if (($q0-$q)>0) $ok = 0;
         }
         if ($q1<>"") {
           if (($q1-$q)<0) $ok = 0;

         }
         // check e
         if ($e0<>"") {
           if (($e0-$e)>0) $ok = 0;
         }
         if ($e1<>"") {
           if (($e1-$e)<0) $ok = 0;
         }
         
         // check peri
         if ($peri0<>"") {
           if (($peri0-$peri)>0) $ok = 0;
         }
         if ($peri1<>"") {
           if (($peri1-$peri)<0) $ok = 0;
         }
         
         // check node
         if ($node0<>"") {
           if (($node0-$node)>0) $ok = 0;
         }
         if ($node1<>"") {
           if (($node1-$node)<0) $ok = 0;
         }
         
         // check incl
         if ($incl0<>"") {
           if (($incl0-$incl)>0) $ok = 0;
         }
         if ($incl1<>"") {
           if (($incl1-$incl)<0) $ok = 0;
         }
         
         // check str
         if ($str<>"") {
           if (!stripos($line,$str)) $ok = 0;
         }
         

         if ($ok==1) array_push($filtered, "<tr><td>".implode("</td><td>",$stream)."</td></tr>");
      }
    }

    echo "finished!";    
    echo "</p>";
    
    echo '<div class="fancyTable">';
    echo "<table>";
    echo "<thead><tr><th>".str_replace(';','</th><th>','LP;IAUNo;AdNo;Code;shower name;activity;s;LaSun;Ra;De;dRa;dDe;Vg;a;q;e;peri;node;inc;N;Group;CG;Parent body;Remarks;Reference')."</th></tr></thead><tbody>"; 
    foreach ($filtered as $i => $value) {
       echo $filtered[$i];
    }
    echo "</tbody></table></div>";
?>
<footer><p><author>Created by I. Skokic, May 17, 2013</author></p></footer>