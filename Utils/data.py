import pickle

def save(username, password):
    with open('data.pkl', 'wb') as f:
    pickle.dump(my_data, f)

def load():
    with open('data.pkl', 'rb') as f:
    my_data = pickle.load(f)
