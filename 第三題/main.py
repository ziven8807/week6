from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import mysql.connector
import os


app = FastAPI(debug=True)


# 使用 SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# MySQL 資料庫配置
def get_db_connection():

    return mysql.connector.connect(
        host="localhost",        # MySQL 伺服器地址
        user="root",             # 使用 'root' 用戶
        password=os.getenv("MYSQL_PASSWORD"),  # MySQL 密碼（替換為實際的 root 密碼，但要從環境變數讀取密碼 ）
        database="website"       # 資料庫名稱
    )

# 登入頁面
@app.get("/", response_class=HTMLResponse)
async def get_login_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 註冊邏輯
@app.post("/signup")
async def signup(request: Request, name: str = Form(), username: str = Form(), password: str = Form()):
    # 連接資料庫
    db = get_db_connection()
    cursor = db.cursor()

    # 檢查帳號是否已存在
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        cursor.close()
        db.close()
        return RedirectResponse(url=f"/error?message=帳號已存在", status_code=303)

    # 創建新用戶並插入資料庫
    cursor.execute("INSERT INTO users (name, username, password) VALUES (%s, %s, %s)", (name, username, password))
    db.commit()

    cursor.close()
    db.close()

    # 註冊成功，跳轉到登入頁面
    return RedirectResponse(url="/", status_code=303)

# 登入邏輯
@app.post("/signin")
async def signin(request: Request, username: str = Form(), password: str = Form()):
    # 連接資料庫
    db = get_db_connection()
    cursor = db.cursor()

    # 驗證帳號和密碼
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        db.close()
        return RedirectResponse(url=f"/error?message=Username or password is not correct", status_code=303)

    # 登入成功，將用戶名保存至 session
    request.session["user"] = username

    cursor.close()
    db.close()

    return RedirectResponse(url="/member", status_code=303)

# 會員頁面
@app.get("/member", response_class=HTMLResponse)
async def member_page(request: Request):
    username = request.session.get("user")  # 從 session 獲得登入的 username
    
    if not username:
        return RedirectResponse(url="/", status_code=303)  # 若沒登入則跳回登入頁面

    # 連接資料庫
    db = get_db_connection()
    cursor = db.cursor()

    # 根據 username 查找對應的 user
    cursor.execute("SELECT name, username FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        db.close()
        return RedirectResponse(url="/", status_code=303)  # 如果找不到對應用戶，跳回登入頁面

    cursor.close()
    db.close()

    # 傳遞用戶的 name 和 username 到模板
    return templates.TemplateResponse("member.html", {
        "request": request, 
        "username": user[1],  # 顯示 username
        "name": user[0]       # 顯示 name
    })

# 登入錯誤頁面
@app.get("/error", response_class=HTMLResponse)
async def error_page(request: Request, message: str):
    return templates.TemplateResponse("signinError.html", {"request": request, "message": message})

# 登出處理
@app.get("/signout")
async def signout(request: Request):
    request.session.clear()
    response = RedirectResponse(url="/")
    response.delete_cookie("session")
    response.set_cookie("session", "", expires=0)  # 強制設置過期時間
    return response




