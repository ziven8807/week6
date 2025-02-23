# MySQL 用戶資料表設計

`users` Table 來儲存用戶資料：
CREATE TABLE users (
id INT AUTO_INCREMENT PRIMARY KEY, -- ID，作為主鍵
name VARCHAR(100) NOT NULL, -- 用戶姓名
username VARCHAR(100) NOT NULL UNIQUE, -- 用戶帳號
password VARCHAR(100) NOT NULL -- 用戶密碼
);

`messages` Table 來儲存用戶留言內容的相關資訊：
CREATE TABLE messages (
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(100) NOT NULL, -- 與 users Table 中的 username 欄位關聯
name VARCHAR(100) NOT NULL, -- name 欄位來儲存用戶名稱
content TEXT NOT NULL, -- 留言內容
timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 留言時間，默認為當前時間
FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);
