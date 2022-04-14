# (C) Lage Bonde, 10/4 2022
from flask import *
from xml.etree.ElementTree import parse
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.secret_key = 'hjudioubgjkn'

def UserName(post):
	if "account" in session and len(session['account']) > 0:
		return "<div class='user'>"+session['account']+"</div>"
	
	def findName(name):
		accounts = parse('accounts.xml').getroot()
		for user in accounts:
			if user.attrib['name'] == name:
				return user
		return -1
	try:
		# Create account
		user = request.form['user']
		pass_ = request.form['pass']
		
		if findName(user) == -1:
			userElement = ET.Element('user')
			
			userElement.attrib['name'] = user
			userElement.attrib['password'] = pass_
			
			accounts = parse('accounts.xml').getroot()
			accounts.append(userElement)
			
			# Save
			strRoot = ET.tostring(accounts).decode()
			open('accounts.xml', "w").write(strRoot)
		else:
			# Try to login
			account = findName(user)
			if account.attrib['name'] == user and account.attrib['password'] == pass_:
				session['account'] = user
			else:
				return "<div class='user'>could not sign in</div>"
		
		return "<div class='user'>"+session['account']+"</div>" #session['account']
		
	except KeyError: return "<div class='user'>not logged in</div>"

@app.route("/",methods=['GET','POST'])
def home():
	def searchResult(search,threadText):
		for word in search.split(' '):
			if word.upper() in threadText.upper(): # Compare with upper case letters
				return True
		return False
		
	try:
		root = parse('postThreads.xml').getroot()
		search = str(request.args['search'])
		findings = []
		
		for thread in range(len(root)):
			threadText = ""
			for message in root[thread]:
				threadText += message.text
			if searchResult(search,threadText):
				findings.append(thread)
		
		output = "<table class='search'>"
		for find in findings:
			output += "<tr><td><a href='thread?post=" + str(find) + "'>" + root[find][0].text + "</a></td><td>" + str(len(root[find])-1) + ' reply(-ies)</td></tr>'
		output += "</table>"
	except KeyError:
		output = ""
		try:
			if request.args['logout'] == 'yes': # test if it exists
				session['account'] = ""
				return redirect('./')
			
		except KeyError: output = ""
	return render_template("menu.html")+render_template("home.html") + output+UserName(request.form)




@app.route('/newThread', methods=['GET','POST'])
def newThread():
	root = parse('postThreads.xml').getroot() # Prepare xml tree
	thread = ET.Element('thread')
	root.append(thread) # Add thread
	
	# Save
	strRoot = ET.tostring(root).decode()
	open('postThreads.xml', "w").write(strRoot)
	
	return redirect('thread?post='+str(len(root.findall('thread'))-1)) # Open as thread



@app.route("/thread", methods=['GET','POST'])
def thread():
	def options():
		root = parse('accounts.xml').getroot()
		
		output = ""
		for account in root:
			if account.attrib['name'] != session['account']:
				output += "<option>"+account.attrib['name']+"</option>"
		return output
	
	root = parse('postThreads.xml').getroot() # Prepare xml tree
	
	try: thread = root[int(request.args['post'])] # Pic post thread from GET
	except IndexError: return redirect('/notfound')
	
	if not thread.attrib['only'] == "" and not session['account'] in thread.attrib['only'].split(','): # Not public && Not allowed to view?
		return render_template("menu.html")+"You are not allowed to view this post thread."+UserName(request.form)
	
	# Generate list with threads
	output = "<table class='threads'>"
	for message in thread:
		output += "<tr><td>"+message.attrib['from']+"</td><td>"+message.text + "</td></tr>"
	output += "</tr></table>"
	
	if session['account'] != "": # logged in
		try:
			element = ET.Element('message')
			element.text = request.form['comment'] # May crash
			element.attrib['from'] = session['account'] # May crash?????
			
			if request.form.get('public') != 'on':
				thread.attrib['only'] = session['account']+","+",".join(request.form.getlist('select'))
			else:
				thread.attrib['only'] = ""
			
			thread.append(element)
			# Save
			strRoot = ET.tostring(root).decode()
			open('postThreads.xml', "w").write(strRoot)
			
			return redirect('thread?post='+str(request.args['post']))
		except KeyError:
			#return "of the sith"
			comment = ""
		
	return render_template("menu.html")+render_template(
		"thread.html",
		threads=output,
		post=request.args['post'],
		options=options()
	)+UserName(request.form)
	
@app.route('/notfound',methods=['GET','POST'])
def notfound():
	return render_template("menu.html")+'<h1>Not found</h1><p>Hm... We have trouble with finding the post thread you\'re looking for.</p><button onclick="history.back()">Go back</button>'+UserName(request.form)

@app.route('/resources',methods=['GET','POST'])
def resources():
	return render_template("menu.html")+render_template("resources.html")+UserName(request.form)

@app.route('/contact',methods=['GET','POST'])
def contact():
	return render_template("menu.html")+render_template("contact.html")+UserName(request.form)

if __name__ == "__main__":
	app.run(debug=True, port=8080, host="0.0.0.0")
	
	
'''
Things to do:
	Search
done	Create
	Thread account

'''
