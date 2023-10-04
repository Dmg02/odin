import os 

print("Database Name:", os.getenv('DB_NAME'))
print("Database Host:", os.getenv('DB_HOST'))
print("Database User:", os.getenv('DB_USER'))
print("Database Password:", os.getenv('DB_PASSWORD'))