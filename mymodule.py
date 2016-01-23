
def get_integer(prompt):
    """Asks the user a question, checks that they entered an integer
       and returns the integer."""
    #
    # Check for a space as the last character and add a space if it
    # is not.
    #
    if prompt[-1] != " ":
        prompt = prompt + " "

    answer = input(prompt)
    #
    # Test to see if the user's answer is really an integer.
    #
    prompt = prompt + "(integers only) "
    while is_integer(answer) == False:
        answer = input(prompt)

    answer = int(answer)
    return answer

def is_integer(string):
    """Takes a string as an argument and returns True if it is an
       integer, and False otherwise."""
    #
    # If the string is empty, then it is not an integer.
    #
    isInteger = True
    if string == "":
        isInteger = False
    else:
        #
        # Check the first characters for + or - and remove it.
        #
        while (string != "") and (string[0] in '+-'):
            string = string[1:]
        #
        # Loop through the string looking for non-integers.
        #
        counter = 0
        stringLength = len(string)
        while counter < stringLength:
            if string[counter] not in '0123456789':
                isInteger = False
            counter = counter + 1
    return isInteger

def get_positive_integer(prompt):
    """Asks the user a question and checks that they entered a positive
       integer."""
    answer = get_integer(prompt)
    prompt = prompt + "(positive only) "
    while answer < 1:
        answer = get_integer(prompt)
    return answer

def get_integer_between(low,high,prompt="Enter an integer:"):
    prompt += " ("+str(low)+"-"+str(high)+") "
    number = get_integer(prompt)
    while (number < low) or (number > high):
        number = get_integer(prompt)
    return number

def get_float(prompt):
    """Asks the user the prompt and verifies they enter a float"""
    if prompt[-1] != " ":
        prompt += " "
    number = input(prompt)
    prompt = prompt + "(numbers only) "
    while not is_float(number):
        number = input(prompt)
    number = float(number)
    return number

def is_float(number):
    """Returns True is number is a float else it returns False."""
    string = str(number)
    isFloat = True
    if string == "":
        isFloat = False
    else:
        #
        # Check the first characters for + or - and remove it.
        #
        while (string != "") and (string[0] in '+-'):
            string = string[1:]
        #
        # Find the decimal point
        #
        decimalCounter = 0
        stringLength = len(string)
        counter = 0
        while counter < stringLength:
            if string[counter] == '.':
                decimalLocation = counter
                decimalCounter = decimalCounter + 1
        #
        # Are there 0, 1 or more decimalPoints?
        #
        if decimalCounter == 0:
            isFloat = is_integer(number)
        elif decimalCounter == 1:
            if is_integer(string[0:decimalLocation]) and is_integer(string[decimalLocation+1:]):
                isFloat == True
            else:
                isFloat == False
        else: # more than one decimal point!
            isFloat == False
    return isFloat

def get_boolean(prompt):
    """Ask the user a yes or no question"""
    prompt = prompt + " (y/n) "
    answer = input(prompt)
    answer = answer.lower()
    if answer in ['yes','sure','yeah','true','absolutely','y','da','si']:
        answer = True
    elif answer in ['n','no','nope','nah']:
        answer = False
    else:
        prompt = "Does "+answer+" mean yes or no?"
        answer = get_boolean(prompt)
    return answer

def get_string(prompt):
    """Get and return a non-empty string"""
    if prompt[-1] != " ":
        prompt = prompt + " "
    string = input(prompt)
    prompt = prompt + "(you have to enter something) "
    while string == '':
        string = input(prompt)
    return string

def tester():
    print(is_integer("-"))
    print(is_integer("+"))
    print(is_integer("+-+-+"))
    print(is_integer("+1++++++1++++3"))
    print(is_integer("-5-----443---3"))
    print(is_integer("3-"))
    print(is_integer(""))
    print(is_integer("-3"))
    print(is_integer("+1"))
    print(is_integer("+++1"))

def tester2():
    answer = 0
    while answer != 12:
        answer = get_integer("Enter a number:")
        print("good answer")

def tester3():
    answer = 0
    while answer != 12:
        answer = get_positive_integer("Enter a number:")
        print("good answer:", answer)


