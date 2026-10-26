<?php
// messages/view.php — Portfolio Inbox Viewer
// Password-protected. The password lives in config.php, which is kept out of git.

$configFile = __DIR__ . '/config.php';
if (!file_exists($configFile)) {
    http_response_code(500);
    exit('Inbox is not configured: copy config.example.php to config.php and set a password.');
}
$password = (require $configFile)['password'];
$msgFile  = __DIR__ . '/messages.json';

session_start();

// ── Auth ──────────────────────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['pw'])) {
    if ($_POST['pw'] === $password) {
        $_SESSION['portfolio_inbox_auth'] = true;
    } else {
        $authError = 'Incorrect password. Try again.';
    }
}

if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: view.php');
    exit;
}

// Mark as read
if (isset($_GET['read']) && isset($_SESSION['portfolio_inbox_auth'])) {
    $messages = file_exists($msgFile) ? json_decode(file_get_contents($msgFile), true) : [];
    foreach ($messages as &$m) {
        if ($m['id'] === $_GET['read']) $m['read'] = true;
    }
    file_put_contents($msgFile, json_encode($messages, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    header('Location: view.php');
    exit;
}

// Delete message
if (isset($_GET['delete']) && isset($_SESSION['portfolio_inbox_auth'])) {
    $messages = file_exists($msgFile) ? json_decode(file_get_contents($msgFile), true) : [];
    $messages = array_filter($messages, fn($m) => $m['id'] !== $_GET['delete']);
    file_put_contents($msgFile, json_encode(array_values($messages), JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    header('Location: view.php');
    exit;
}

$authed   = isset($_SESSION['portfolio_inbox_auth']);
$messages = [];
$unread   = 0;

if ($authed && file_exists($msgFile)) {
    $data     = json_decode(file_get_contents($msgFile), true) ?? [];
    $messages = $data['messages'] ?? [];
    $unread   = count(array_filter($messages, fn($m) => !($m['read'] ?? false)));
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Portfolio Inbox<?= $authed && $unread ? " ({$unread} new)" : '' ?></title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0d0d14; --card: #13131f; --border: #1e1e2e;
    --purple: #6333ff; --purple-light: #a855f7;
    --text: #e2e8f0; --muted: #64748b; --white: #fff;
    --green: #22c55e; --red: #ef4444;
  }
  body { background: var(--bg); color: var(--text); font-family: 'Inter', system-ui, sans-serif; min-height: 100vh; }

  /* ── Login ── */
  .login-wrap {
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; padding: 20px;
  }
  .login-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 16px;
    padding: 48px 40px; width: 100%; max-width: 400px; text-align: center;
  }
  .login-card .icon { font-size: 40px; margin-bottom: 16px; }
  .login-card h1 { font-size: 22px; margin-bottom: 6px; }
  .login-card p { color: var(--muted); font-size: 14px; margin-bottom: 28px; }
  .login-card input[type=password] {
    width: 100%; padding: 12px 16px; border-radius: 8px;
    border: 1px solid var(--border); background: var(--bg);
    color: var(--text); font-size: 15px; margin-bottom: 14px; outline: none;
  }
  .login-card input:focus { border-color: var(--purple); }
  .login-card button {
    width: 100%; padding: 12px; border-radius: 8px;
    background: linear-gradient(135deg, var(--purple), var(--purple-light));
    color: #fff; border: none; font-size: 15px; font-weight: 600;
    cursor: pointer; transition: opacity .2s;
  }
  .login-card button:hover { opacity: .85; }
  .error-msg { color: var(--red); font-size: 13px; margin-bottom: 12px; }

  /* ── Header ── */
  .header {
    background: var(--card); border-bottom: 1px solid var(--border);
    padding: 18px 32px; display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 10;
  }
  .header h1 { font-size: 18px; display: flex; align-items: center; gap: 10px; }
  .badge {
    background: var(--purple); color: #fff; border-radius: 100px;
    font-size: 11px; font-weight: 700; padding: 2px 8px;
  }
  .header a {
    color: var(--muted); font-size: 13px; text-decoration: none;
    border: 1px solid var(--border); padding: 6px 14px; border-radius: 8px;
    transition: color .2s;
  }
  .header a:hover { color: var(--text); }

  /* ── Main ── */
  .main { max-width: 900px; margin: 0 auto; padding: 32px 20px; }
  .empty { text-align: center; padding: 80px 20px; color: var(--muted); }
  .empty .big { font-size: 48px; margin-bottom: 12px; }

  /* ── Message Card ── */
  .msg-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    margin-bottom: 16px; overflow: hidden; transition: border-color .2s;
  }
  .msg-card.unread { border-left: 3px solid var(--purple); }
  .msg-head {
    padding: 18px 22px; display: flex; align-items: flex-start;
    justify-content: space-between; gap: 16px; cursor: pointer;
  }
  .msg-head:hover { background: rgba(99,51,255,.04); }
  .msg-meta { flex: 1; min-width: 0; }
  .msg-name {
    font-weight: 600; font-size: 15px;
    display: flex; align-items: center; gap: 8px; margin-bottom: 4px;
  }
  .unread-dot {
    width: 8px; height: 8px; background: var(--purple);
    border-radius: 50%; flex-shrink: 0;
  }
  .msg-subject { color: var(--muted); font-size: 13px; }
  .msg-date { color: var(--muted); font-size: 12px; white-space: nowrap; }
  .msg-actions { display: flex; gap: 8px; align-items: center; }
  .btn-sm {
    padding: 5px 12px; border-radius: 6px; font-size: 12px;
    font-weight: 500; cursor: pointer; border: 1px solid var(--border);
    text-decoration: none; transition: all .2s; color: var(--muted);
    background: transparent; display: inline-block;
  }
  .btn-sm:hover { color: var(--text); border-color: var(--muted); }
  .btn-delete { color: var(--red); border-color: rgba(239,68,68,.3); }
  .btn-delete:hover { background: rgba(239,68,68,.1); color: var(--red); }

  /* ── Message Body (toggle) ── */
  .msg-body { display: none; border-top: 1px solid var(--border); padding: 22px; }
  .msg-body.open { display: block; }
  .msg-fields { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 24px; margin-bottom: 20px; }
  .field-row label { display: block; font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 4px; }
  .field-row span { font-size: 14px; color: var(--text); }
  .field-row a { color: var(--purple-light); text-decoration: none; }
  .msg-text {
    background: var(--bg); border-radius: 8px; padding: 16px;
    font-size: 14px; line-height: 1.75; color: var(--text);
    white-space: pre-wrap; border: 1px solid var(--border);
  }
  .toggle-icon { transition: transform .3s; display: inline-block; color: var(--muted); }
  .toggle-icon.open { transform: rotate(180deg); }
</style>
</head>
<body>

<?php if (!$authed): ?>
<!-- ── Login Screen ── -->
<div class="login-wrap">
  <div class="login-card">
    <div class="icon">📬</div>
    <h1>Portfolio Inbox</h1>
    <p>Enter your password to view messages</p>
    <?php if (isset($authError)): ?>
      <div class="error-msg"><?= htmlspecialchars($authError) ?></div>
    <?php endif; ?>
    <form method="POST">
      <input type="password" name="pw" placeholder="Password" autofocus>
      <button type="submit">View Messages</button>
    </form>
  </div>
</div>

<?php else: ?>
<!-- ── Inbox ── -->
<div class="header">
  <h1>
    📬 Portfolio Inbox
    <?php if ($unread > 0): ?>
      <span class="badge"><?= $unread ?> new</span>
    <?php endif; ?>
  </h1>
  <a href="?logout=1">Logout</a>
</div>

<div class="main">
  <?php if (empty($messages)): ?>
    <div class="empty">
      <div class="big">✉️</div>
      <p>No messages yet. Your inbox is empty.</p>
    </div>
  <?php else: ?>
    <p style="color:var(--muted);font-size:13px;margin-bottom:20px;"><?= count($messages) ?> message<?= count($messages) !== 1 ? 's' : '' ?> total</p>

    <?php foreach ($messages as $m):
      $isUnread = !($m['read'] ?? false);
      $id = htmlspecialchars($m['id']);
    ?>
    <div class="msg-card <?= $isUnread ? 'unread' : '' ?>" id="card-<?= $id ?>">
      <div class="msg-head" onclick="toggleMsg('<?= $id ?>')">
        <div class="msg-meta">
          <div class="msg-name">
            <?php if ($isUnread): ?><span class="unread-dot"></span><?php endif; ?>
            <?= htmlspecialchars($m['name']) ?>
            <span style="color:var(--muted);font-weight:400;font-size:13px;">&lt;<?= htmlspecialchars($m['email']) ?>&gt;</span>
          </div>
          <div class="msg-subject"><?= htmlspecialchars($m['subject']) ?></div>
        </div>
        <div style="display:flex;align-items:center;gap:12px;">
          <div class="msg-date"><?= htmlspecialchars($m['date']) ?></div>
          <span class="toggle-icon" id="icon-<?= $id ?>">▼</span>
        </div>
      </div>
      <div class="msg-body" id="body-<?= $id ?>">
        <div class="msg-fields">
          <div class="field-row">
            <label>Name</label>
            <span><?= htmlspecialchars($m['name']) ?></span>
          </div>
          <div class="field-row">
            <label>Email</label>
            <span><a href="mailto:<?= htmlspecialchars($m['email']) ?>"><?= htmlspecialchars($m['email']) ?></a></span>
          </div>
          <div class="field-row">
            <label>Phone</label>
            <span><?= htmlspecialchars($m['phone'] ?? '—') ?></span>
          </div>
          <div class="field-row">
            <label>Subject</label>
            <span><?= htmlspecialchars($m['subject']) ?></span>
          </div>
          <div class="field-row">
            <label>Date</label>
            <span><?= htmlspecialchars($m['date']) ?></span>
          </div>
        </div>
        <div class="msg-text"><?= htmlspecialchars($m['message']) ?></div>
        <div class="msg-actions" style="margin-top:14px;">
          <?php if ($isUnread): ?>
            <a href="?read=<?= $id ?>" class="btn-sm">✓ Mark as read</a>
          <?php endif; ?>
          <a href="mailto:<?= htmlspecialchars($m['email']) ?>?subject=Re: <?= htmlspecialchars($m['subject']) ?>" class="btn-sm">↩ Reply</a>
          <a href="?delete=<?= $id ?>" class="btn-sm btn-delete" onclick="return confirm('Delete this message?')">🗑 Delete</a>
        </div>
      </div>
    </div>
    <?php endforeach; ?>
  <?php endif; ?>
</div>

<script>
function toggleMsg(id) {
    var body = document.getElementById('body-' + id);
    var icon = document.getElementById('icon-' + id);
    var isOpen = body.classList.toggle('open');
    icon.classList.toggle('open', isOpen);
    // Auto-mark as read when opened
    if (isOpen) {
        var card = document.getElementById('card-' + id);
        if (card.classList.contains('unread')) {
            fetch('?read=' + id);
            card.classList.remove('unread');
            var dot = card.querySelector('.unread-dot');
            if (dot) dot.remove();
        }
    }
}
</script>

<?php endif; ?>
</body>
</html>
