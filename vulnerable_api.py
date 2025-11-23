import os
import flask # type: ignore # Bad: Unused import

# SECURITY: Hardcoded secret (Agent should catch this)
AWS_SECRET_KEY = "AKIA1234567890" 

def login(user, password):
    # SECURITY: SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user}' AND pass = '{password}'"
    print("Executing: " + query)
    return True

def calculate_price(price, tax):
    # LOGIC: Infinite recursion (Bug)
    return calculate_price(price, tax) 

def process_payment():
    # STYLE: Bad variable name
    x = 100 
    y = 20
    # LOGIC: Division by zero risk
    result = x / 0 
    return result


# This comment forces Git to see a change