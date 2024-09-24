from flask import render_template, Blueprint, request, redirect, session
from mysql.connector.connection_cext import CMySQLConnection
from hashlib import sha256
import datetime
from datetime import datetime as dt
from zoneinfo import ZoneInfo as zi

def constructBlueprint(dbClient: CMySQLConnection):   
    db_name = "revision_app"
    user_table_name = "users"
    topic_table_name = "topics"
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
        checkConnection()
        logged_user= session.get("uname")                
        if logged_user:
            return redirect("/")
        elif request.method == "POST":
            session.clear()
            try:          
                cur=dbClient.cursor()      
                data = request.get_json()
                t_offset = data.get(offset)                
                logged_user = data["user"]
                pwd = sha256(data["password"].encode()).hexdigest()                
                cur.execute(f"select user from {user_table_name} where user =%s and password =%s", (logged_user, pwd))
                ret = cur.fetchone()
                if ret:
                    cur.execute(f"update {user_table_name} set t_offset = %s where user =%s", (t_offset, logged_user))
                    dbClient.commit()
                    session["uname"] = logged_user
                    return redirect("/")
                else:
                    return redirect("/login", code= 404)
            except Exception as e:
                print("Error Reading the Username or Password", e)
            finally:
                cur.close()
        return render_template("login.html")
    

    
    @page.route('/register', methods = ["GET", "POST"])
    def register():
        checkConnection()
        logged_user= session.get("uname")                
        if logged_user:
            return redirect("/")
        elif request.method == "POST":
            session.clear()
            try:
                cur=dbClient.cursor()
                data = request.get_json()
                uname = data[user]
                pwd = sha256(data["password"].encode()).hexdigest()
                cur.execute(f"select user from {user_table_name} where user =%s", (uname,))
                ret = cur.fetchone()
                if ret:                    
                    return redirect("/register", code=409)
                else:                    
                    cur.execute(f"insert into {user_table_name}(user, password) values(%s,%s)", (uname, pwd))                    
                    dbClient.commit()
                    return redirect("/login")
                
            except Exception as e:
                print("Error Reading the Username or Password", e)
            finally:
                cur.close()
        return render_template("register.html", data = None)
    


    @page.route('/stats', methods=['GET'])
    def stats():
        checkConnection()
        logged_user= session.get("uname")        
        if not logged_user:
            print("No one is logged in")
            session.clear()
            return redirect('/login')
        else:
            ret_data = {}
            try:                
                cur=dbClient.cursor()         
                cur.execute(f"select t_offset from {user_table_name} where user=%s",(logged_user,))
                t_offset = cur.fetchone()[0]
                today = (dt.now(datetime.timezone.utc)-datetime.timedelta(minutes=t_offset)).date()

                cur.execute = cur.execute(f"select {subject}, {topic}, {times_done}, {do_on} from {topic_table_name} where user = %s order by {subject}, {times_done}",(logged_user,))
                query_data = cur.fetchall()
                for item in query_data:                    
                    sub, top, td, do = item                    
                    if sub in ret_data:
                        ret_data[sub].append([top, do, td])
                        ret_data[sub][0]+= int(do>today)
                        ret_data[sub][1]+=1
                    else:
                        ret_data[sub] = [int(do>today),1,[top, do, td]]  
            except Exception as e:
                print("Failed to load Stats, ",e)                
            return render_template("stats.html", data = ret_data)        


    @page.route('/add-topics',  methods=['GET', 'POST'])
    def add_topics():
        checkConnection()
        logged_user= session.get("uname")        
        if not logged_user:
            print("No one is logged in")
            session.clear()
            return redirect("/login")
        elif request.method == "POST":        
            try:       
                cur=dbClient.cursor()         
                cur.execute(f"select t_offset from {user_table_name} where user=%s",(logged_user,))
                t_offset = cur.fetchone()[0]            
                data = request.get_json()
                server_data = []
                for sub_top in data:
                    d=(sub_top[topic], 
                       sub_top[subject].capitalize(), 
                       dt.combine(dt.now(datetime.timezone.utc)-datetime.timedelta(minutes=t_offset), datetime.time.min), 
                       dt.min,
                       0, 
                       logged_user)
                    server_data.append(d)                
                cur.executemany(f"insert into {topic_table_name}({topic}, {subject}, {do_on}, {last_done}, {times_done}, {user}) values(%s, %s, %s, %s, %s, %s)", server_data)
                dbClient.commit()
            except Exception as e:            
                print("Error while adding Topics, ", e)
            finally:
                cur.close()
            return render_template('add-topics.html', data= server_data)
        return render_template('add-topics.html')


    @page.route('/<action>/<id>', methods=['GET'])
    def done(action, id):
        checkConnection()
        logged_user= session.get("uname")        
        if not logged_user:
            print("No one is logged in")
            session.clear()
            return redirect('/login')
        else:
            try:
                cur=dbClient.cursor()
                cur.execute(f"select t_offset from {user_table_name} where user=%s",(logged_user,))
                t_offset = cur.fetchone()[0]
                today = (dt.now(datetime.timezone.utc)-datetime.timedelta(minutes=t_offset)).date()
                if action == "done":
                    cur.execute(f"select {subject}, {topic}, {times_done}, {do_on}, {last_done} from {topic_table_name} where id=%s",(id,))
                    ctopic = cur.fetchone()
                    if not ctopic: RuntimeError("No result found for the query!")
                    changes={}
                    changes[last_done] = today
                    changes[do_on] = today+datetime.timedelta(days=7*(1<<ctopic[2]))
                    changes[times_done] = ctopic[2]+1
                    change_keys = f"{last_done} = %s, {do_on} = %s, {times_done} = %s"
                    change_values = (changes[last_done], changes[do_on], changes[times_done], id)
                    print(change_values)
                    cur.execute(f"update {topic_table_name} set {change_keys} where id=%s", change_values)
                    dbClient.commit()
                elif action == "undo":
                    cur.execute(f"select {subject}, {topic}, {times_done}, {do_on}, {last_done} from {topic_table_name} where id=%s",(id,))
                    ctopic = cur.fetchone()
                    if not ctopic: RuntimeError("No result found for the query!")
                    changes={}
                    changes[last_done] = dt.min
                    changes[times_done] = ctopic[2]-1
                    changes[do_on] = today
                    change_keys = f"{last_done} = %s, {do_on} = %s, {times_done} = %s"
                    change_values = (changes[last_done], changes[do_on], changes[times_done], id)
                    cur.execute(f"update {topic_table_name} set {change_keys} where id=%s", change_values)
                    dbClient.commit()
                else:
                    print("Wrong action")
            except Exception as e: 
                print("Failed to perform the action, ",e)
            finally:
                cur.close()
        return render_template('home.html')


    @page.route('/')
    def home():        
        checkConnection()
        logged_user= session.get("uname")        
        if not logged_user:
            print("No one is logged in")
            session.clear()
        else:
            print(logged_user, "is logged in")
            try:
                cur=dbClient.cursor()
                cur.execute("select t_offset from "+user_table_name+" where user=%s",(logged_user,))
                t_offset = cur.fetchone()[0]
            except Exception as e:
                print("Timezone offset not foound , ",e)
                t_offset = 0
            finally:
                cur.close()

            today = (dt.now(datetime.timezone.utc)-datetime.timedelta(minutes=t_offset)).date()
            resp_data = {today_tbd : [], today_done : []}            

            try:            
                cur=dbClient.cursor()
                cur.execute = cur.execute(f"select {subject}, {topic}, {times_done}, {do_on}, id from {topic_table_name} where user = %s and do_on <= %s order by {subject}, {do_on}",(logged_user, today))
                query_res1 = cur.fetchall()                
                for x in query_res1:
                    c = (x[0], x[1], x[2], dt.strftime(x[3], disp_date), x[4])
                    resp_data[today_tbd].append(c)
            except Exception as e:
                print("Error in fetching todo data, ",e)
            finally:
                cur.close()

            try:
                cur=dbClient.cursor()
                cur.execute = cur.execute(f"select {subject}, {topic}, {times_done}, {do_on}, id from {topic_table_name} where user = %s and last_done = %s order by {subject}, {do_on}",(logged_user, today))
                query_res2 = cur.fetchall()                                
                for x in query_res2:
                    c = (x[0], x[1], x[2], dt.strftime(x[3], disp_date), x[4])
                    resp_data[today_done].append(c)     
            except Exception as e:
                print("Error in fetching done data, ",e)
            finally:
                cur.close()
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
    
    def checkConnection():
        if not dbClient.is_connected():
            print("Re-establishing connection")
            dbClient.connect(database = db_name)
            
    return page    
