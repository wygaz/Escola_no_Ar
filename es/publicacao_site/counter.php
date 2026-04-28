<?php
$id = isset($_GET['id']) ? preg_replace('/[^A-Za-z0-9_\-]/', '', $_GET['id']) : 'page';
$storePath = __DIR__ . DIRECTORY_SEPARATOR . 'visit_counter.json';
$data = array(
  'total' => 0,
  'pages' => array()
);

if (file_exists($storePath)) {
  $raw = file_get_contents($storePath);
  $decoded = json_decode($raw, true);
  if (is_array($decoded)) {
    $data = array_merge($data, $decoded);
    if (!isset($data['pages']) || !is_array($data['pages'])) {
      $data['pages'] = array();
    }
  }
}

$data['total'] = isset($data['total']) ? intval($data['total']) + 1 : 1;
if (!isset($data['pages'][$id])) {
  $data['pages'][$id] = 0;
}
$data['pages'][$id] = intval($data['pages'][$id]) + 1;

$fp = fopen($storePath, 'c+');
if ($fp) {
  flock($fp, LOCK_EX);
  ftruncate($fp, 0);
  rewind($fp);
  fwrite($fp, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
  fflush($fp);
  flock($fp, LOCK_UN);
  fclose($fp);
}

$pageCount = intval($data['pages'][$id]);
$totalCount = intval($data['total']);
$svg = '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="72" viewBox="0 0 320 72" role="img" aria-label="Contador de visitas">' .
       '<rect x="0" y="0" width="320" height="72" rx="14" fill="#f6fbff" stroke="#d9e1e8"/>' .
       '<text x="18" y="24" font-family="Segoe UI,Arial,sans-serif" font-size="13" font-weight="700" fill="#175f8f">Visitas desta pÃ¡gina</text>' .
       '<text x="18" y="49" font-family="Segoe UI,Arial,sans-serif" font-size="28" font-weight="700" fill="#17212b">' . $pageCount . '</text>' .
       '<text x="92" y="49" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="#5c6a75">Total geral: ' . $totalCount . '</text>' .
       '</svg>';

header('Content-Type: image/svg+xml; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
echo $svg;