from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return vowel_to_emoji("hanna is fat")

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