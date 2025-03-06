from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    if is_palindrome("Bocab"):
        return "palindrome"
    return "not palindrome"

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