#!/usr/bin/env python3
"""Khởi tạo bí mật cục bộ, schema và toàn bộ stack Docker Compose."""
from pathlib import Path
import json, os, re, secrets, subprocess

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

def env_values():
    values = {}
    if (ROOT/'.env').exists():
        for line in (ROOT/'.env').read_text().splitlines():
            if '=' not in line or line.lstrip().startswith('#'):
                continue
            key, value = line.split('=', 1)
            try: value = json.loads(value)
            except json.JSONDecodeError: value = value.strip().strip("'\"")
            values[key.strip()] = str(value)
    return values

def run(args, **kwargs):
    return subprocess.run(['docker', 'compose', *args], check=True, **kwargs)

def main():
    vals = env_values()
    defaults = {
        'MYSQL_ROOT_PASSWORD': secrets.token_urlsafe(24), 'MYSQL_DATABASE': 'recipe_db',
        'MYSQL_USER': 'recipe_user', 'MYSQL_PASSWORD': secrets.token_urlsafe(24),
        'MYSQL_EXPORTER_PASSWORD': secrets.token_urlsafe(24),
        'PMA_BLOWFISH_SECRET': secrets.token_hex(16),
        'APP_ADMIN_USER': vals.get('WP_ADMIN_USER','recipe_admin'),
        'APP_ADMIN_PASSWORD': vals.get('WP_ADMIN_PASSWORD',secrets.token_urlsafe(24)),
        'GRAFANA_ADMIN_USER': 'recipe_admin', 'GRAFANA_ADMIN_PASSWORD': secrets.token_urlsafe(24),
        'APP_URL': 'http://127.0.0.1:'+os.environ.get('APP_HTTP_PORT','8088'),
    }
    changed = not (ROOT/'.env').exists()
    for key, value in defaults.items():
        if key not in vals:
            vals[key] = value; changed = True
    if changed:
        fd = os.open(ROOT/'.env', os.O_WRONLY|os.O_CREAT|os.O_TRUNC, 0o600)
        with os.fdopen(fd,'w') as f:
            for k,v in vals.items(): f.write(k+'='+json.dumps(v,ensure_ascii=False)+'\n')
    os.chmod(ROOT/'.env', 0o600)
    secret_dir=ROOT/'secrets'
    secret_dir.mkdir(mode=0o700,exist_ok=True)
    os.chmod(secret_dir,0o700)
    if not re.fullmatch(r'[A-Za-z0-9_-]{32,64}',vals['PMA_BLOWFISH_SECRET']):
        raise SystemExit('PMA_BLOWFISH_SECRET must contain 32–64 safe characters')
    secret_file=secret_dir/'phpmyadmin-secret.php'
    if secret_file.exists():os.chmod(secret_file,0o600)
    secret_file.write_text("<?php\n$cfg['blowfish_secret'] = '"+vals['PMA_BLOWFISH_SECRET']+"';\n")
    os.chmod(secret_file,0o444)
    for key in ['MYSQL_DATABASE','MYSQL_USER']:
        if not re.fullmatch(r'[A-Za-z0-9_]+',vals[key]): raise SystemExit('Invalid database identifier')
    for key in ['MYSQL_ROOT_PASSWORD','MYSQL_PASSWORD','MYSQL_EXPORTER_PASSWORD','APP_ADMIN_PASSWORD','GRAFANA_ADMIN_PASSWORD']:
        if len(vals[key]) < 20 or 'generate_' in vals[key]:
            raise SystemExit(key+': cần mật khẩu riêng ít nhất 20 ký tự; không dùng giá trị mẫu.')
    run(['config','--quiet'])
    run(['build'])
    run(['up','-d','--wait','--wait-timeout','180','db'])
    run(['exec','-T','db','sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot "$MYSQL_DATABASE"'],input=(ROOT/'mysql/init.sql').read_text(),text=True)
    def quote(s): return "'"+s.replace('\\','\\\\').replace("'","''")+"'"
    user=quote(vals['MYSQL_USER'])+"@'%'";database=vals['MYSQL_DATABASE']
    sql = f"REVOKE ALL PRIVILEGES, GRANT OPTION FROM {user};\nGRANT SELECT, INSERT, UPDATE, DELETE ON `{database}`.* TO {user};\n"
    sql += "CREATE USER IF NOT EXISTS 'recipe_exporter'@'%' IDENTIFIED BY "+quote(vals['MYSQL_EXPORTER_PASSWORD'])+" WITH MAX_USER_CONNECTIONS 3;\n"
    sql += "ALTER USER 'recipe_exporter'@'%' IDENTIFIED BY "+quote(vals['MYSQL_EXPORTER_PASSWORD'])+" WITH MAX_USER_CONNECTIONS 3;\n"
    sql += "GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'recipe_exporter'@'%';\n"
    run(['exec','-T','db','sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot'],input=sql,text=True)
    run(['up','-d','--wait','--wait-timeout','180'])
    php = r'''$d=json_decode(file_get_contents('php://stdin'),true);require '/var/www/html/bootstrap.php';
    $s=db()->prepare('INSERT INTO users(username,password_hash,role) VALUES(?,?,?) ON DUPLICATE KEY UPDATE username=username');
    $s->execute([$d['APP_ADMIN_USER'],password_hash($d['APP_ADMIN_PASSWORD'],PASSWORD_DEFAULT),'admin']);
    echo "Recipe administrator initialized.\n";'''
    run(['exec','-T','app','php','-r',php], input=json.dumps(vals),text=True)
    print('Website: '+vals['APP_URL'])
    print('Tài khoản Recipe và Grafana được lưu trong .env (quyền 0600).')

if __name__ == '__main__': main()
