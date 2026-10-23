SET NAMES utf8mb4;
-- Đề 29 Recipe schema. Idempotent and independent of legacy WordPress tables.
CREATE TABLE IF NOT EXISTS categories (id INT PRIMARY KEY, name VARCHAR(80) NOT NULL UNIQUE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS recipes (
 id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255) NOT NULL, description TEXT NOT NULL,
 category_id INT NOT NULL, prep_minutes SMALLINT UNSIGNED NOT NULL DEFAULT 0,
 cook_minutes SMALLINT UNSIGNED NOT NULL DEFAULT 0, servings TINYINT UNSIGNED NOT NULL DEFAULT 2,
 difficulty VARCHAR(20) NOT NULL DEFAULT 'Dễ', illustration VARCHAR(30) NOT NULL DEFAULT 'pho',
 is_deleted BOOLEAN NOT NULL DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 CONSTRAINT fk_category FOREIGN KEY(category_id) REFERENCES categories(id), INDEX idx_category(category_id,is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS ingredients (
 id INT AUTO_INCREMENT PRIMARY KEY, recipe_id INT NOT NULL, name VARCHAR(500) NOT NULL,
 position SMALLINT UNSIGNED NOT NULL, UNIQUE KEY uq_ingredient(recipe_id,position),
 FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS steps (
 id INT AUTO_INCREMENT PRIMARY KEY, recipe_id INT NOT NULL, instruction TEXT NOT NULL,
 position SMALLINT UNSIGNED NOT NULL, UNIQUE KEY uq_step(recipe_id,position),
 FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS users (
 id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(80) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL, role ENUM('admin') NOT NULL DEFAULT 'admin',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT IGNORE INTO categories(id,name) VALUES(1,'Món Việt'),(2,'Bữa nhanh'),(3,'Rau và salad'),(4,'Món ngọt');
INSERT IGNORE INTO recipes(id,title,description,category_id,prep_minutes,cook_minutes,servings,difficulty,illustration) VALUES('1','Phở gà thơm vị nhà','Nước dùng trong ngọt, thịt gà mềm và hương rau thơm cho buổi sáng ấm bụng.','1','20','50','4','Vừa','pho');
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(1,'1 con gà khoảng 1,2 kg',1);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(1,'600 g bánh phở',2);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(1,'1 củ hành tây, 1 nhánh gừng',3);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(1,'2 hoa hồi, 1 thanh quế nhỏ',4);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(1,'Hành lá, rau mùi và chanh',5);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(1,'Muối, nước mắm theo khẩu vị',6);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(1,'Rửa sạch gà, để ráo. Hành tây và gừng nướng sơ rồi làm sạch phần cháy.',1);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(1,'Cho gà vào nồi, đổ nước ngập và đun sôi nhẹ. Hớt bọt, thêm hành gừng, hồi và quế.',2);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(1,'Luộc và kiểm tra phần thịt dày nhất đã chín hoàn toàn. Vớt gà ra, để nguội bớt rồi xé thịt.',3);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(1,'Nêm nước dùng bằng muối và nước mắm. Trụng bánh phở theo hướng dẫn trên bao bì.',4);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(1,'Xếp phở, thịt gà và rau vào bát. Chan nước dùng nóng, thêm chanh tùy khẩu vị.',5);
INSERT IGNORE INTO recipes(id,title,description,category_id,prep_minutes,cook_minutes,servings,difficulty,illustration) VALUES('2','Bánh mì gà xé','Ổ bánh giòn, gà xé đậm đà cùng dưa leo và rau mùi tươi mát.','2','15','15','2','Dễ','banh-mi');
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(2,'2 ổ bánh mì',1);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(2,'250 g thịt ức gà đã nấu chín',2);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(2,'1 quả dưa leo',3);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(2,'1 củ cà rốt nhỏ',4);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(2,'Rau mùi và ớt tùy chọn',5);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(2,'1 thìa nước tương, 1 thìa dầu ăn',6);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(2,'Xé thịt gà đã chín thành sợi vừa ăn. Dưa leo thái lát, cà rốt bào sợi.',1);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(2,'Đảo gà với dầu ăn và nước tương trong 3–5 phút đến khi nóng đều.',2);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(2,'Làm nóng bánh mì trong lò hoặc chảo khô cho vỏ giòn.',3);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(2,'Rạch bánh, xếp gà và rau vào trong. Dùng ngay khi còn nóng.',4);
INSERT IGNORE INTO recipes(id,title,description,category_id,prep_minutes,cook_minutes,servings,difficulty,illustration) VALUES('3','Cơm rang rau củ','Cơm tơi hạt, trứng vàng và rau củ nhiều màu cho bữa ăn nhanh đủ vị.','2','10','15','2','Dễ','com-rang');
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(3,'2 bát cơm nguội bảo quản lạnh đúng cách',1);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(3,'2 quả trứng',2);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(3,'100 g đậu Hà Lan và cà rốt',3);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(3,'2 nhánh hành lá',4);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(3,'1 thìa nước tương',5);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(3,'2 thìa dầu ăn',6);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(3,'Cà rốt thái hạt lựu, hành lá thái nhỏ. Đánh tan trứng.',1);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(3,'Làm nóng chảo với dầu, đảo trứng đến khi vừa chín rồi thêm rau củ.',2);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(3,'Cho cơm vào, đảo tơi và nêm nước tương. Rang đến khi cơm nóng đều hoàn toàn.',3);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(3,'Thêm hành lá, đảo nhanh rồi tắt bếp và dùng ngay.',4);
INSERT IGNORE INTO recipes(id,title,description,category_id,prep_minutes,cook_minutes,servings,difficulty,illustration) VALUES('4','Canh chua cá thanh mát','Vị chua dịu của me, ngọt của cá và rau thơm cho bữa cơm gia đình.','1','20','25','4','Vừa','canh-chua');
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(4,'500 g cá đã làm sạch',1);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(4,'2 quả cà chua',2);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(4,'150 g dứa',3);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(4,'100 g đậu bắp',4);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(4,'1 thìa me chín',5);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(4,'Rau ngổ, hành và nước mắm',6);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(4,'Cá cắt khúc, cà chua bổ múi, dứa cắt lát và đậu bắp cắt vừa ăn.',1);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(4,'Ngâm me với nước nóng rồi lọc bỏ hạt. Đun sôi khoảng 1,2 lít nước.',2);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(4,'Thả cá vào, hớt bọt và nấu đến khi cá chín hoàn toàn.',3);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(4,'Cho cà chua, dứa, nước me và đậu bắp vào nấu thêm vài phút.',4);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(4,'Nêm nước mắm theo khẩu vị, thêm rau thơm rồi tắt bếp.',5);
INSERT IGNORE INTO recipes(id,title,description,category_id,prep_minutes,cook_minutes,servings,difficulty,illustration) VALUES('5','Salad vườn nhà','Rau xanh giòn mát, cà chua và sốt chanh nhẹ nhàng cho một ngày tươi mới.','3','15','0','2','Dễ','salad');
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(5,'150 g xà lách',1);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(5,'150 g cà chua bi',2);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(5,'1 quả dưa leo',3);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(5,'1 thìa nước cốt chanh',4);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(5,'2 thìa dầu ô liu',5);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(5,'Muối và tiêu theo khẩu vị',6);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(5,'Rửa sạch rau bằng nước sạch, để ráo. Thái dưa leo và bổ đôi cà chua.',1);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(5,'Khuấy nước chanh với dầu ô liu, một ít muối và tiêu.',2);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(5,'Trộn rau với sốt ngay trước khi ăn để giữ độ giòn.',3);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(5,'Bày ra đĩa và dùng cùng món chính hoặc bánh mì.',4);
INSERT IGNORE INTO recipes(id,title,description,category_id,prep_minutes,cook_minutes,servings,difficulty,illustration) VALUES('6','Chè đậu xanh cốt dừa','Đậu xanh bùi mềm, nước cốt dừa béo nhẹ và vị ngọt vừa đủ.','4','15','35','4','Dễ','che');
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(6,'200 g đậu xanh cà vỏ',1);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(6,'150 ml nước cốt dừa',2);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(6,'70 g đường hoặc tùy khẩu vị',3);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(6,'1 thìa bột năng',4);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(6,'1 nhúm muối',5);
INSERT IGNORE INTO ingredients(recipe_id,name,position) VALUES(6,'800 ml nước',6);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(6,'Rửa đậu xanh, ngâm khoảng 2 giờ rồi để ráo. Thời gian ngâm chưa tính vào sơ chế.',1);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(6,'Cho đậu và nước vào nồi, nấu lửa vừa đến khi đậu chín mềm.',2);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(6,'Thêm đường và muối, khuấy nhẹ. Hòa bột năng với nước nguội rồi rót từ từ vào chè.',3);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(6,'Đun nước cốt dừa riêng cho nóng, không để sôi quá lâu.',4);
INSERT IGNORE INTO steps(recipe_id,instruction,position) VALUES(6,'Múc chè ra bát, thêm nước cốt dừa. Bảo quản lạnh phần chưa dùng sau khi nguội.',5);
