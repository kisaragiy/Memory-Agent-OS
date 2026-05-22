x = 0

try:
    result = 1 / x
except ZeroDivisionError:
    print("Error: Division by zero is not allowed.")
else:
    print(f"The result is {result}")
