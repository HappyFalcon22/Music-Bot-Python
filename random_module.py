import random

def random_coin():
    outcome = ["Head", "Tail"]
    return outcome[random.randint(0, 1)]
