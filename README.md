# Đề 29 Website Công thức Nấu ăn Recipe

Ứng dụng PHP và MySQL chia sẻ món ăn, nguyên liệu, các bước nấu và danh mục. Quản trị viên có thể thêm, sửa, lưu trữ và khôi phục công thức. Dự án triển khai bằng Docker Compose trên Ubuntu; khung thư mục tham khảo repo [Đề 7 Blog CMS](https://github.com/Khanhslee/DTC245220024_De7-Blog-CMS).

Mã sinh viên: **DTC245220017**. Phần bìa báo cáo do sinh viên bổ sung.

## Khởi chạy

Cần Docker Engine, Docker Compose v2, Git và Python 3.

```bash
git clone https://github.com/longphan632000/DTC245220017_De29-Recipe.git
cd DTC245220017_De29-Recipe
python3 scripts/setup.py
```

Script tạo `.env` với mật khẩu ngẫu nhiên, build ứng dụng, tạo schema và tài khoản quản trị. Nếu đã có `.env`, script giữ các giá trị đã cấu hình. Không sao chép nguyên mật khẩu mẫu từ `.env.example`.

## Dịch vụ

| Dịch vụ | Địa chỉ |
| --- | --- |
| Website qua Nginx | http://127.0.0.1:8088 |
| Quản trị Recipe | http://127.0.0.1:8088/?page=login |
| phpMyAdmin qua Nginx | http://127.0.0.1:8081 |
| MySQL | Mạng nội bộ `db_net`, không publish cổng |
| Grafana | http://127.0.0.1:3000 |
| Prometheus | http://127.0.0.1:9090 |

Tài khoản ứng dụng dùng `APP_ADMIN_USER`, `APP_ADMIN_PASSWORD`. phpMyAdmin dùng `MYSQL_USER`, `MYSQL_PASSWORD`. Tất cả bí mật chỉ lưu trong `.env`, quyền `600`, không commit lên GitHub.

## Cấu trúc

`app/src` chứa mã nguồn PHP, `mysql/init.sql` chứa schema và dữ liệu mẫu, `nginx/nginx.conf` cấu hình reverse proxy và security headers. `docker-compose.yml` quản lý các dịch vụ và volume dữ liệu.

## Bảo mật

Ứng dụng, MySQL, phpMyAdmin và Nginx chạy bằng UID không phải root. Container bỏ toàn bộ Linux capabilities, bật `no-new-privileges`, đặt filesystem gốc chỉ đọc. Database dùng mạng nội bộ và tài khoản ứng dụng chỉ có quyền DML. Mật khẩu đăng nhập được băm; POST có CSRF token và truy vấn DB có tham số. Nginx thêm security headers và hạn chế tần suất đăng nhập.

## Dừng hệ thống

```bash
docker compose stop
docker compose up -d
```

Không dùng `down -v` khi cần giữ dữ liệu.

## Giám sát

Prometheus scrape mỗi 15 giây từ cAdvisor, Nginx Exporter và MySQL Exporter. Grafana tự nhận datasource và dashboard **Recipe — Containers • Nginx • MySQL**, có CPU/RAM/mạng theo container, yêu cầu và kết nối Nginx, trạng thái và truy vấn MySQL. Đăng nhập bằng `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD` trong `.env`.

```promql
up
mysql_up
nginx_up
sum by (container_label_com_docker_compose_service) (rate(container_cpu_usage_seconds_total{container_label_com_docker_compose_project="recipe"}[2m])) * 100
```

cAdvisor là ngoại lệ chạy root để đọc cgroups và metadata Docker/containerd. Các mount host đặt chỉ đọc, không bật privileged và không publish cổng cAdvisor. Socket Unix gắn `:ro` vẫn có khả năng gọi API runtime; chỉ sử dụng collector đáng tin cậy trên máy lab. Database, ứng dụng và các dịch vụ thông thường chạy non-root.
