# Biện pháp hardening đã áp dụng

| Biện pháp | Cấu hình và cách kiểm chứng |
| --- | --- |
| Non-root | App/phpMyAdmin UID 33, Nginx 101, MySQL 999, Grafana 472, Prometheus/exporter 65534, Loki/Promtail 10001. `docker compose exec app id`. |
| Giảm quyền Linux | Mọi service dùng `cap_drop: [ALL]`, `no-new-privileges:true`, không bật `privileged`. |
| Filesystem chỉ đọc | `read_only: true`; chỉ data volume và tmpfs cho phép ghi. |
| Network isolation | `db_net` và `monitoring_net` có `internal: true`; app và exporter chỉ nối những mạng cần dùng. MySQL không publish cổng. |
| Chỉ mở UI trên localhost | Nginx, phpMyAdmin, Grafana, Prometheus và Loki publish với `host_ip=127.0.0.1`. Exporter/cAdvisor/Promtail không publish. |
| Mật khẩu riêng | Script tạo mật khẩu ngẫu nhiên 32 ký tự cho DB, ứng dụng và Grafana. `.env` quyền 600, thư mục `secrets` quyền 700, không vào Git. |
| Phân quyền DB | `recipe_user` chỉ SELECT/INSERT/UPDATE/DELETE trên database ứng dụng. `recipe_exporter` có quyền giám sát chỉ đọc và tối đa 3 kết nối. Root không dùng trong ứng dụng và bị chặn ở phpMyAdmin. |
| Bảo mật ứng dụng | PDO prepared statements, escape HTML, băm mật khẩu, CSRF token, session cookie HttpOnly/SameSite=Strict và đổi session ID sau đăng nhập. |
| Bảo mật Nginx | CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy; ẩn phiên bản; chặn file cấu hình; hạn chế tần suất đăng nhập. |
| Tái lập phiên bản | Base image và các image bên ngoài ghim SHA256 digest; Grafana tắt tự cài/cập nhật plugin khi runtime dùng root filesystem chỉ đọc. |
| Hạn chế tài nguyên | Memory limit theo service; Docker log rotation 10 MB × 3 file; retention Prometheus/Loki 7 ngày. |

## Ngoại lệ cAdvisor

cAdvisor cần root để đọc cgroups và socket Docker/containerd trên host. Collector không chạy privileged, bỏ capabilities, dùng mount chỉ đọc và không mở cổng host. Mount socket `:ro` không biến Docker API thành API chỉ đọc; đây vẫn là thành phần cần được tin cậy. Dashboard giới hạn nhãn hiển thị vào project Recipe. Không thu thập biến môi trường vào nhãn metrics.

## Giới hạn của bản lab

Website dùng HTTP trên loopback với security headers theo lựa chọn mà đề bài cho phép. Khi đưa lên Internet cần HTTPS bằng chứng chỉ tin cậy, quản lý bí mật chuyên dụng và giới hạn truy cập các UI quản trị. Promtail được giữ đúng yêu cầu bài tập, dù Grafana đã kết thúc hỗ trợ Promtail ngày 02/03/2026; hệ thống mới dùng thực tế nên chuyển sang Alloy. Xem [tài liệu chính thức Promtail](https://grafana.com/docs/loki/latest/send-data/promtail/).

Access log nguồn trong named volume chưa có lịch logrotate tự động; cần theo dõi dung lượng nếu chạy lâu dài. Alert rules hiện hiển thị trong Prometheus, chưa cấu hình gửi thông báo tới dịch vụ bên ngoài.
