import random
def getAndorHTML():
    AndorText = open('public/andor.txt','r').readlines()
    printed = AndorText[random.randint(0,len(AndorText)-1)]
    print(printed)
    htmlContent = f"""
    <html>
        <body>
            <p style='font-family: monospace; padding-bottom:20px; text-align:center; text-indent: initial;font-size: initial;tab-size: 4;border-spacing: 0px;overflow:wrap;'>{printed}</p>
        </body>
    </html>
    """
    return htmlContent