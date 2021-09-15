from flask import redirect,render_template,request,session
from functools import wraps

def apology(messege):
    
    return render_template("apology.html",messege=messege)


    

#ログイン画面を経由するようにする
def login_required(f):
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
    
