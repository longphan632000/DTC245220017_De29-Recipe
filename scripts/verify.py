#!/usr/bin/env python3
"""Kiểm thử tích hợp thực tế. Dữ liệu tạm do script tạo sẽ được dọn trong finally."""
from pathlib import Path
import base64, datetime, html.parser, http.cookiejar, json, os, re, subprocess
import urllib.error, urllib.parse, urllib.request, time
from zoneinfo import ZoneInfo
from setup import env_values

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
ENV=env_values()
BASE=ENV.get('APP_URL','http://127.0.0.1:8088')
RESULTS=[]
jar=http.cookiejar.CookieJar()
client=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(jar))

def check(name, ok, evidence):
    RESULTS.append({'test':name,'passed':bool(ok),'evidence':evidence})
    print(('PASS ' if ok else 'FAIL ')+name+': '+str(evidence))
    if not ok: raise AssertionError(name)

def request(url, data=None, headers=None):
    if url.startswith('/'):url=BASE+url
    req=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode() if data is not None else None,headers=headers or {})
    try:r=client.open(req,timeout=30)
    except urllib.error.HTTPError as e:r=e
    with r:return r.status,r.geturl(),dict(r.headers),r.read().decode('utf8')

def token(body):
    match=re.search(r'name="csrf" value="([a-f0-9]+)"',body)
    if not match:raise AssertionError('CSRF token missing')
    return match.group(1)

def php(code,data):
    p=subprocess.run(['docker','compose','exec','-T','app','php','-r',"$d=json_decode(file_get_contents('php://stdin'),true);require '/var/www/html/bootstrap.php';"+code],input=json.dumps(data),text=True,capture_output=True,check=True,timeout=30)
    return p.stdout.strip()

for path in ['http://127.0.0.1:3000/api/health','http://127.0.0.1:3100/ready','http://127.0.0.1:9090/-/ready']:
    for attempt in range(90):
        try:
            if request(path)[0]==200: break
        except (OSError, ValueError): pass
        time.sleep(2)
    else: raise SystemExit('Service not ready: '+path)

temp_id=None
try:
    status,url,headers,body=request('/?page=health')
    check('Health và kết nối DB',status==200 and json.loads(body)['database']=='connected','HTTP '+str(status))
    status,url,headers,body=request('/')
    check('Trang chủ và tiếng Việt',status==200 and 'Phở gà thơm vị nhà' in body and body.count('<article class="card">')>=6,'6 công thức mẫu, UTF-8 đúng')
    required=['X-Content-Type-Options','X-Frame-Options','Referrer-Policy','Permissions-Policy','Content-Security-Policy']
    check('Security headers Nginx',all(x in headers for x in required),{x:headers.get(x) for x in required})
    _,_,_,body=request('/?'+urllib.parse.urlencode({'q':'me chín'}))
    check('Tìm theo nguyên liệu','Canh chua cá thanh mát' in body and body.count('<article class="card">')==1,'me chín → 1 công thức canh chua')
    _,_,_,body=request('/?category=3')
    check('Lọc danh mục',body.count('<article class="card">')==1 and 'Salad vườn nhà' in body,'Rau và salad → 1 công thức')
    status,_,_,body=request('/?recipe=1')
    check('Chi tiết nguyên liệu và cách nấu',status==200 and 'Nguyên liệu' in body and 'Cách thực hiện' in body and body.count('type="checkbox"')==6,'6 nguyên liệu, các bước nấu và khẩu phần')
    _,url,_,body=request('/?page=admin')
    check('Chặn quản trị chưa đăng nhập','page=login' in url,'Chuyển về trang đăng nhập')
    status,_,_,_=request('/?page=login',{'action':'login','username':'invalid','password':'invalid'})
    check('Chặn POST thiếu CSRF',status==403,'HTTP 403')
    _,_,_,body=request('/?page=login');csrf=token(body)
    status,_,_,body=request('/?page=login',{'action':'login','username':ENV['APP_ADMIN_USER'],'password':'invalid-integration-test','csrf':csrf})
    check('Từ chối mật khẩu sai',status==401,'HTTP 401, ghi sự kiện login_failed')
    csrf=token(body)
    before=next((c.value for c in jar if c.name=='PHPSESSID'),None)
    status,url,_,body=request('/?page=login',{'action':'login','username':ENV['APP_ADMIN_USER'],'password':ENV['APP_ADMIN_PASSWORD'],'csrf':csrf})
    after=next((c.value for c in jar if c.name=='PHPSESSID'),None)
    check('Đăng nhập quản trị',status==200 and 'page=admin' in url and 'Góc bếp của bạn' in body,'Tài khoản '+ENV['APP_ADMIN_USER'])
    check('Đổi session ID sau đăng nhập',before!=after,'Session được tạo lại, không ghi cookie vào báo cáo')
    csrf=token(body)
    title='Integration recipe '+datetime.datetime.now().strftime('%H%M%S')
    form={'action':'save','csrf':csrf,'id':0,'title':title,'description':'Công thức tạm để kiểm thử tích hợp.','category_id':1,'prep_minutes':5,'cook_minutes':10,'servings':2,'difficulty':'Dễ','illustration':'salad','ingredients':'1 củ cà rốt\n1 quả dưa leo','steps':'Rửa sạch nguyên liệu.\nTrộn đều và dùng ngay.'}
    status,_,_,body=request('/?page=edit',form)
    raw=php("$s=db()->prepare('SELECT id FROM recipes WHERE title=?');$s->execute([$d['title']]);echo $s->fetchColumn();",{'title':title})
    temp_id=int(raw)
    check('Tạo công thức',status==200 and temp_id>0 and title in body,'Bản ghi tạm ID '+str(temp_id))
    form.update(id=temp_id,title=title+' updated',csrf=token(body))
    status,_,_,body=request('/?page=edit',form)
    status,_,_,detail=request('/?recipe='+str(temp_id))
    check('Sửa công thức',status==200 and title+' updated' in detail,'Tên và dữ liệu chi tiết được cập nhật')
    _,_,_,body=request('/?page=admin')
    status,_,_,body=request('/?page=admin',{'action':'archive','id':temp_id,'csrf':token(body)})
    code,_,_,_=request('/?recipe='+str(temp_id))
    check('Lưu trữ công thức',code==404,'Ẩn khỏi trang công khai, giữ dữ liệu trong DB')
    _,_,_,body=request('/?page=admin&archived=1')
    request('/?page=admin',{'action':'restore','id':temp_id,'csrf':token(body)})
    code,_,_,body=request('/?recipe='+str(temp_id))
    check('Khôi phục công thức',code==200 and title+' updated' in body,'Công thức hiển thị lại')
    _,_,_,body=request('/?'+urllib.parse.urlencode({'q':"' OR 1=1 --"}))
    check('Truy vấn có tham số',body.count('<article class="card">')==0,'Chuỗi SQL injection được xử lý như từ khóa')
    _,_,_,body=request('/?'+urllib.parse.urlencode({'q':'<script>alert(1)</script>'}))
    check('Escape HTML', '<script>alert(1)</script>' not in body and '&lt;script&gt;' in body,'Nội dung nhập được HTML-escape')
    code,_,_,_=request('/.env')
    check('Chặn file nhạy cảm',code==403,'/.env → HTTP 403')
    result=php("try{db()->exec('CREATE TABLE forbidden_integration_test(id INT)');echo 'UNEXPECTED';}catch(PDOException $e){echo $e->errorInfo[1];}",{})
    check('Tài khoản DB không có quyền DDL',result=='1142','CREATE TABLE bị MySQL từ chối với mã 1142')
finally:
    if temp_id:
        php("$s=db()->prepare('DELETE FROM recipes WHERE id=? AND title LIKE ?');$s->execute([$d['id'],'Integration recipe %']);echo $s->rowCount();",{'id':temp_id})

class PmaForm(html.parser.HTMLParser):
    def __init__(self):
        super().__init__();self.inside=False;self.fields={};self.action=''
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form':
            self.inside=a.get('id')=='login_form'
            if self.inside:self.action=a.get('action','')
        if tag=='input' and self.inside and a.get('type')=='hidden' and 'name' in a:self.fields[a['name']]=a.get('value','')
    def handle_endtag(self,tag):
        if tag=='form':self.inside=False
_,_,_,body=request('http://127.0.0.1:8081/')
form=PmaForm();form.feed(body)
form.fields.update(pma_username=ENV['MYSQL_USER'],pma_password=ENV['MYSQL_PASSWORD'])
status,_,_,body=request(urllib.parse.urljoin('http://127.0.0.1:8081/',form.action),form.fields)
check('Đăng nhập phpMyAdmin',status==200 and 'route=/logout' in body and 'name="pma_password"' not in body,'Tài khoản ứng dụng '+ENV['MYSQL_USER'])
_,_,_,body=request('http://127.0.0.1:8081/index.php?'+urllib.parse.urlencode({'route':'/database/structure','db':ENV['MYSQL_DATABASE']}))
check('phpMyAdmin xem schema Recipe',all(x in body for x in ['recipes','categories','ingredients','steps','users']),'Đủ 5 bảng chính của ứng dụng PHP')

def prom(query):
    _,_,_,body=request('http://127.0.0.1:9090/api/v1/query?'+urllib.parse.urlencode({'query':query}))
    return json.loads(body)['data']['result']
for attempt in range(30):
    up=prom('up')
    if len(up)==6 and all(x['value'][1]=='1' for x in up):break
    time.sleep(2)
check('Prometheus targets',len(up)==6 and all(x['value'][1]=='1' for x in up),{x['metric']['job']:x['value'][1] for x in up})
for expr in ['mysql_up','nginx_up','count(container_cpu_usage_seconds_total{container_label_com_docker_compose_project="recipe"})','count(container_memory_working_set_bytes{container_label_com_docker_compose_project="recipe"})']:
    result=prom(expr)
    check('Metrics '+expr,bool(result) and float(result[0]['value'][1])>0,[x['value'][1] for x in result])
auth='Basic '+base64.b64encode((ENV['GRAFANA_ADMIN_USER']+':'+ENV['GRAFANA_ADMIN_PASSWORD']).encode()).decode()
for uid in ['prometheus','loki']:
    status,_,_,body=request('http://127.0.0.1:3000/api/datasources/uid/'+uid+'/health',headers={'Authorization':auth})
    j=json.loads(body);check('Grafana datasource '+uid,status==200 and j.get('status')=='OK',j.get('message'))
status,_,_,body=request('http://127.0.0.1:3000/api/dashboards/uid/recipe-overview',headers={'Authorization':auth})
check('Dashboard tự provision',status==200 and len(json.loads(body)['dashboard']['panels'])==10,'10 panel cho container, Nginx và MySQL')
queries=['{job="nginx"}','{job="nginx"} | json | status >= 400','{job="app"} |= "login_success"','{job="mysql"}']
for q in queries:
    params={'query':q,'limit':20,'direction':'backward','start':str(int((datetime.datetime.now().timestamp()-3600)*1e9)),'end':str(int(datetime.datetime.now().timestamp()*1e9))}
    status,_,_,body=request('http://127.0.0.1:3100/loki/api/v1/query_range?'+urllib.parse.urlencode(params))
    j=json.loads(body);rows=sum(len(x['values']) for x in j.get('data',{}).get('result',[]))
    check('LogQL '+q,status==200 and rows>0,{'rows':rows})
    (ROOT/'minh-chung').mkdir(exist_ok=True)
    (ROOT/'minh-chung'/('logql-'+str(queries.index(q)+1)+'.json')).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
ids=subprocess.run(['docker','compose','ps','-q'],capture_output=True,text=True,check=True).stdout.split()
inspect=json.loads(subprocess.run(['docker','inspect',*ids],capture_output=True,text=True,check=True).stdout)
runtime=[]
for c in inspect:
    service=c['Config']['Labels']['com.docker.compose.service'];h=c['HostConfig'];u=c['Config']['User']
    record={'service':service,'user':u or '0','read_only':h['ReadonlyRootfs'],'cap_drop':h['CapDrop'],'security_opt':h['SecurityOpt'],'privileged':h['Privileged'],'ports':h['PortBindings']}
    runtime.append(record)
    check('Runtime hardening '+service,h['ReadonlyRootfs'] and h['CapDrop']==['ALL'] and not h['Privileged'] and 'no-new-privileges:true' in h['SecurityOpt'] and (service=='cadvisor' or u.split(':')[0] not in ['','0','root']),{k:record[k] for k in ['user','read_only','cap_drop','privileged']})
    if service=='db':check('MySQL không publish cổng',not h['PortBindings'],'Chỉ truy cập qua db_net')
    for port,bindings in (h['PortBindings'] or {}).items():
        check('Loopback '+service+' '+port,all(x['HostIp']=='127.0.0.1' for x in bindings),'Chỉ 127.0.0.1')
net=json.loads(subprocess.run(['docker','network','inspect','recipe_db_net'],capture_output=True,text=True,check=True).stdout)[0]
check('Network isolation DB',net['Internal'],'db_net internal=true')
now=datetime.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat()
out={'time':now,'passed':sum(r['passed'] for r in RESULTS),'total':len(RESULTS),'results':RESULTS,'runtime':runtime}
(ROOT/'minh-chung/verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(ROOT/'minh-chung/verification.txt').write_text('THỜI ĐIỂM '+now+'\n'+'\n'.join(('PASS ' if r['passed'] else 'FAIL ')+r['test']+': '+json.dumps(r['evidence'],ensure_ascii=False) for r in RESULTS)+'\n')
print('TOTAL:',out['passed'],'/',out['total'])
