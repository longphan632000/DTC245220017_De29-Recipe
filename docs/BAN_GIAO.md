# Bàn giao Đề 29 Recipe

Dự án trên máy Ubuntu: `/home/longphan/DTC245220017-De 29`. Đường dẫn `/home/longphan/recipe-stack` trỏ tới cùng dự án. Repository: https://github.com/longphan632000/DTC245220017_De29-Recipe.

## Mở hệ thống

| Nội dung | Địa chỉ trên Ubuntu | Tài khoản trong .env |
| --- | --- | --- |
| Website | http://127.0.0.1:8088/ | Không cần đăng nhập |
| Quản trị công thức | http://127.0.0.1:8088/?page=login | APP_ADMIN_USER / APP_ADMIN_PASSWORD |
| phpMyAdmin | http://127.0.0.1:8081/ | MYSQL_USER / MYSQL_PASSWORD, server db |
| Grafana | http://127.0.0.1:3000/ | GRAFANA_ADMIN_USER / GRAFANA_ADMIN_PASSWORD |
| Prometheus Targets | http://127.0.0.1:9090/targets | Không cần đăng nhập |

Mở `.env` trên máy để xem mật khẩu; file này không được đưa lên GitHub. Hai tài khoản quản trị ứng dụng và Grafana hiện có tên `recipe_admin` nhưng dùng mật khẩu riêng.

## Khởi động lại và kiểm tra

```bash
cd -- "/home/longphan/DTC245220017-De 29"
docker compose up -d
docker compose ps -a
python3 scripts/verify.py
```

Khi cài từ máy mới, chạy `python3 scripts/setup.py` theo README để tạo secret, build image, nạp schema và tạo tài khoản. Nếu Docker chưa chạy sau khi mở Ubuntu, khởi động Docker trước. Không dùng `docker compose down -v` khi cần giữ dữ liệu.

## Kết quả đã ghi nhận

- 11 dịch vụ Docker Compose đang chạy.
- 51/51 kiểm tra chức năng, database, bảo mật và hệ thống đạt; kết quả tại `minh-chung/verification.*`.
- 8/8 kiểm tra cài mới độc lập từ GitHub đạt, với volume mới và cổng khác; kết quả tại `minh-chung/reproducibility.json`.
- Prometheus có sáu target UP; Grafana có hai datasource và hai dashboard tự provision.
- Bốn truy vấn LogQL có dữ liệu thực; ảnh minh chứng và JSON nằm trong `minh-chung/`.
- Grafana được cấp giới hạn RAM 768 MiB và giảm các plugin không dùng để phục vụ dashboard ổn định trên máy lab.

## Trình tự demo

1. Mở repo và giải thích ba commit triển khai: ứng dụng/Nginx, monitoring, logging/hardening. Commit tài liệu bổ sung báo cáo và minh chứng.
2. Mở website, tìm “me chín”, lọc danh mục và xem nguyên liệu/cách nấu.
3. Đăng nhập quản trị, thêm hoặc sửa một công thức; minh họa lưu trữ và khôi phục.
4. Mở phpMyAdmin để đối chiếu dữ liệu của năm bảng ứng dụng.
5. Mở Prometheus Targets và dashboard Grafana metrics; giải thích CPU/RAM, Nginx và MySQL.
6. Mở dashboard log hoặc Explore, chọn Loki và chạy truy vấn trong `docs/LOGQL.md`.
7. Chỉ ra cấu hình hardening và kết quả kiểm thử.
8. Trình bày `scripts/backup.py` và cách giữ volume khi dừng hệ thống.

## Báo cáo và dữ liệu được giữ lại

Báo cáo Word/PDF có 16 trang nội dung, sơ đồ kiến trúc, mô hình dữ liệu và ảnh chụp giao diện thực tế. Sinh viên tự bổ sung bìa.

Bản này dùng PHP/MySQL theo khung repo mẫu, thay cho WordPress đã cài thử trước đó. Các bảng WordPress cũ và volume cũ được giữ để bảo toàn dữ liệu; ứng dụng Recipe không sử dụng chúng. Cài mới từ GitHub chỉ tạo năm bảng ứng dụng. Bản sao cấu hình/dữ liệu trước khi triển khai nằm ngoài Git tại `/home/longphan/recipe-safety/`.

Bản lab truy cập HTTP qua localhost và có security headers theo phương án đề bài cho phép. Các giới hạn triển khai và ngoại lệ cAdvisor được nêu trong `docs/HARDENING.md` và báo cáo.
