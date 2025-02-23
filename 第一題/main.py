from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# 使用 SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 假設的用戶資料
fake_user_db = [
    {
        "name":"廖柏睿",
        "username": "liaoborui998513",
        "password": "945396000"
    }
]

# 登入頁面
@app.get("/", response_class=HTMLResponse)
async def get_login_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 註冊邏輯
@app.post("/signup")
async def signup(request: Request, name: str = Form(), username: str = Form(), password: str = Form()):
    # 檢查帳號是否已存在
    if any(user["username"] == username for user in fake_user_db):
        return RedirectResponse(url=f"/error?message=帳號已存在", status_code=303)

    # 創建新用戶並加入資料庫
    fake_user_db.append({"name": name, "username": username, "password": password})

    # 註冊成功，跳轉到登入頁面
    return RedirectResponse(url="/", status_code=303)

# 登入邏輯
@app.post("/signin")
async def signin(request: Request, username: str = Form(), password: str = Form()):
    # 驗證帳號和密碼
    user = next((user for user in fake_user_db if user["username"] == username and user["password"] == password), None)

    if user is None:
        return RedirectResponse(url=f"/error?message=帳號或密碼錯誤", status_code=303)

    # 登入成功，將用戶名保存至 session
    request.session["user"] = username
    return RedirectResponse(url="/member", status_code=303)

# 會員頁面
@app.get("/member", response_class=HTMLResponse)
async def member_page(request: Request):
    username = request.session.get("user")  # 從 session 獲得登入的 username
    
    if not username:
        return RedirectResponse(url="/", status_code=303)  # 若沒登入則跳回登入頁面

    # 根據 username 查找對應的 user
    user = next((user for user in fake_user_db if user["username"] == username), None)

    if not user:
        return RedirectResponse(url="/", status_code=303)  # 如果找不到對應用戶，跳回登入頁面

    # 傳遞 user['name'] 和 user['username'] 到模板
    return templates.TemplateResponse("member.html", {
        "request": request, 
        "username": username, 
        "name": user["name"]
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
