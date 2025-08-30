import streamlit_authenticator as stauth

passwords_to_hash = ["adminpassword", "password1", "password2", "password3", "password4"]

hasher = stauth.Hasher()
hashed_passwords = [hasher.hash(pw) for pw in passwords_to_hash]

print("Hashed passwords to be copied into config.yaml file:")
print(hashed_passwords)