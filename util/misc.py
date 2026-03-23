import random, string

def generate_random_string(length:int):
    characters:str = str(string.ascii_letters) + str(string.digits) # Includes uppercase, lowercase letters, and digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
