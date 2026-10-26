<?php
/**
 * Portfolio Contact Form API
 * Saves submissions to messages/messages.json
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Only accept POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
    exit();
}

// Read form data (supports both form-encoded and JSON body)
$name    = '';
$email   = '';
$phone   = '';
$subject = '';
$message = '';

if (!empty($_POST)) {
    // Standard form submission (jQuery serialize)
    $name    = trim($_POST['name']    ?? '');
    $email   = trim($_POST['email']   ?? '');
    $phone   = trim($_POST['phone']   ?? '');
    $subject = trim($_POST['subject'] ?? '');
    $message = trim($_POST['message'] ?? '');
} else {
    // JSON body
    $input   = json_decode(file_get_contents('php://input'), true);
    $name    = trim($input['name']    ?? '');
    $email   = trim($input['email']   ?? '');
    $phone   = trim($input['phone']   ?? '');
    $subject = trim($input['subject'] ?? '');
    $message = trim($input['message'] ?? '');
}

// Sanitize
function clean($v) {
    return htmlspecialchars(strip_tags($v), ENT_QUOTES, 'UTF-8');
}

$name    = clean($name);
$email   = clean($email);
$phone   = clean($phone);
$subject = clean($subject);
$message = clean($message);

// Validate
if (empty($name) || empty($email) || empty($message)) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Please fill in all required fields.']);
    exit();
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Please enter a valid email address.']);
    exit();
}

// Path to messages file
$messagesFile = __DIR__ . '/messages/messages.json';
$messagesDir  = __DIR__ . '/messages';

// Create directory if needed
if (!is_dir($messagesDir)) {
    mkdir($messagesDir, 0755, true);
}

// Read existing messages
$data = ['messages' => []];
if (file_exists($messagesFile)) {
    $content = file_get_contents($messagesFile);
    $decoded = json_decode($content, true);
    if ($decoded) {
        $data = $decoded;
    }
}

// Build new message entry
$entry = [
    'id'      => uniqid('msg_', true),
    'date'    => date('Y-m-d H:i:s'),
    'name'    => $name,
    'email'   => $email,
    'phone'   => $phone ?: '—',
    'subject' => $subject ?: '(No subject)',
    'message' => $message,
    'read'    => false,
];

// Prepend (newest first)
array_unshift($data['messages'], $entry);

// Save to file
if (file_put_contents($messagesFile, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE))) {
    echo json_encode(['status' => 'success', 'message' => 'Message sent successfully.']);
} else {
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Could not save message. Check folder permissions.']);
}
