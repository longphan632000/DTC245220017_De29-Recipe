# Các truy vấn LogQL của Recipe

Mở Grafana → Explore → chọn datasource **Loki**. Chọn thời gian Last 1 hour. Hoặc mở dashboard **Recipe — Logs và LogQL** đã được provision sẵn.

## Toàn bộ access log Nginx

```logql
{job="nginx"}
```

Mỗi dòng JSON có thời điểm, phương thức, URI, mã HTTP, số byte và thời gian xử lý. Nginx ghi `$uri` để tránh đưa query string chứa dữ liệu người dùng vào log tập trung.

## Những yêu cầu trả lỗi HTTP

```logql
{job="nginx"} | json | status >= 400
```

Tạo minh chứng bằng cách truy cập `http://127.0.0.1:8088/?recipe=999999`; ứng dụng trả 404. Truy cập `/.env` nhận 403. Hai trường hợp phải xuất hiện trong kết quả truy vấn.

## Đăng nhập thành công vào ứng dụng

```logql
{job="app"} |= "login_success"
```

Ứng dụng ghi tên sự kiện, thời điểm và ID người dùng; không ghi mật khẩu, CSRF token hay cookie. Có thể đổi thành `login_failed`, `recipe_saved`, `recipe_archived`, `recipe_restored`.

## Log MySQL

```logql
{job="mysql"}
```

Đọc error log của MySQL để kiểm tra tiến trình khởi động và sự kiện của database.

## Đếm yêu cầu theo mã HTTP trong 5 phút

```logql
sum by (status) (count_over_time({job="nginx"} | json [5m]))
```

File JSON kết quả thực được lưu trong `minh-chung/logql-1.json` đến `logql-4.json` bởi `scripts/verify.py`.
