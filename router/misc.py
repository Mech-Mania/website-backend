import random, string




def getAndorHTML():
    AndorText = open('public/andor.txt','r').readlines()
    printed = AndorText[random.randint(0,len(AndorText)-1)]
    htmlContent = f"""
    <html>
        <body>
            <p style='font-family: monospace; padding-bottom:20px; text-align:center; text-indent: initial;font-size: initial;tab-size: 4;border-spacing: 0px;overflow:wrap;'>{printed}</p>
        </body>
    </html>
    """
    return htmlContent

def generate_random_string(length:int):
    characters:str = str(string.ascii_letters) + str(string.digits) # Includes uppercase, lowercase letters, and digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
