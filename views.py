from flask import render_template, Blueprint, request, redirect
from collections import defaultdict
import datetime
import json
page = Blueprint('page', __name__, template_folder="templates", static_folder="static")

@page.route('/stats.html', methods=['GET'])
def stats():
    try:
         disp_date = "%d %B, %Y"
         with open('config.json', 'r') as file:                        
            config_data = json.load(file)
            subs = defaultdict(lambda: [])            

            today_done= {}
            if tdn in config_data:                
                for x,y in config_data[tdn].items():
                    today_done[x]=y

            if topics in config_data:                
                for x, y in config_data[topics].items():                    
                    subs[y['subject']].append((x, 
                                               datetime.datetime.strftime(datetime.datetime.strptime(today_done[x][to_do] if x in today_done else y[to_do],date_fmt), disp_date), 
                                               y[timesDone] + (x in today_done)))                    
            else:
                raise Exception('Topics Not Found')            
            for x in subs:
                subs[x].sort(key=lambda a: a[2])                                                                
                n=len(list(filter(lambda a: datetime.datetime.strptime(a[1],disp_date)>datetime.datetime.today(), subs[x])))                
                d=len(subs[x])                
                subs[x].append(n*100/d if d else "NA")                
    except: 
        subs = None    
    return render_template('stats.html', data=subs)


@page.route('/add-topics.html',  methods=['GET', 'POST'])
def todo():
    if request.method == 'POST':
        data = request.get_json()  # Get data from request in JSON format
        try:
            with open('config.json', 'r') as file:            
                config_data = json.load(file)
                config_data['topics'].update(data['topics'])  # Update the value of the JSON data
        except:
            config_data = data
        with open('config.json', 'w+') as file:                                        
            json.dump(config_data, file)  # Save updated data to file in JSON format  
    return render_template('add-topics.html')    


@page.route('/<action>/<topic>', methods=['GET'])
def done(action, topic):
    try:        
        with open('config.json', 'r') as file:                        
            config_data = json.load(file)
        if tdn not in config_data: config_data[tdn] = {}
        if tbd not in config_data: config_data[tbd] = {}
        if action == "done":
            nd = (1<<config_data[tbd][topic][timesDone]) * 7 - 1
            config_data[tbd][topic][to_do] = (datetime.datetime.today()+datetime.timedelta(days=nd)).strftime(date_fmt)
            config_data[tbd][topic][timesDone]+=1            
            config_data[tdn][topic]=config_data[tbd][topic]
            config_data[tbd].pop(topic)      
        elif action == "undo":
            config_data[tdn][topic][timesDone]-=1
            pd = (1<<config_data[tdn][topic][timesDone]) * 7 - 1
            config_data[tdn][topic][to_do] = (datetime.datetime.today()+datetime.timedelta(days=pd)).strftime(date_fmt)
            config_data[tbd][topic]=config_data[tdn][topic]
            config_data[tdn].pop(topic) 
        else:
            print("Wrong Action")
    except: pass

    with open('config.json', 'w+') as file:        
        json.dump(config_data, file)  # Save updated data to file in JSON format
    return redirect('/home.html')


@page.route('/')
@page.route('/home.html')
def home():
    today = datetime.datetime.today().strftime(date_fmt)
    try:
        with open('config.json', 'r') as file:                        
            config_data = json.load(file)
            nextDay=False
            if t not in config_data or config_data[t] != today:
                config_data[t]=today
                config_data[tbd] = {}
                if tdn not in config_data: config_data[tdn] = {}
                nextDay=True
            recalc(config_data, nextDay)
    except:            
        config_data = {tbd:{}, t:""}
    with open('config.json', 'w+') as file:        
        json.dump(config_data, file)  # Save updated data to file in JSON format  

    response = {tbd:[], tdn:[]} 
    if tbd in config_data:
        for x, y in config_data[tbd].items():
            response[tbd].append((y['subject'],x, y[timesDone], y[to_do]))    
    if tdn in config_data:
        for x, y in config_data[tdn].items():
            response[tdn].append((y['subject'],x, y[timesDone], y[to_do]))
    
    response[tbd].sort()
    response[tdn].sort()
    return render_template('home.html', data=response)    


date_fmt = "%Y-%m-%d"
t = "today"
tbd = "today-tbd"
tdn = "today-done"
topics = "topics"
to_do = "todo"
timesDone = "timesDone"

def recalc(d, nextDay):
    today= datetime.datetime.today()
    td, dn={}, {}
    for x, y in d[topics].items():
        pdate=datetime.datetime.strptime(y[to_do],date_fmt)
        if pdate<=today and x not in d[tdn]:
            td[x] = y
        
    d[tbd].update(td)
    if not nextDay: return     
    d[topics].update(d[tdn])
    d[tdn].clear()

