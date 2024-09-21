from flask import render_template, Blueprint, request, redirect, session
from hashlib import sha256
import datetime
from datetime import datetime as dt
from zoneinfo import ZoneInfo as zi
from bson import ObjectId

def constructBlueprint(dbClient):    
    db_name = "revision_app"     
    topic = "topic"
    subject = "subject"
    do_on = "do_on"
    last_done = "last_done"
    times_done = "times_done"
    user = "user"
    offset="t_offset"
    disp_date = "%d %B, %Y"
    today_tbd = "today-tbd"
    today_done = "today-done"

    page = Blueprint('page', __name__, template_folder="templates", static_folder="static" )

    @page.route('/login', methods = ["GET", "POST"])
    def login():        
        if session.get("uname"):
            return redirect("/")
        if request.method == "POST":            
            try:                
                data = request.get_json()
                t_offset = data.get(offset)                
                user = data["user"]
                pwd = sha256(data["password"].encode()).hexdigest()                
                ret = dbClient[db_name]["users"].find_one({"user":user, "password":pwd})                
                if ret:                                        
                    dbClient[db_name]["users"].update_one({"user":user},{"$set": {offset: t_offset}})
                    session["uname"] = user
                    return redirect("/")
                else:
                    return redirect("/login", code= 404)
            except Exception as e:
                print("Error Reading the Username or Password", e)
        return render_template("login.html")
    

    
    @page.route('/register', methods = ["GET", "POST"])
    def register():
        if request.method == "POST":            
            try:
                data = request.get_json()
                uname = data[user]
                pwd = sha256(data["password"].encode()).hexdigest()
                ret = dbClient[db_name]["users"].find_one({user:uname})                
                if ret:                    
                    return redirect("/register", code=409)
                else:
                    dbClient[db_name]["users"].insert_one({user:uname, "password": pwd})
                    return redirect("/login")
                
            except Exception as e:
                print("Error Reading the Username or Password", e)
        return render_template("register.html", data = None)
    


    @page.route('/stats', methods=['GET'])
    def stats():
        logged_user= session.get("uname")        
        if not logged_user:
            print("No one is logged in")
            return redirect('/login')
        else:
            t_offset = dbClient[db_name]["users"].find_one({user: logged_user})[offset]
            today = dt.combine(dt.now()-datetime.timedelta(minutes=t_offset), datetime.time.min)
            query_data = dbClient[db_name]["topics"].find({user: logged_user}).sort({subject:1, times_done:1})
            ret_data = {}
            for item in query_data:
                print(item[topic])
                sub = item[subject]
                top = item[topic]
                do = item[do_on]
                td = item[times_done]
                if sub in ret_data:
                    ret_data[sub].append([top, do, td])
                    ret_data[sub][0]+= int(do>today)
                    ret_data[sub][1]+=1
                else:
                    ret_data[sub] = [int(do>today),1,[top, do, td]]  
            return render_template("stats.html", data = ret_data)        


    @page.route('/add-topics',  methods=['GET', 'POST'])
    def todo():
        if not session.get("uname"):            
            session.clear()
            return redirect("/login")
        if request.method == "POST":        
            try:
                uname = session.get("uname")
                t_offset = dbClient[db_name]["users"].find_one({user: uname})[offset]
                data = request.get_json()
                server_data = []
                for sub_top in data:
                    d={}
                    d[topic] = sub_top[topic]
                    d[subject] = sub_top[subject].capitalize()
                    d[do_on] = dt.combine(dt.now()-datetime.timedelta(minutes=t_offset), datetime.time.min)
                    d[last_done] = dt.min
                    d[times_done] = 0
                    d[user] = uname
                    server_data.append(d)                
                dbClient[db_name]["topics"].insert_many(server_data)
            except Exception as e:            
                print("Error while adding Topics, ", e)
            return render_template('add-topics.html', data= server_data)
        return render_template('add-topics.html')


    @page.route('/<action>/<id>', methods=['GET'])
    def done(action, id):
        logged_user= session.get("uname")        
        if not logged_user:
            print("No one is logged in")
            return redirect('/login')
        else:
            t_offset = dbClient[db_name]["users"].find_one({user: logged_user})[offset]
            if action == "done":
                topic = dbClient[db_name]["topics"].find_one({"_id": ObjectId(id)})
                changes = {}
                changes[last_done] = dt.combine(dt.now()-datetime.timedelta(minutes=t_offset), datetime.time.min)
                changes[do_on] = changes[last_done]+datetime.timedelta(days=7*(1<<topic[times_done]))
                changes[times_done] = topic[times_done]+1
                dbClient[db_name]["topics"].update_one({"_id":ObjectId(id)},{"$set": changes})
            elif action == "undo":
                topic = dbClient[db_name]["topics"].find_one({"_id": ObjectId(id)})
                changes = {}
                changes[last_done] = dt.min
                changes[times_done] = topic[times_done]-1
                changes[do_on] = topic[do_on]-datetime.timedelta(days=7*(1<<changes[times_done]))                
                dbClient[db_name]["topics"].update_one({"_id":ObjectId(id)},{"$set": changes})
            else:
                print("Wrong action")
        return render_template('home.html')


    @page.route('/')
    def home():        
        logged_user= session.get("uname")        
        if not logged_user:
            print("No one is logged in")
        else:
            print(logged_user, "is logged in")                        
            t_offset = dbClient[db_name]["users"].find_one({user: logged_user})[offset]            
            query_res1 = dbClient[db_name]["topics"].find({user:logged_user, do_on: {"$lte": dt.combine(dt.now()-datetime.timedelta(minutes=t_offset), datetime.time.min)}}).sort(subject)
            query_res2 = dbClient[db_name]["topics"].find({user:logged_user, last_done: dt.combine(dt.now()-datetime.timedelta(minutes=t_offset), datetime.time.min)}).sort(subject)
            resp_data = {today_tbd : [], today_done : []}
            for x in query_res1:
                cur = (x[subject], x[topic], x[times_done], x[do_on].astimezone(zi("Asia/Kolkata")).strftime(disp_date), x['_id'])
                resp_data[today_tbd].append(cur)                
            for x in query_res2:
                cur = (x[subject], x[topic], x[times_done], x[do_on].astimezone(zi("Asia/Kolkata")).strftime(disp_date), x['_id'])
                resp_data[today_done].append(cur)                
            return render_template('home.html', data=resp_data)
        return render_template('home.html', data = None)
        

    @page.route('/header')
    def header():
        logged_user= session.get("uname")
        data = {"uname": logged_user}
        return render_template('header.html', data=data)
    
    @page.route('/logout')
    def logout():        
        session.clear()
        return redirect("/")
    
    return page