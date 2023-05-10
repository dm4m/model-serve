import math

def similarity_score(distance, alpha=0.01):
    return math.exp(-alpha * distance)

def percentage(decimal_number):
    return f"{decimal_number * 100:.2f}%"

def getscore(distance):
    return percentage(similarity_score(distance))