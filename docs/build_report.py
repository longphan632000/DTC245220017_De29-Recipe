"""Tạo báo cáo Word từ minh chứng thực tế. Cần python-docx và Pillow."""
from pathlib import Path
import json, subprocess, textwrap, datetime
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'minh-chung';OUT=ROOT/'docs';OUT.mkdir(exist_ok=True)
V=json.loads((E/'verification.json').read_text())
CHECKED_AT=datetime.datetime.fromisoformat(V['time'])
REPRO=json.loads((E/'reproducibility.json').read_text())
REPO='https://github.com/longphan632000/DTC245220017_De29-Recipe'

font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def diagram(path,kind):
    im=Image.new('RGB',(1600,1000),'white');d=ImageDraw.Draw(im)
    f=ImageFont.truetype(font,29);small=ImageFont.truetype(font,24);large=ImageFont.truetype(font,38);boxfont=ImageFont.truetype(font,34)
    def box(x,y,w,h,title,lines,fill='#edf3ee'):
        d.rounded_rectangle((x,y,x+w,y+h),18,fill=fill,outline='#809789',width=2)
        d.text((x+22,y+18),title,font=boxfont,fill='#173b2c')
        for i,line in enumerate(lines):d.text((x+22,y+76+i*38),line,font=small,fill='#283e32')
    def arrow(x1,y1,x2,y2,label=''):
        import math
        d.line((x1,y1,x2,y2),fill='#50645a',width=4)
        a=math.atan2(y2-y1,x2-x1);pts=[(x2,y2),(x2-18*math.cos(a-.45),y2-18*math.sin(a-.45)),(x2-18*math.cos(a+.45),y2-18*math.sin(a+.45))]
        d.polygon(pts,fill='#50645a')
        if label:d.text(((x1+x2)/2-40,(y1+y2)/2-32),label,font=small,fill='#526557')
    if kind=='architecture':
        d.text((50,25),'Luồng truy cập và quan sát hệ thống Recipe',font=large,fill='black')
        box(40,120,280,155,'Trình duyệt',['127.0.0.1:8088','127.0.0.1:8081'])
        box(420,120,290,155,'Nginx',['Reverse proxy','Security headers'])
        box(820,120,300,155,'Ứng dụng PHP',['Apache 8080','Món ăn và quản trị'])
        box(1230,120,310,155,'MySQL',['recipe_db','5 bảng ứng dụng'])
        arrow(320,197,420,197);arrow(710,197,820,197);arrow(1120,197,1230,197)
        box(820,365,300,155,'phpMyAdmin',['Tài khoản DML','Qua Nginx :8081'])
        arrow(710,240,820,405);arrow(1120,430,1380,275)
        box(40,620,340,180,'Grafana',['Dashboard metrics','Dashboard và Explore log'])
        box(490,620,350,180,'Prometheus',['Scrape mỗi 15 giây','cAdvisor và exporters'])
        box(980,620,280,180,'Loki',['TSDB filesystem','Retention 7 ngày'])
        box(1230,365,310,155,'Promtail',['Đọc volume log','Nginx PHP MySQL'],fill='#eef0e5')
        arrow(380,670,490,670);d.line([(380,760),(430,760),(430,565),(1120,565),(1120,620)],fill='#50645a',width=4);arrow(1120,600,1120,620);d.text((720,530),'LogQL',font=small,fill='#526557');arrow(1385,520,1240,620,'Push log')
        arrow(665,620,665,275,'Metrics')
        d.text((50,865),'web_net  Nginx và ứng dụng     db_net  internal     monitoring_net  internal',font=f,fill='#334c3e')
        d.text((50,918),'management_net  UI quản trị chỉ publish qua localhost',font=f,fill='#334c3e')
    else:
        d.text((50,30),'Mô hình dữ liệu của ứng dụng Recipe',font=large,fill='black')
        box(70,160,370,230,'categories',['id PK','name UNIQUE'])
        box(600,160,390,300,'recipes',['id PK, category_id FK','title, description','prep_minutes, cook_minutes','servings, is_deleted'])
        box(1140,100,390,250,'ingredients',['id PK, recipe_id FK','name, position','UNIQUE recipe_id position'])
        box(1140,460,390,250,'steps',['id PK, recipe_id FK','instruction, position','UNIQUE recipe_id position'])
        box(70,570,370,250,'users',['id PK, username UNIQUE','password_hash','role admin'])
        arrow(440,260,600,260,'1 → N');arrow(990,250,1140,225,'1 → N');arrow(990,380,1140,550,'1 → N')
        d.text((540,780),'Dữ liệu mẫu  4 danh mục  6 công thức',font=f,fill='#334c3e')
        d.text((540,835),'36 nguyên liệu  27 bước  1 quản trị viên',font=f,fill='#334c3e')
        d.text((70,920),'InnoDB và utf8mb4   Khóa ngoại giữ tính toàn vẹn dữ liệu',font=f,fill='#334c3e')
    im.save(path)

diagram(E/'So_do_kien_truc.png','architecture');diagram(E/'So_do_du_lieu.png','data')
doc=Document();sec=doc.sections[0]
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=Inches(.8);sec.bottom_margin=Inches(.75);sec.left_margin=Inches(.9);sec.right_margin=Inches(.9)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
    st=doc.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
    rf=st.element.rPr.rFonts
    for attr in ['ascii','hAnsi','eastAsia','cs']:rf.set(qn('w:'+attr),'Times New Roman')
    for attr in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
        if qn('w:'+attr) in rf.attrib:del rf.attrib[qn('w:'+attr)]
normal=doc.styles['Normal'];normal.font.size=Pt(12);normal.paragraph_format.line_spacing=1.2;normal.paragraph_format.space_after=Pt(7)
doc.styles['Title'].font.size=Pt(21)
doc.styles['Heading 1'].font.size=Pt(17);doc.styles['Heading 1'].font.bold=True
doc.styles['Heading 2'].font.size=Pt(13);doc.styles['Heading 2'].font.bold=True
doc.styles['Caption'].font.size=Pt(10);doc.styles['Caption'].font.italic=True
for n in ['Heading 1','Heading 2']:
    doc.styles[n].paragraph_format.space_before=Pt(9);doc.styles[n].paragraph_format.space_after=Pt(10)
header=sec.header.paragraphs[0];header.text='Triển khai và Quản trị Hệ thống Phần mềm     |     Đề 29 Recipe'
for run in header.runs:run.font.size=Pt(9);run.font.color.rgb=RGBColor(0,0,0)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER;footer.add_run('Trang ')
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
doc.core_properties.title='Báo cáo triển khai Website Công thức Nấu ăn Recipe'
doc.core_properties.subject='Đề 29 DTC245220017';doc.core_properties.author='DTC245220017'

def p(text):
    x=doc.add_paragraph(text);x.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;return x
def h(text):doc.add_heading(text,level=2)
def page(title):doc.add_page_break();doc.add_heading(title,level=1)
def code(text):
    for line in text.splitlines():
        for part in textwrap.wrap(line,85,break_long_words=False,break_on_hyphens=False) or ['']:
            x=doc.add_paragraph();x.paragraph_format.line_spacing=1.05;x.paragraph_format.space_after=Pt(2)
            r=x.add_run(part);r.font.name='Liberation Mono';r.font.size=Pt(9)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
def table(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    if widths:
        for i,width in enumerate(widths):t.columns[i].width=Inches(width)
    for i,x in enumerate(headers):t.rows[0].cells[i].text=x
    for row in rows:
        cells=t.add_row().cells
        for i,x in enumerate(row):cells[i].text=str(x)
    for ri,row in enumerate(t.rows):
        pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
        if ri==0:pr.append(OxmlElement('w:tblHeader'))
        for ci,c in enumerate(row.cells):
            if widths:c.width=Inches(widths[ci])
            c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            props=c._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)
            props.append(b);m=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:w'),'90');e.set(qn('w:type'),'dxa');m.append(e)
            props.append(m)
            shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'DCE6F1' if ri==0 else ('F5F7F8' if ri%2==0 else 'FFFFFF'));props.append(shade)
            for para in c.paragraphs:
                para.paragraph_format.space_after=Pt(2);para.paragraph_format.line_spacing=1.08
                for r in para.runs:r.font.size=Pt(10.5);r.bold=ri==0
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
def image(name,caption,maxheight=3.8):
    path=E/name
    if not path.exists():raise FileNotFoundError(path)
    im=Image.open(path);ratio=im.width/im.height;width=min(6.5,maxheight*ratio)
    x=doc.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.keep_with_next=True
    x.add_run().add_picture(str(path),width=Inches(width))
    c=doc.add_paragraph(caption,style='Caption');c.alignment=WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph('Báo cáo triển khai và quản trị hệ thống',style='Title')
doc.add_heading('Đề 29 Website Công thức Nấu ăn Recipe',level=1)
p('Báo cáo trình bày hệ thống chia sẻ công thức nấu ăn triển khai trên Ubuntu bằng Docker Compose. Phần mềm sử dụng PHP và MySQL, có phpMyAdmin, Nginx reverse proxy, Prometheus, Grafana, Loki và Promtail. Mã nguồn và cấu hình được quản lý trên GitHub theo mã sinh viên DTC245220017.')
p(f'Tại thời điểm kiểm tra {CHECKED_AT.strftime("%d/%m/%Y")}, hệ thống đã vượt qua {V["passed"]}/{V["total"]} kiểm tra tích hợp. Kết quả được thu trực tiếp từ HTTP, API giám sát, truy vấn log và cấu hình runtime Docker.')
h('Phạm vi và tiêu chí nghiệm thu')
table(['Tiêu chí','Sản phẩm và minh chứng'],[
('GitHub','Mã nguồn, README, cấu hình và ba commit theo các giai đoạn kỹ thuật'),('Ứng dụng và database','Danh mục, món ăn, nguyên liệu, cách nấu, quản trị và phpMyAdmin'),('Reverse proxy','Truy cập qua Nginx với security headers cơ bản'),('Giám sát','Metrics container, Nginx và MySQL; dashboard Grafana'),('Log tập trung','Log ba nguồn, Loki và ít nhất ba truy vấn LogQL'),('Hardening','Non-root, mạng nội bộ, giảm quyền, bảo vệ bí mật và ứng dụng'),('Báo cáo và demo','Ảnh giao diện, kết quả kiểm thử và hướng dẫn vận hành')],[1.6,4.9])
p('Các phần tiếp theo lần lượt mô tả kiến trúc, mã nguồn, dữ liệu, chức năng ứng dụng, reverse proxy, giám sát, log, hardening và quy trình vận hành. Báo cáo phân biệt kết quả đã kiểm tra với giới hạn của môi trường lab; không xem việc container khởi động là bằng chứng duy nhất của chức năng.')

page('1 Kiến trúc và luồng hoạt động')
image('So_do_kien_truc.png','Hình 1 Kiến trúc ứng dụng và các lớp quan sát',3.65)
p('Người dùng truy cập Nginx tại cổng 8088. Nginx chuyển yêu cầu tới Apache của ứng dụng PHP trên cổng nội bộ 8080. Ứng dụng đọc và ghi MySQL qua PDO. Cổng 8081 của Nginx chuyển tới phpMyAdmin để xem dữ liệu bằng tài khoản ứng dụng; không công bố cổng MySQL ra host.')
table(['Mạng','Thành phần và mục đích'],[('web_net','Nginx, ứng dụng và phpMyAdmin'),('db_net internal','MySQL, ứng dụng, phpMyAdmin và MySQL Exporter'),('monitoring_net internal','Prometheus, Grafana, exporters, Loki và Promtail'),('management_net','Kết nối các UI giám sát với cổng loopback trên host')],[1.8,4.7])
p('Prometheus chủ động scrape metrics từ các exporter; Grafana truy vấn Prometheus để vẽ biểu đồ. Với log, Promtail đọc các volume chỉ đọc của Nginx, PHP và MySQL rồi gửi dữ liệu tới Loki. Grafana sử dụng datasource Loki để truy vấn LogQL. Các luồng dữ liệu này được tách khỏi luồng người dùng truy cập website.')

page('2 Quản lý mã nguồn và khởi tạo')
p('Repository công khai của bài làm: '+REPO+'. Khung thư mục tham khảo dự án Blog CMS, gồm app/src, mysql, nginx, prometheus, loki và promtail. Dự án bổ sung provisioning Grafana, script khởi tạo và bộ kiểm thử để tái lập cấu hình. Mật khẩu, khóa bí mật và bản dump database không nằm trong lịch sử Git.')
commits=subprocess.run(['git','log','--reverse','--format=%h|%s'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()[:3]
table(['Commit','Nội dung kỹ thuật'],[x.split('|',1) for x in commits],[1,5.5])
h('Cài đặt từ repository')
code('git clone '+REPO+'.git\ncd DTC245220017_De29-Recipe\npython3 scripts/setup.py\ndocker compose ps -a\npython3 scripts/verify.py')
p('Script setup tạo các mật khẩu ngẫu nhiên trong .env, chuẩn bị secret cho phpMyAdmin, build image và khởi động MySQL. Sau khi database healthy, script nạp schema và dữ liệu mẫu, giới hạn quyền DB, tạo tài khoản quản trị ứng dụng rồi chạy các thành phần còn lại. Chạy lại script giữ tài khoản đã có và không xóa volume.')
table(['Thành phần','Phiên bản hoặc cơ chế cố định'],[('Ứng dụng','PHP 8.3 và Apache từ image ghim digest'),('Database','MySQL 8.0.46; phpMyAdmin 5.2.3'),('Grafana','13.2.2; tắt tự cập nhật plugin khi chạy'),('Log','Loki 3.7.8; Promtail 3.6.8'),('Image khác','Ghim SHA256 digest trong Compose hoặc Dockerfile')],[1.7,4.8])

page('3 Thiết kế cơ sở dữ liệu')
image('So_do_du_lieu.png','Hình 2 Quan hệ giữa năm bảng của ứng dụng Recipe',3.4)
table(['Bảng','Nội dung','Số dòng mẫu'],[('categories','Tên danh mục món ăn',4),('recipes','Món ăn, mô tả, thời gian, khẩu phần, trạng thái',6),('ingredients','Nguyên liệu và thứ tự trong công thức',36),('steps','Hướng dẫn chế biến theo thứ tự',27),('users','Tên đăng nhập, password hash và vai trò',1)],[1.1,4.1,1.3])
p('Schema dùng InnoDB, utf8mb4 và khóa ngoại. recipes liên kết categories; ingredients và steps liên kết recipes, có ràng buộc thứ tự trong từng món. Mật khẩu không lưu ở dạng rõ trong users. Lưu trữ công thức chỉ đổi is_deleted; khôi phục đưa công thức trở lại danh sách công khai.')
p('Trên máy Ubuntu hiện tại, các bảng wp_ từ lần cài WordPress ban đầu được giữ để bảo toàn dữ liệu. Ứng dụng PHP không sử dụng chúng. Cài mới từ repo chỉ tạo năm bảng nêu trên; dữ liệu cũ đã có bản sao lưu cục bộ trước khi triển khai theo khung PHP.')
doc.add_page_break();doc.add_heading('Kiểm tra cơ sở dữ liệu bằng phpMyAdmin',level=2)
image('Hinh_05_phpMyAdmin_recipe_db.png','Hình 3 Database Recipe được truy cập thành công bằng phpMyAdmin',3.8)
p('Giao diện phpMyAdmin truy cập qua Nginx tại http://127.0.0.1:8081. Sau khi đăng nhập bằng recipe_user, cột bên trái hiển thị recipe_db và các bảng dữ liệu. Năm bảng đầu gồm categories, ingredients, recipes, steps và users là các bảng mà ứng dụng PHP sử dụng.')
p('Ảnh chụp xác nhận bốn danh mục, sáu công thức, 36 dòng nguyên liệu, 27 bước chế biến và một quản trị viên. Các bảng có tiền tố wp_ phía dưới là dữ liệu WordPress cũ được giữ trên máy hiện tại. Kết quả cài mới độc lập từ repo chỉ có đúng năm bảng ứng dụng, đã được kiểm chứng bằng truy vấn information_schema.')
p('Tài khoản này chỉ có quyền DML, đủ để xem và sửa bản ghi trong database được cấp. phpMyAdmin không cho phép đăng nhập bằng root. Bộ kiểm thử xác minh đăng nhập thành công và đọc được cấu trúc các bảng; đồng thời lệnh thử CREATE TABLE bằng tài khoản ứng dụng bị MySQL từ chối, chứng minh việc giới hạn quyền đã có hiệu lực.')

page('4 Giao diện và tìm kiếm công thức')
image('Hinh_01_Trang_chu_Recipe.png','Hình 4 Trang chủ Recipe được phục vụ qua Nginx',3.8)
p('Trang chủ hiển thị các công thức công khai, thời gian nấu, khẩu phần, độ khó và danh mục. Dữ liệu lấy từ MySQL, không phải nội dung chỉ hiển thị cố định trong HTML. Sáu món mẫu gồm phở gà, bánh mì gà xé, cơm rang rau củ, canh chua cá, salad và chè đậu xanh.')
p('Ô tìm kiếm hỗ trợ tên món, mô tả và nguyên liệu. Kiểm thử từ khóa “me chín” trả đúng món canh chua. Bộ lọc “Rau và salad” trả một công thức salad. Người dùng có thể kết hợp từ khóa và danh mục; khi không có kết quả, giao diện hiển thị hướng dẫn thử lại.')
p('CSS có bố cục thích ứng với màn hình nhỏ. Các hình minh họa SVG đi kèm source giúp website chạy độc lập với dịch vụ ảnh bên ngoài. Nội dung nhập từ người dùng được escape trước khi hiển thị; câu lệnh tìm kiếm dùng tham số PDO.')

page('5 Chi tiết món ăn và nguyên liệu')
image('Hinh_03_Nguyen_lieu_cach_nau.png','Hình 5 Nguyên liệu và các bước thực hiện của món phở gà',3.8)
p('Trang chi tiết đọc một công thức bằng ID, nối tên danh mục và truy vấn các nguyên liệu, các bước theo position. Phần thông tin đầu trang cho biết thời gian sơ chế, thời gian nấu, khẩu phần và độ khó. Người nấu có thể đánh dấu nguyên liệu đã chuẩn bị bằng checkbox; các checkbox chỉ phục vụ thao tác trong giao diện.')
p('Công thức phở gà mẫu có sáu dòng nguyên liệu và năm bước chế biến. Những món khác có cấu trúc dữ liệu tương tự nên quản trị viên có thể chỉnh nội dung mà không cần sửa template. Nút in sử dụng định dạng riêng để bỏ điều hướng và giữ nội dung nấu ăn.')
p('Nếu ID không tồn tại hoặc công thức đã lưu trữ, ứng dụng trả mã HTTP 404 và trang thông báo. Trường hợp này đồng thời tạo dữ liệu để kiểm chứng truy vấn LogQL lọc những yêu cầu lỗi. Ảnh minh chứng trên là giao diện thật sau khi truy xuất database.')

page('6 Đăng nhập và quản trị nội dung')
image('Hinh_04_Quan_tri_Recipe.png','Hình 6 Quản trị viên quản lý các công thức Recipe',3.7)
p('Tài khoản quản trị được khởi tạo từ APP_ADMIN_USER và APP_ADMIN_PASSWORD trong .env. Khi đăng nhập, ứng dụng so sánh password hash và đổi session ID. Người dùng chưa có session hợp lệ được chuyển về trang đăng nhập khi truy cập chức năng quản trị.')
table(['Thao tác','Kết quả kiểm thử'],[('Thêm','Tạo món mới với nguyên liệu và các bước bằng transaction'),('Sửa','Cập nhật tên, mô tả, danh mục, thời gian và nội dung'),('Lưu trữ','Ẩn công thức; truy cập công khai nhận 404'),('Khôi phục','Đưa công thức trở lại trang công khai')],[1.4,5.1])
p('Các thao tác thay đổi dữ liệu dùng POST có CSRF token. Form kiểm tra danh mục hợp lệ, khẩu phần từ 1 đến 50, thời gian tối đa 600 phút và nội dung không được rỗng. Bộ kiểm thử tạo dữ liệu riêng, thực hiện đủ chu trình rồi xóa đúng bản ghi tạm; sáu công thức mẫu vẫn được giữ nguyên.')

page('7 Nginx reverse proxy và security headers')
p('Nginx lắng nghe cổng 8080 trong container và được publish thành 127.0.0.1:8088. Một server block khác lắng nghe 8081 để chuyển tới phpMyAdmin. Ứng dụng và phpMyAdmin không mở cổng trực tiếp ra host. Docker DNS được phân giải lại định kỳ để upstream có thể đổi địa chỉ khi container được tạo lại.')
code('resolver 127.0.0.11 valid=10s ipv6=off;\nupstream recipe_backend {\n    zone recipe_backend 64k;\n    server app:8080 resolve;\n}\nproxy_set_header Host $http_host;\nproxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;')
table(['Header','Ý nghĩa'],[('X-Content-Type-Options nosniff','Ngăn trình duyệt tự đoán MIME khác với nội dung khai báo'),('X-Frame-Options SAMEORIGIN','Giới hạn việc nhúng trang trong frame khác nguồn'),('Referrer-Policy','Giảm thông tin referrer gửi sang nguồn khác'),('Permissions-Policy','Tắt camera, microphone và geolocation cho website'),('Content-Security-Policy','Giới hạn nguồn script, style, ảnh, kết nối và form')],[2.6,3.9])
p('Bản lab chọn security headers cơ bản theo phương án mà đề bài cho phép. HTTP chỉ chạy trên loopback; không tuyên bố đã triển khai HTTPS cho môi trường Internet. Nginx ẩn phiên bản, chặn các file cấu hình và giới hạn tần suất truy cập trang đăng nhập. Kiểm thử /.env nhận HTTP 403.')
p('Access log Nginx có định dạng JSON với mã HTTP và thời gian đáp ứng. Log dùng URI không kèm query string để hạn chế ghi dữ liệu người dùng. Endpoint stub_status chỉ nằm trong mạng giám sát và được Nginx Exporter sử dụng, không có cổng host riêng.')

page('8 Prometheus và các exporter')
image('Hinh_06_Prometheus_targets.png','Hình 7 Sáu target được Prometheus scrape thành công',3.55)
p('Prometheus thu thập mỗi 15 giây từ chính Prometheus, cAdvisor, Nginx Exporter, MySQL Exporter, Loki và Promtail. Kết quả API xác nhận đủ sáu target UP. mysql_up bằng 1 chứng minh exporter kết nối được MySQL; nginx_up bằng 1 chứng minh exporter lấy được stub_status từ Nginx.')
code('up\nmysql_up\nnginx_up\nrate(nginx_http_requests_total[2m])\nrate(mysql_global_status_questions[2m])')
p('cAdvisor cung cấp CPU, RAM và mạng container. Dashboard lọc theo nhãn com.docker.compose.project bằng recipe để tập trung vào bài làm. Prometheus giữ dữ liệu trong named volume, giới hạn retention 7 ngày hoặc dung lượng TSDB 512 MB. Bộ alert rules gồm target down, MySQL down và Nginx down sau một phút; chưa cấu hình gửi thông báo ra dịch vụ ngoài.')

page('9 Dashboard Grafana')
image('Hinh_07_Grafana_metrics.png','Hình 8 Dashboard metrics của Recipe từ dữ liệu thực',3.7)
p('Datasource Prometheus và Loki được khai báo bằng provisioning YAML. Hai dashboard được lưu dưới dạng JSON trong repository và nạp tự động khi Grafana khởi động. Người dùng không phải import dashboard thủ công sau mỗi lần cài mới. API health đã xác minh cả hai datasource hoạt động.')
p('Dashboard metrics có mười panel: số target UP, trạng thái MySQL và Nginx, kết nối MySQL, CPU và RAM theo container, yêu cầu Nginx mỗi giây, kết nối Nginx, số truy vấn MySQL và lưu lượng mạng nhận theo container. CPU dùng rate trong khoảng hai phút; cần có nhiều mẫu scrape để vẽ đường thời gian có ý nghĩa.')
p('Grafana chạy bằng UID 472, dùng filesystem gốc chỉ đọc và volume riêng cho dữ liệu. Chức năng tự cài/cập nhật plugin được tắt để giữ đúng bản plugin đã có trong image và tránh sửa filesystem bất biến. Tài khoản quản trị dùng mật khẩu riêng trong .env; đăng ký công khai và anonymous access đều bị tắt.')

page('10 Log tập trung và truy vấn LogQL')
image('Hinh_08_Grafana_LogQL.png','Hình 9 Dashboard log và kết quả truy vấn từ Loki',3.45)
p('Nginx, PHP và MySQL ghi log vào ba named volume. Promtail chỉ mount các volume này ở chế độ chỉ đọc, không được cấp Docker socket. Vị trí đọc được lưu trong volume positions; Loki lưu TSDB và chunks trên volume riêng. Nhãn project, job và service giúp chọn đúng nguồn log.')
code('{job="nginx"}\n{job="nginx"} | json | status >= 400\n{job="app"} |= "login_success"\n{job="mysql"}')
p('Truy vấn đầu liệt kê access log. Truy vấn thứ hai parse JSON rồi lọc mã HTTP từ 400, có các sự kiện 403 và 404 do kiểm thử tạo ra. Truy vấn thứ ba tìm đăng nhập thành công vào ứng dụng; truy vấn cuối đọc log database. Cả bốn truy vấn đều trả bản ghi thực và được lưu trong các file logql-1.json đến logql-4.json.')
p('Mật khẩu, cookie và CSRF token không được ghi vào audit log. Loki đặt retention 168 giờ. Promtail được dùng để đáp ứng đúng yêu cầu học phần; với hệ thống mới đưa vào vận hành thực tế cần xem lộ trình chuyển sang Alloy vì Promtail đã kết thúc hỗ trợ.')

page('11 Hardening container và dữ liệu')
p('Hardening được kiểm chứng trên container đang chạy bằng Docker inspect và thử nghiệm HTTP/SQL. Cấu hình nguồn chỉ là ý định; kết quả runtime trong verification.json cho thấy các biện pháp đã được áp dụng khi triển khai.')
table(['Biện pháp','Áp dụng và kết quả'],[('Non-root','App/phpMyAdmin UID 33; Nginx 101; MySQL 999; Grafana 472; Prometheus/exporter 65534; Loki/Promtail 10001'),('Giảm quyền','Tất cả service bỏ ALL capabilities, bật no-new-privileges và không privileged'),('Filesystem','Root filesystem chỉ đọc; dữ liệu và log nằm trong volume; file tạm ở tmpfs'),('Tách mạng','db_net và monitoring_net internal; MySQL không publish cổng; UI chỉ 127.0.0.1'),('Bí mật','Mật khẩu ngẫu nhiên riêng; .env mode 600; secrets directory mode 700; loại khỏi Git'),('Quyền DB','Ứng dụng chỉ DML trên database; thử CREATE TABLE nhận lỗi MySQL 1142'),('Ứng dụng','Băm mật khẩu, CSRF, HTML escape, prepared statements và đổi session ID'),('Cấu hình ổn định','Image ghim digest, giới hạn RAM và Docker log rotation')],[1.45,5.05])
h('Ngoại lệ của collector')
p('cAdvisor là service duy nhất chạy root để đọc cgroups và metadata Docker/containerd. Collector không privileged, không publish cổng và dùng mount host chỉ đọc. Tuy nhiên socket Unix gắn :ro vẫn cho phép gọi API runtime; đây là thành phần phải được tin cậy, không được xem tương đương cách ly hoàn toàn host.')
p('phpMyAdmin chặn đăng nhập root và chỉ dùng tài khoản ứng dụng. Exporter có tài khoản riêng với quyền giám sát chỉ đọc và giới hạn ba kết nối đồng thời. Không sử dụng mật khẩu hoặc private key từ repository tham khảo.')

page('12 Kết quả kiểm thử và khả năng tái lập')
p(f'Bộ kiểm thử thực hiện {V["total"]} kiểm tra và ghi nhận {V["passed"]} kết quả đạt lúc {CHECKED_AT.strftime("%H:%M:%S ngày %d/%m/%Y")}. Dữ liệu thử được tách bằng tên và ID, sau đó dọn đúng bản ghi tạm. Các kết quả chi tiết nằm trong minh-chung/verification.json và verification.txt để có thể đối chiếu lại.')
table(['Nhóm kiểm thử','Kết quả quan sát'],[('HTTP và database','Health 200, kết nối PDO thành công, tiếng Việt đúng'),('Nội dung công khai','Tìm theo nguyên liệu, lọc danh mục, hiển thị nguyên liệu và các bước'),('Quản trị','Đăng nhập, đổi session, tạo, sửa, lưu trữ và khôi phục'),('Bảo vệ dữ liệu','CSRF 403, mật khẩu sai 401, SQL injection và XSS được xử lý'),('phpMyAdmin','Đăng nhập được, nhìn thấy đủ năm bảng ứng dụng'),('Metrics','Sáu target UP; dữ liệu CPU/RAM; mysql_up và nginx_up bằng 1'),('Grafana','Hai datasource healthy; dashboard mười panel được provision'),('LogQL','Bốn truy vấn có kết quả'),('Runtime','Non-root theo vai trò, cap_drop ALL, read_only và loopback ports'),('Cài mới','Clone từ GitHub, database và volume mới; health và dữ liệu mẫu hợp lệ')],[1.6,4.9])
p('Kiểm tra cài mới sử dụng project Docker Compose riêng và cổng host khác, không dùng volume của hệ thống chính. Kết quả được lưu trong reproducibility.json. Các container và volume thử chỉ được xóa sau khi kiểm tra xong. Kết quả này chứng minh script khởi tạo hoạt động từ mã nguồn đã đẩy lên GitHub, thay vì phụ thuộc hoàn toàn vào dữ liệu có sẵn trên máy.')
p('Ảnh minh chứng chụp từ giao diện đang chạy; JSON lấy từ API và Docker inspect. Không dùng hình dựng để thay cho ảnh kết quả. Các file minh chứng không chứa thông tin đăng nhập.')

page('13 Vận hành sao lưu và kịch bản demo')
h('Khởi động và theo dõi')
code('cd DTC245220017_De29-Recipe\npython3 scripts/setup.py\ndocker compose ps -a\npython3 scripts/verify.py\ndocker compose logs --tail=50 app nginx')
p('Nếu máy được khởi động lại, restart policy unless-stopped khởi chạy lại các dịch vụ đã chạy. Có thể dùng docker compose stop để tạm dừng và docker compose up -d để chạy lại. Không dùng down -v khi cần giữ database, dashboards, metrics và log. Nếu chỉnh cấu hình Nginx, build lại image và tạo lại container tương ứng.')
h('Sao lưu database')
code('python3 scripts/backup.py')
p('Script dùng mysqldump với single-transaction và tạo file gzip có quyền 600 trong runtime/backups. Bản sao lưu không được commit. Cần lưu thêm .env bằng phương thức riêng an toàn nếu muốn khôi phục tài khoản và cấu hình sang máy khác. Thao tác phục hồi ghi đè database phải được cân nhắc và sao lưu hiện trạng trước.')
h('Trình tự demo đề xuất')
for text in ['Mở GitHub, chỉ rõ README và ba commit triển khai theo giai đoạn.','Chạy docker compose ps rồi mở website, tìm một nguyên liệu và lọc danh mục.','Mở chi tiết món ăn, minh họa nguyên liệu, các bước và khẩu phần.','Đăng nhập quản trị, thêm hoặc chỉnh một công thức và kiểm tra trên website.','Mở phpMyAdmin để đối chiếu bản ghi trong MySQL.','Mở Prometheus Targets và dashboard Grafana; giải thích các panel container, web và DB.','Chạy ba truy vấn LogQL, giải thích một log 403 hoặc 404.','Trình bày hardening, kết quả verify.py và cách sao lưu.']:doc.add_paragraph(text,style='List Number')

page('14 Đánh giá giới hạn và tài liệu tham khảo')
p('Hệ thống đáp ứng các hạng mục kỹ thuật của Đề 29 trong môi trường lab: ứng dụng công thức nấu ăn, MySQL và phpMyAdmin, reverse proxy, giám sát container/web/database, log tập trung, truy vấn LogQL và hardening. Mã nguồn, cấu hình và hướng dẫn được quản lý chung trong repository, có script khởi tạo và kiểm tra lại.')
p('Các giới hạn cần phân biệt khi trình bày: website chạy HTTP trên localhost với security headers, chưa có chứng chỉ HTTPS cho miền công khai; alert rules chưa nối tới dịch vụ thông báo ngoài; log file nguồn chưa có lịch logrotate; dữ liệu minh họa gồm sáu công thức. Cấu hình nhiều replica, high availability và đánh giá tải lớn không thuộc phạm vi kiểm thử của bản lab này.')
p('Promtail đã hết hỗ trợ ngày 02/03/2026 theo Grafana. Đề bài yêu cầu Loki và Promtail nên bài làm vẫn triển khai thành phần này, đồng thời ghi rõ hướng chuyển đổi sang Alloy cho môi trường vận hành thực. Base image được cố định bằng digest để kết quả cài đặt không thay đổi ngoài ý muốn, nhưng việc cập nhật bảo mật cần được thực hiện có kiểm thử.')
h('Tài liệu tham khảo')
sources=[('Mã nguồn bài làm',REPO),('Dự án Blog CMS tham khảo','https://github.com/Khanhslee/DTC245220024_De7-Blog-CMS'),('Nginx stub status','https://nginx.org/en/docs/http/ngx_http_stub_status_module.html'),('Nginx Prometheus Exporter','https://github.com/nginx/nginx-prometheus-exporter'),('MySQL Exporter và quyền giám sát','https://github.com/prometheus/mysqld_exporter'),('Grafana configuration','https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/'),('Promtail và vòng đời hỗ trợ','https://grafana.com/docs/loki/latest/send-data/promtail/')]
for label,url in sources:
    x=doc.add_paragraph(label+'\n'+url);x.paragraph_format.line_spacing=1.05;x.paragraph_format.space_after=Pt(7)
    for r in x.runs:r.font.size=Pt(10)
p('Phụ lục điện tử đi kèm gồm ảnh giao diện, verification.json, bốn kết quả LogQL và kết quả cài mới.')

for tree in [doc.styles.element,doc._element]:
    for border in list(tree.iter(qn('w:pBdr'))):border.getparent().remove(border)
path=OUT/'Bao_cao_De29_Recipe.docx';doc.save(path);print(path)
