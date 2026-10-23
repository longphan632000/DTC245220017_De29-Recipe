#!/usr/bin/env python3
"""Sao lưu MySQL vào file gzip cục bộ có quyền 0600."""
from pathlib import Path
import datetime,gzip,os,subprocess
root=Path(__file__).resolve().parents[1]
folder=root/'runtime/backups';folder.mkdir(parents=True,mode=0o700,exist_ok=True)
target=folder/('recipe-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.sql.gz')
p=subprocess.run(['docker','compose','exec','-T','db','sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump --default-character-set=utf8mb4 -uroot --single-transaction --no-tablespaces "$MYSQL_DATABASE"'],cwd=root,capture_output=True,check=True)
fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'wb') as f:
    with gzip.GzipFile(fileobj=f,mode='wb') as out:out.write(p.stdout)
print(target)
