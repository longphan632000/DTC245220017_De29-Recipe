<?php
declare(strict_types=1);
date_default_timezone_set('Asia/Ho_Chi_Minh');
session_start();
function e(mixed $value): string { return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function db(): PDO {
    static $pdo;
    if (!$pdo) {
        $pdo = new PDO('mysql:host=' . getenv('DB_HOST') . ';dbname=' . getenv('DB_NAME') . ';charset=utf8mb4', getenv('DB_USER'), getenv('DB_PASSWORD'), [PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC, PDO::ATTR_EMULATE_PREPARES=>false]);
    }
    return $pdo;
}
function audit(string $event, array $context = []): void {
    error_log(json_encode(['event'=>$event, 'time'=>date(DATE_ATOM)] + $context, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));
}
function csrf(): string { return $_SESSION['csrf'] ??= bin2hex(random_bytes(32)); }
function csrf_field(): void { echo '<input type="hidden" name="csrf" value="'.e(csrf()).'">'; }
function verify_csrf(): void {
    if (!is_string($_POST['csrf'] ?? null) || !hash_equals(csrf(), $_POST['csrf'])) {
        http_response_code(403); audit('csrf_rejected'); exit('Yêu cầu không hợp lệ. Hãy tải lại trang và thử lại.');
    }
}
function admin_required(): void {
    if (empty($_SESSION['user_id'])) { header('Location: /?page=login'); exit; }
}
function redirect(string $url): never { header('Location: '.$url); exit; }
function categories(): array { return db()->query('SELECT * FROM categories ORDER BY id')->fetchAll(); }
function recipe(int $id): array|false {
    $s=db()->prepare('SELECT r.*,c.name category FROM recipes r JOIN categories c ON c.id=r.category_id WHERE r.id=? AND r.is_deleted=0'); $s->execute([$id]); return $s->fetch();
}
function items(string $table, int $id): array {
    if (!in_array($table,['ingredients','steps'],true)) throw new LogicException('Invalid table');
    $s=db()->prepare('SELECT * FROM '.$table.' WHERE recipe_id=? ORDER BY position,id');$s->execute([$id]);return $s->fetchAll();
}
function image_for(string $key): string {
    return '/assets/'.(in_array($key,['pho','banh-mi','com-rang','canh-chua','salad','che'],true)?$key:'pho').'.svg';
}
set_exception_handler(function(Throwable $error): void {
    audit('application_error',['type'=>get_class($error)]);
    http_response_code(500);
    echo '<h1>Hệ thống đang bận</h1><p>Vui lòng thử lại sau.</p>';
});
