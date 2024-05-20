import bcrypt

def generate_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt), salt

if __name__ == "__main__":
    password = input("Enter password: ")
    password, salt = generate_password(password)
    print("Salt: ", salt)
    print("Password: ", password)