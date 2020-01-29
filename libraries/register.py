from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string



def register_user(user):
    client = MongoClient(host=['host.docker.internal:27017'])
    db = client.users
    result=db.users.insert_one(user).inserted_id
    print(result)
    return result



