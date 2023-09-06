import datetime
from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
import csv
import os
import base64

app = Flask(__name__)

app.secret_key="secret_key"

room_files_path=os.getenv('ROOM_FILES_PATH')

csv_path=os.getenv('CSV_PATH')


#region helper functions

#used in register and in login functions
def check_user_registration(username, password,callFunction):
    with open(csv_path, 'r', newline='') as file:
        reader = csv.reader(file)
        if callFunction=="login":
          for row in reader:
              if row[0] == username and decode_password(row[1]) == password:
                  return True
        elif callFunction=="register":
           for row in reader:
              if row[0] == username:
                  return True
    return False
  
def encode_password(password):
    encoded_bytes = base64.b64encode(password.encode('utf-8'))
    return encoded_bytes.decode('utf-8')



def decode_password(encoded_password):
    decoded_bytes = base64.b64decode(encoded_password.encode('utf-8'))
    return decoded_bytes.decode('utf-8')
#endregion

#region login
@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
        username = request.form['username']
        userpass = request.form['password']
        if check_user_registration(username,userpass,"login"):
            session['username'] = username
            return redirect('/lobby')
        else:
            return "Invalid credentials"
   return render_template('login.html')

#endregion

#region register
@app.route('/', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        userpass = request.form['password']
        encoded_pass=encode_password(userpass)
        
        #Check if the user already exists
        if check_user_registration(username, userpass,"register"):
          return redirect("/login")

         # Check if username is valid
        if not valid_username(username):
            return "Username must be at least 5 characters"
        
        # Check if password is strong
        if not is_password_strong(userpass):
            return "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number."
        
        # Open the CSV file in read mode
        with open(csv_path, 'a',newline='') as file:
          writer=csv.writer(file)
          writer.writerow([username,encoded_pass])
        return redirect("/login")
        
    return render_template("register.html")

def valid_username(username):
    # Check if username is at least 5 characters long
    if len(username) < 5:
        return False
    return True
    

def is_password_strong(password):
    # Check if password is at least 8 characters long
    if len(password) < 8:
        return False

    # Check if password contains at least one uppercase letter
    if not any(c.isupper() for c in password):
        return False

    # Check if password contains at least one lowercase letter
    if not any(c.islower() for c in password):
        return False

    # Check if password contains at least one number
    if not any(c.isdigit() for c in password):
        return False

    return True

#endregion

#region lobby
@app.route('/lobby', methods=['GET', 'POST'])
def lobby():
    if 'username' in session:
        if request.method == 'POST':
            room_name = request.form['new_room']
            rooms = os.listdir('rooms/')
            new_rooms = [x[:-4] for x in rooms]
            # Check if room name already exists
            if room_name in new_rooms:
                return "The given room name already exists"
            else:
                try:
                    with open(f'rooms/{room_name}.txt', 'x') as f:
                        f.write('Welcome! \n')
                except FileNotFoundError:
                    return "The given room name already exists"
            print("CREATED NEW ROOM NAMED: " + room_name )
        rooms = os.listdir('rooms/')
        new_rooms = [x[:-4] for x in rooms]
        return render_template('lobby.html', rooms=new_rooms)  
    else:
        return redirect('/login')

#endregion

#region logout
@app.route("/logout")
def logout():
  session.pop('username', None)
  return redirect("/login")
#endregion

#region chat ( This function handles the chat page)
@app.route('/chat/<room>', methods=['GET', 'POST'])
def chat(room):
  return render_template('chat.html', room=room)

#endregion

#region update_content (This function handles the API for getting chat message)
@app.route('/api/chat/<room>', methods=['GET','POST'])
def updateChat(room):
    if not session.get("username"):
        return redirect("/")
    print("add msg")
    filename = room_files_path+room+".txt"

    if request.method == 'POST':
        msg = request.form['msg']
        if "username" in session:
            # Get the current date and time
            current_datetime = datetime.datetime.now()
            # Format the date and time as a string
            formatted_datetime = current_datetime.strftime("[%Y-%m-%d %H:%M:%S]")
            with open(filename,"a") as file:
              file.write("\n"+session.get('username')+": "+msg + " " + formatted_datetime)
              
    with open(filename,"r") as file:
        room_data = file.read()
        return room_data

#endregion

#region health check
@app.route("/health")
def health():
    return "OK", 200
#endregion

#region delete messages
@app.route('/chat/<room>/clear', methods=['GET', 'POST'])
def clear_messages(room):
  """Clears all messages in the current room, except for the messages of the current user."""
  if not session.get("username"):
    return redirect("/")
  filename = room_files_path + room + ".txt"
  with open(filename, "r") as f:
    messages = f.read().splitlines()
  f.close()

  # Get the current user ID.
  user_name = session['username']

  # Delete all messages from the current user.
  messages_to_remove = []

  for message in messages:
    if message.split(':')[0] == user_name:
      messages_to_remove.append(message)

  for message in messages_to_remove:
    messages.remove(message)

  # Empty the file.
  os.remove(filename)
  # Write the updated messages to the file.
  with open(filename, "w") as f:
    f.write("\n".join(messages))
  f.close()
  return "succeed"

#endregion

if __name__ == '__main__':
  app.run(host="0.0.0.0",debug=True)