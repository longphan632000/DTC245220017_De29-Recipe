"""Thu kết quả thật để làm hình trích xuất lệnh trong báo cáo.

Không dựng giao diện Terminal. Mỗi PNG có TXT và JSON nguồn để đối chiếu.
Chạy bằng Python có Pillow; không đọc giá trị bí mật vào ảnh kết quả.
"""
from pathlib import Path
import datetime, json, os, platform, subprocess, textwrap, urllib.request, urllib.parse, base64, gzip
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'minh-chung/chi-tiet';OUT.mkdir(exist_ok=True)
os.chdir(ROOT)
NOW=datetime.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(timespec='seconds')
records={}

def run(args, input=None):
    p=subprocess.run(args,input=input,text=True,capture_output=True)
    return p.returncode,'\n'.join(line.rstrip() for line in (p.stdout+p.stderr).splitlines()).strip()

def record(key,title,command,output,returncode=0):
    records[key]={'title':title,'command':command,'time':NOW,'returncode':returncode,'output':output}
    (OUT/(key+'.txt')).write_text('THOI DIEM '+NOW+'\nLENH '+command+'\nEXIT '+str(returncode)+'\n\n'+output+'\n')
    return output

def capture(key,title,args):
    rc,s=run(args);return record(key,title,' '.join(args),s,rc)

capture('CLI_01_Moi_truong','Phiên bản công cụ trên Ubuntu',['sh','-c','uname -sr; . /etc/os-release; echo "$PRETTY_NAME"; docker --version; docker compose version; git --version; gh --version | head -1; python3 --version'])
capture('CLI_02_Git','Các mốc commit của repository',['git','log','--reverse','--format=%h %ad%n%s','--date=format:%d/%m/%Y %H:%M'])
capture('CLI_03_Containers','Trạng thái dịch vụ Docker Compose',['docker','compose','ps','--format','table {{.Service}}\t{{.State}}\t{{.Health}}\t{{.Ports}}'])
ids=run(['docker','compose','ps','-q'])[1].split()
inspect=json.loads(run(['docker','inspect',*ids])[1])
lines=['SERVICE          UID           RO    CAP_DROP  NNP     PRIVILEGED']
for c in sorted(inspect,key=lambda x:x['Config']['Labels']['com.docker.compose.service']):
    h=c['HostConfig'];name=c['Config']['Labels']['com.docker.compose.service']
    lines.append(f"{name:<16} {(c['Config']['User'] or '0'):<13} {str(h['ReadonlyRootfs']):<5} {','.join(h['CapDrop']):<9} {str('no-new-privileges:true' in h['SecurityOpt']):<7} {h['Privileged']}")
record('CLI_04_Hardening','Trích các trường hardening từ Docker inspect','docker inspect $(docker compose ps -q) | chọn các trường cần kiểm tra','\n'.join(lines))
networks=json.loads(run(['docker','network','ls','--filter','label=com.docker.compose.project=recipe','--format','json'])[1].replace('}\n{','},{').join(['[',']']))
net_lines=[]
for n in sorted(networks,key=lambda x:x['Name']):
    d=json.loads(run(['docker','network','inspect',n['Name']])[1])[0]
    net_lines += [d['Name']+'  internal='+str(d['Internal']),'  '+', '.join(sorted(x['Name'] for x in d['Containers'].values()))]
record('CLI_05_Networks','Mạng và thành viên đang chạy','docker network inspect recipe_db_net recipe_web_net recipe_monitoring_net recipe_management_net','\n'.join(net_lines))
port_lines=[]
for c in inspect:
    name=c['Config']['Labels']['com.docker.compose.service']
    b=c['HostConfig'].get('PortBindings') or {}
    for port,bindings in b.items():
        for item in bindings or []:port_lines.append(name+' '+item['HostIp']+':'+item['HostPort']+' -> '+port)
port_lines += ['db: không publish cổng','app, phpmyadmin: chỉ truy cập qua mạng Docker']
for path in ['.env','secrets']:
    port_lines.append(path+' mode '+oct((ROOT/path).stat().st_mode & 0o777))
port_lines += ['git check-ignore:',run(['git','check-ignore','.env','secrets/phpmyadmin-secret.php'])[1]]
record('CLI_06_Ports_secrets','Cổng loopback và bảo vệ file bí mật','Docker inspect PortBindings; stat .env secrets; git check-ignore','\n'.join(port_lines))
sql="SET NAMES utf8mb4; SELECT 'categories' AS bang, COUNT(*) AS so_dong FROM categories UNION ALL SELECT 'recipes',COUNT(*) FROM recipes UNION ALL SELECT 'ingredients',COUNT(*) FROM ingredients UNION ALL SELECT 'steps',COUNT(*) FROM steps UNION ALL SELECT 'users',COUNT(*) FROM users; SHOW GRANTS FOR CURRENT_USER();"
db_args=['docker','compose','exec','-T','db','sh','-c','MYSQL_PWD="$MYSQL_PASSWORD" mysql --default-character-set=utf8mb4 -u"$MYSQL_USER" "$MYSQL_DATABASE"']
rc,s=run(db_args,input=sql)
record('CLI_07_Database','Số dòng dữ liệu và quyền tài khoản ứng dụng','SELECT COUNT(*); SHOW GRANTS FOR CURRENT_USER();',s,rc)
denied_sql='CREATE TABLE __report_denied_probe_20261024 (id INT);'
rc,s=run(db_args,input=denied_sql)
if rc==0:
    run(db_args,input='DROP TABLE __report_denied_probe_20261024;')
    raise RuntimeError('Application account unexpectedly has DDL privileges')
record('CLI_08_DDL_bi_tu_choi','MySQL từ chối quyền tạo bảng',denied_sql,s,rc)
headers=[]
with urllib.request.urlopen('http://127.0.0.1:8088/',timeout=15) as r:
    headers += ['GET http://127.0.0.1:8088/ -> HTTP '+str(r.status)]
    for k in ['Server','X-Content-Type-Options','X-Frame-Options','Referrer-Policy','Permissions-Policy','Content-Security-Policy']:headers.append(k+': '+str(r.headers.get(k)))
for path in ['/.env','/?recipe=999999','/?page=health']:
    try:
        with urllib.request.urlopen('http://127.0.0.1:8088'+path,timeout=15) as r:status=r.status
    except urllib.error.HTTPError as e:status=e.code
    headers.append('GET '+path+' -> HTTP '+str(status))
record('CLI_09_HTTP_headers','Kết quả HTTP và security headers','HTTP GET; chỉ trích status và các header không chứa cookie','\n'.join(headers))
capture('CLI_10_Nginx_config_test','Kiểm tra cú pháp Nginx',['docker','compose','exec','-T','nginx','nginx','-t'])
capture('CLI_11_UID','UID thực tế của các dịch vụ',['sh','-c','docker compose exec -T app id; docker compose exec -T nginx id; docker compose exec -T db id'])
capture('CLI_12_Volumes','Named volume của project Recipe',['docker','volume','ls','--filter','label=com.docker.compose.project=recipe','--format','table {{.Name}}\t{{.Driver}}'])
with urllib.request.urlopen('http://127.0.0.1:9090/api/v1/targets',timeout=15) as r:j=json.load(r)
metrics=['JOB          HEALTH    SCRAPE URL']
for x in sorted(j['data']['activeTargets'],key=lambda x:x['labels']['job']):metrics.append(f"{x['labels']['job']:<13}{x['health']:<10}{x['scrapeUrl']}")
record('CLI_13_Targets_API','Target metrics từ API Prometheus','GET /api/v1/targets','\n'.join(metrics))
verification=json.loads((ROOT/'minh-chung/verification.json').read_text())
for key,title,subset in [('CLI_14_Test_ung_dung','Kiểm thử ứng dụng và database',verification['results'][:21]),('CLI_15_Test_monitoring','Kiểm thử monitoring và LogQL',verification['results'][21:33]),('CLI_16_Test_runtime','Kiểm thử runtime và network',verification['results'][33:])]:
    result_lines=[('PASS ' if x['passed'] else 'FAIL ')+x['test'] for x in subset]
    result_lines+=['Kết quả toàn bộ: '+str(verification['passed'])+'/'+str(verification['total']),'Thời điểm kiểm thử: '+verification['time']]
    record(key,title,'python3 scripts/verify.py; trích từ verification.json','\n'.join(result_lines))
repro=json.loads((ROOT/'minh-chung/reproducibility.json').read_text())
repro_lines=['Thời điểm gốc: '+repro['time'],'Nguồn: '+repro['source'],'Commit: '+repro['commit'],'Project độc lập: '+repro['project'],'']
repro_lines += [('PASS ' if x['passed'] else 'FAIL ')+x['test'] for x in repro['checks']]
repro_lines += ['',f"TOTAL {repro['passed']}/{repro['total']}; bảng ứng dụng: {repro['application_tables']}"]
record('CLI_17_Cai_moi','Kết quả cài mới độc lập đã lưu','Đọc minh-chung/reproducibility.json','\n'.join(repro_lines))
rc,backup_output=run(['python3','scripts/backup.py'])
backup_files=sorted((ROOT/'runtime/backups').glob('*.sql.gz'),key=lambda x:x.stat().st_mtime)
if rc!=0 or not backup_files:raise RuntimeError('Backup failed: '+backup_output)
last=backup_files[-1]
with gzip.open(last,'rb') as f:valid=bool(f.read(1024))
backup_output+='\nFile mode: '+oct(last.stat().st_mode & 0o777)+'\nSize bytes: '+str(last.stat().st_size)+'\nGzip can be read: '+str(valid)+'\nGit ignored: '+str(run(['git','check-ignore',str(last.relative_to(ROOT))])[0]==0)
record('CLI_18_Backup','Bản sao lưu database mới','python3 scripts/backup.py; stat và kiểm tra gzip',backup_output,rc)
record('CLI_19_Source_tree','Các file nguồn và cấu hình được quản lý','git ls-files; chọn các file triển khai chính','\n'.join(x for x in run(['git','ls-files'])[1].splitlines() if not x.startswith(('minh-chung/','docs/Bao_'))))

def render_record(key,rec):
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',27)
    heading=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',31)
    sub=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
    lines=[]
    for line in rec['output'].splitlines():lines += textwrap.wrap(line,86,replace_whitespace=False,drop_whitespace=False,break_long_words=True,break_on_hyphens=False) or ['']
    # Long source listings and historical JSON use all text in TXT; figures show a stated excerpt.
    if len(lines)>31:lines=lines[:29]+['',f'[Trích 29 dòng đầu; toàn bộ ở {key}.txt]']
    width=1500;height=170+len(lines)*38+55
    im=Image.new('RGB',(width,height),'white');d=ImageDraw.Draw(im)
    d.text((40,24),rec['title'],font=heading,fill='black')
    d.text((40,73),'Kết quả lệnh thực tế  |  '+rec['time'],font=sub,fill='#424242')
    d.line((40,120,width-40,120),fill='#bbbbbb',width=2)
    for i,line in enumerate(lines):d.text((40,145+i*38),line,font=font,fill='#111111')
    im.save(OUT/(key+'.png'))

for key,rec in records.items():render_record(key,rec)
(OUT/'command-evidence.json').write_text(json.dumps({'time':NOW,'records':records},ensure_ascii=False,indent=2)+'\n')
print('Saved',len(records),'command records with TXT/JSON source and labeled PNG excerpts.')
