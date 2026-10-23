# Minh chứng bổ sung cho báo cáo Đề 29

Bản báo cáo mở rộng có **45 trang, 52 hình**. Các ảnh và kết quả bên dưới ghi nhận hệ thống thực tế; chúng mô tả trạng thái tại thời điểm chụp/chạy lệnh.

## Phân biệt nguồn minh chứng

- `UI_01` đến `UI_29`: 29 ảnh chụp giao diện trực tiếp, gồm website, phpMyAdmin, Prometheus, Grafana và GitHub. Không chèn thêm kết quả giả vào ảnh.
- `CLI_01` đến `CLI_19`: 19 bản ghi command/output. PNG là bản định dạng output để đọc trong báo cáo, **không phải ảnh chụp cửa sổ Terminal**. TXT giữ command, thời điểm, exit code và output; `command-evidence.json` tập hợp cùng dữ liệu. Báo cáo dùng 18 hình CLI, không dùng `CLI_19_Source_tree`.
- `So_do_metrics_logs.png`: sơ đồ kỹ thuật từ cấu hình hệ thống. Hai sơ đồ kiến trúc và dữ liệu cùng hai ảnh trang chủ/danh sách được dùng từ thư mục cha.

Tổng 52 hình trong báo cáo gồm 31 ảnh UI, 18 hình output lệnh và 3 sơ đồ. Lần thu output bổ sung: **2026-10-24T00:15:18+07:00**. Kết quả kiểm thử tích hợp: **2026-10-24T00:00:41.703449+07:00**, đạt 51/51.

Các nhóm `CLI_14`–`CLI_16` trích từ `../verification.json` và giữ thời điểm kiểm thử gốc trong output. `CLI_17` trích `../reproducibility.json`, giữ thời điểm và commit cài mới độc lập; không biểu thị một lần cài mới vừa được chạy lại. `CLI_08` trả exit code khác 0 theo kỳ vọng vì quyền CREATE TABLE bị từ chối.

MySQL error log thường không có dòng mới khi database bình thường; ảnh `UI_29` và kiểm thử dùng khoảng bảy ngày. Ảnh GitHub ghi nhận bốn commit tại thời điểm chụp; các commit bổ sung tài liệu xuất hiện sau đó.

Bản ghi công thức ID 14 phục vụ ảnh thao tác đã được xóa riêng sau khi chụp; hệ thống giữ sáu công thức mẫu. Backup thật nằm trong `runtime/backups/`, quyền 0600 và bị Git bỏ qua. Không đưa mật khẩu, hash mật khẩu hoặc dump database vào minh chứng công khai.

## Đối chiếu hình trong báo cáo

| Hình | Nội dung | Trang | Ảnh nguồn |
| --- | --- | --- | --- |
| 1 | Kiến trúc ứng dụng và các thành phần quan sát | 3 | [So_do_kien_truc.png](../So_do_kien_truc.png) |
| 2 | Phiên bản công cụ được kiểm tra trực tiếp trên Ubuntu | 4 | [CLI_01_Moi_truong.png](CLI_01_Moi_truong.png) |
| 3 | Repository GitHub có source và các thư mục cấu hình | 5 | [UI_20_GitHub_repository.png](UI_20_GitHub_repository.png) |
| 4 | Lịch sử bốn mốc commit tại thời điểm chụp minh chứng | 5 | [UI_21_GitHub_lich_su_commit.png](UI_21_GitHub_lich_su_commit.png) |
| 5 | Các commit kỹ thuật và thời điểm từ git log | 6 | [CLI_02_Git.png](CLI_02_Git.png) |
| 6 | Mười một dịch vụ của project Recipe đang chạy | 8 | [CLI_03_Containers.png](CLI_03_Containers.png) |
| 7 | Các named volume được Docker quản lý | 8 | [CLI_12_Volumes.png](CLI_12_Volumes.png) |
| 8 | Các mạng Docker và thành viên tại thời điểm kiểm tra | 9 | [CLI_05_Networks.png](CLI_05_Networks.png) |
| 9 | Cổng chỉ bind localhost và quyền file bí mật | 9 | [CLI_06_Ports_secrets.png](CLI_06_Ports_secrets.png) |
| 10 | Quan hệ giữa năm bảng dữ liệu của ứng dụng Recipe | 10 | [So_do_du_lieu.png](../So_do_du_lieu.png) |
| 11 | Số dòng dữ liệu và quyền DML thực tế của recipe_user | 11 | [CLI_07_Database.png](CLI_07_Database.png) |
| 12 | Năm bảng Recipe và các bảng WordPress cũ được giữ trên máy | 11 | [UI_17_phpMyAdmin_cau_truc.png](UI_17_phpMyAdmin_cau_truc.png) |
| 13 | Truy vấn JOIN trả sáu công thức cùng danh mục thời gian khẩu phần | 12 | [UI_19_SQL_doi_chieu_cong_thuc.png](UI_19_SQL_doi_chieu_cong_thuc.png) |
| 14 | Trang chủ Recipe được truy cập qua cổng Nginx | 13 | [Hinh_01_Trang_chu_Recipe.png](../Hinh_01_Trang_chu_Recipe.png) |
| 15 | Các thẻ công thức và bộ lọc danh mục | 13 | [Hinh_02_Danh_sach_cong_thuc.png](../Hinh_02_Danh_sach_cong_thuc.png) |
| 16 | Từ khóa me chín trả đúng món canh chua | 14 | [UI_11_Tim_kiem_nguyen_lieu.png](UI_11_Tim_kiem_nguyen_lieu.png) |
| 17 | Danh mục Rau và salad trả một công thức salad | 14 | [UI_12_Loc_danh_muc.png](UI_12_Loc_danh_muc.png) |
| 18 | Thông tin món ăn thời gian và khẩu phần từ database | 15 | [UI_13_Chi_tiet_mon_an.png](UI_13_Chi_tiet_mon_an.png) |
| 19 | Nguyên liệu và hướng dẫn được sắp theo thứ tự | 15 | [UI_14_Nguyen_lieu_cac_buoc.png](UI_14_Nguyen_lieu_cac_buoc.png) |
| 20 | Biểu mẫu đăng nhập quản trị trước khi nhập mật khẩu | 16 | [UI_01_Dang_nhap.png](UI_01_Dang_nhap.png) |
| 21 | Trang quản trị hiển thị danh sách công thức hiện có | 16 | [UI_02_Quan_tri.png](UI_02_Quan_tri.png) |
| 22 | Nhập tên mô tả danh mục thời gian và khẩu phần | 17 | [UI_03_Them_cong_thuc_thong_tin.png](UI_03_Them_cong_thuc_thong_tin.png) |
| 23 | Nhập nguyên liệu cách làm và nút lưu công thức | 17 | [UI_04_Them_nguyen_lieu_cach_nau.png](UI_04_Them_nguyen_lieu_cach_nau.png) |
| 24 | Thông báo lưu thành công và món mới có tổng thời gian 35 phút | 18 | [UI_05_Them_thanh_cong.png](UI_05_Them_thanh_cong.png) |
| 25 | Biểu mẫu chỉnh sửa cùng bản ghi minh họa | 18 | [UI_06_Chinh_sua_cong_thuc.png](UI_06_Chinh_sua_cong_thuc.png) |
| 26 | Tên món được cập nhật và tổng thời gian đổi thành 40 phút | 19 | [UI_07_Sua_thanh_cong.png](UI_07_Sua_thanh_cong.png) |
| 27 | Bản ghi chuyển sang danh sách đã lưu trữ | 19 | [UI_08_Luu_tru_cong_thuc.png](UI_08_Luu_tru_cong_thuc.png) |
| 28 | Công thức đã lưu trữ không còn được phục vụ ở trang chi tiết | 20 | [UI_09_Mon_luu_tru_404.png](UI_09_Mon_luu_tru_404.png) |
| 29 | Cùng công thức hiển thị lại sau khi khôi phục | 20 | [UI_10_Khoi_phuc_cong_thuc.png](UI_10_Khoi_phuc_cong_thuc.png) |
| 30 | Kết quả kiểm tra cú pháp cấu hình Nginx | 22 | [CLI_10_Nginx_config_test.png](CLI_10_Nginx_config_test.png) |
| 31 | HTTP 200 403 404 và security headers từ Nginx | 23 | [CLI_09_HTTP_headers.png](CLI_09_HTTP_headers.png) |
| 32 | Luồng metrics và log cùng được truy vấn qua Grafana | 24 | [So_do_metrics_logs.png](So_do_metrics_logs.png) |
| 33 | Sáu nhóm target Prometheus đều có trạng thái UP | 25 | [UI_15_Prometheus_targets.png](UI_15_Prometheus_targets.png) |
| 34 | Endpoint MySQL Exporter và nhãn job instance | 25 | [UI_16_Target_MySQL_chi_tiet.png](UI_16_Target_MySQL_chi_tiet.png) |
| 35 | Câu up trả sáu chuỗi dữ liệu có giá trị một | 26 | [UI_24_PromQL_up.png](UI_24_PromQL_up.png) |
| 36 | API Prometheus trả endpoint và health của sáu target | 26 | [CLI_13_Targets_API.png](CLI_13_Targets_API.png) |
| 37 | Hai datasource Loki và Prometheus được khai báo sẵn | 27 | [UI_25_Grafana_datasources.png](UI_25_Grafana_datasources.png) |
| 38 | Dashboard hiển thị sáu target UP cùng CPU và RAM của container | 28 | [UI_22_Grafana_CPU_RAM.png](UI_22_Grafana_CPU_RAM.png) |
| 39 | Bốn panel request kết nối MySQL và dữ liệu mạng | 30 | [UI_23_Grafana_web_database_network.png](UI_23_Grafana_web_database_network.png) |
| 40 | Ba luật cảnh báo đã nạp và đang ở trạng thái INACTIVE | 31 | [UI_18_Prometheus_alerts.png](UI_18_Prometheus_alerts.png) |
| 41 | Explore trả các dòng access log và nhãn nguồn Nginx | 33 | [UI_26_LogQL_Nginx_access.png](UI_26_LogQL_Nginx_access.png) |
| 42 | Các request lỗi được lọc bằng trường status sau khi parse JSON | 34 | [UI_27_LogQL_loi_HTTP.png](UI_27_LogQL_loi_HTTP.png) |
| 43 | Các sự kiện đăng nhập thành công có timestamp và user_id | 35 | [UI_28_LogQL_dang_nhap.png](UI_28_LogQL_dang_nhap.png) |
| 44 | MySQL error log hiển thị thông báo khởi động và sẵn sàng kết nối | 36 | [UI_29_LogQL_MySQL.png](UI_29_LogQL_MySQL.png) |
| 45 | Các trường UID read only capabilities và privileged từ Docker inspect | 37 | [CLI_04_Hardening.png](CLI_04_Hardening.png) |
| 46 | Lệnh id xác nhận UID của app Nginx và MySQL | 37 | [CLI_11_UID.png](CLI_11_UID.png) |
| 47 | MySQL trả mã 1142 khi recipe_user thử tạo bảng | 38 | [CLI_08_DDL_bi_tu_choi.png](CLI_08_DDL_bi_tu_choi.png) |
| 48 | Nhóm kiểm thử HTTP tìm kiếm CRUD xác thực và database | 39 | [CLI_14_Test_ung_dung.png](CLI_14_Test_ung_dung.png) |
| 49 | Kết quả kiểm thử target metrics datasource dashboard và bốn LogQL | 40 | [CLI_15_Test_monitoring.png](CLI_15_Test_monitoring.png) |
| 50 | Kết quả kiểm thử cấu hình runtime và cổng mạng | 40 | [CLI_16_Test_runtime.png](CLI_16_Test_runtime.png) |
| 51 | Tám kiểm tra cài mới độc lập từ GitHub ở commit đã ghi nhận | 41 | [CLI_17_Cai_moi.png](CLI_17_Cai_moi.png) |
| 52 | Bản sao lưu mới có quyền 0600 và đọc được định dạng gzip | 41 | [CLI_18_Backup.png](CLI_18_Backup.png) |

## Tái tạo tài liệu

`scripts/capture_report_evidence.py` thu các kiểm tra hiện trạng và tạo một bản sao lưu mới; chạy trên máy lab có dịch vụ Docker đang hoạt động và Python có Pillow. `docs/build_report.py` dùng ảnh và dữ liệu đã thu để dựng Word; cần python-docx và Pillow. Ảnh UI được chụp riêng sau khi thực hiện thao tác thật. Khi thay đổi nội dung cần xuất PDF lại và kiểm tra bố cục.
