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

#Question 1.2
#we can iterate through strings like lists in python using a for loop
def is_palindrome(user_name):
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

@app.route('/<name>', methods=['GET'])
def welcome_text(name):
    # Process this person's name
    processed_name = process_user_name(name)

    if not user_name:    # If there is no user name given, default to guest
        return "Welcome, Guest, to my CSCB20 website!"
    elif is_palindrome(name):
        welcome_message = f"Welcome {processed_name}. Your name is a palindrome!"
    else:
        welcome_message =  f"Welcome, {processed_name}, to my CSCB20 website!"
    # Return the message
    return welcome_message
   

#Question 1.3
#when python concatenates it creates a new string and we must have a variable to store it in
def vowel_to_emoji(user_name: str):

    emoji_string = ""
    for i in user_name:
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


@app.route('/emoji/<name>', methods=['GET'])
def welcome_replace_vowels(name):
    # final_user_name = vowel_to_emoji(user_name)

    processed_name = vowel_to_emoji(name)
    # If there is no user name given, default to guest
    if not name:
        return "Welcome, Guest, to my CSCB20 website!"
    else:
        return f"Welcome, {processed_name}, to my CSCB20 website!"
   

if __name__ == '__main__':
    app.run(debug=True)
