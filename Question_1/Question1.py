from flask import Flask, request
app = Flask(__name__)


# Question 1.1
def process_user_name(user_name):
    # Remove the leading and the trailing spaces
    user_name = user_name.strip()

    # Check is the user's name has any digits
    user_with_digit = False
    digitless_name = ""

    for char in user_name:
        if char.isdigit(): #If there are digits, mark the name
              user_with_digit = True
        else:
            digitless_name += char # Add the characters that aren't digits

    # If the name has digits, convert digitless name to uppercase
    if user_with_digit:
        user_name = digitless_name.upper()

    # If user's name is all uppercase, convert to lower
    elif user_name.isupper():
        user_name = user_name.lower()

    # If user's name is all lowercase, convert to upper
    elif user_name.islower():
        user_name = user_name.upper()
  
    # If the user's name contains both cases, convert the name to a title case
    else:
        user_name = user_name.title()
    
    # Return the updated user's name
    return user_name

@app.route("/")
def welcome_text():
     # Get the name from the URL query string
     user_name = request.args.get('user_name', '')

     # Set the name that will appear as the processed name
     final_user_name = process_user_name(user_name)

     # If there is no user name given, default to guest
     if not user_name:
         return "Welcome, Guest, to my CSCB20 website!"

     # Set the welcome message
     welcome_message =  f"Welcome, {final_user_name}, to my CSCB20 website!"

     # Return the message
     return welcome_message
   
if __name__ == '__main__':
    app.run(debug=True)



=======

#we can iterate through strings like lists in python using a for loop
def is_palindrome(string: str):
    palindrome_counter = 0
    i = 0;
    j = len(string) - 1
    while i < j:
        if string[i].lower() != string[j].lower():
            break;
        i = i + 1
        j = j - 1
        palindrome_counter = palindrome_counter + 1  
         
    if palindrome_counter == len(string)//2:
        return True
    return False

#when python concatenates it creates a new string and we must have a variable to store it in
def vowel_to_emoji(name: str):
    emoji_string = ""
    for i in name:
        if i.lower() == "a":
            emoji_string = emoji_string + "🔺"
        elif i.lower() == "e":
            emoji_string = emoji_string + "🎗"
        elif i.lower() == "i":
            emoji_string = emoji_string + "👁"
        elif i.lower() == "o":
            emoji_string = emoji_string + "🔵"
        elif i.lower() == "u":
            emoji_string = emoji_string + "🆙"
        else:
            emoji_string = emoji_string + i
    return emoji_string
