from aiohttp import web
from cryptography import fernet
from aiohttp_session import setup, new_session, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import base64
import sqlite3


def create_session(user_id):
    conn = sqlite3.connect("task_2.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO sessions (user_id)
        VALUES (?)
    """,
        (user_id),
    )
    conn.commit()
    conn.close()


def get_session_by_user(user_id):
    conn = sqlite3.connect("task_2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def delete_session(user_id):
    conn = sqlite3.connect("task_2.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id))
    conn.commit()
    conn.close()


routes = web.RouteTableDef()


@routes.view("/login")
class Login(web.View):
    async def get(self):
        login_form = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Login</title>
            </head>
            <body>
                <h2>Login</h2>
                <form action="/login" method="post"accept-charset="utf-8" enctype="application/x-www-form-urlencoded">
                    <label for="username">Username:</label>
                    <input id="username" type="text" name="username" value="" autofocus>
                    <label for="password">Password:</label>
                    <input id="password" type="password" name="password" value="">
                    <input type="submit" value="Login">
                </form>
            </body>
        </html>
        """

        return web.Response(text=login_form, content_type="text/html")

    async def post(self):
        data = await self.request.post()
        username = data["username"]
        password = data["password"]

        conn = sqlite3.connect("task_2.db")
        c = conn.cursor()
        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?", (username, password)
        )
        user = c.fetchone()

        if not user:
            return web.json_response(
                {"message": "Invalid username or password"}, status=401
            )
        elif get_session_by_user(user[0]):
            return web.json_response(
                {"message": "Already logged in with another session"}, status=400
            )
        else:
            session = await new_session(self.request)
            session["user_id"] = user[0]

            create_session(user[0])
            return web.json_response({"message": "Login successful"}, status=200)


@routes.view("/logout")
class Logout(web.View):
    async def get(self):
        logout_form = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Logout</title>
            </head>
            <body>
                <h2>Logout</h2>
                <form action="/logout" method="post" accept-charset="utf-8" enctype="application/x-www-form-urlencoded">
                    <input type="submit" value="Logout">
                </form>
            </body>
        </html>
        """

        return web.Response(text=logout_form, content_type="text/html")

    async def post(self):
        session = await get_session(self.request)

        if session["user_id"]:
            delete_session(session["user_id"])
            return web.json_response({"message": "Logout successful"}, status=200)
        else:
            return web.json_response(
                {"message": "No active session to log out from."}, status=400
            )


@routes.get("/")
async def index(request):
    page_html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Home</title>
            </head>
            <body>
                <h2>Login</h2>
                <a href="/login"><button>Login</button></a>
                <h2>Logout</h2>
                <form action="/logout" method="post" accept-charset="utf-8" enctype="application/x-www-form-urlencoded">
                    <input type="submit" value="Logout">
                </form>
            </body>
        </html>
        """
    return web.Response(text=page_html, content_type="text/html")


app = web.Application()
fernet_key = fernet.Fernet.generate_key()
secret_key = base64.urlsafe_b64decode(fernet_key)
setup(app, EncryptedCookieStorage(secret_key))
app.add_routes(routes)
web.run_app(app)
