from flask import Flask
from pymongo import  MongoClient




app= Flask(__name__) 
 
app.config.from_mapping(
     SECRET_KEY="Secret_key ",
 
 ) 
app.config["MONGO_URI"]="mongodb+srv://desh97016:dbUser@cluster2.tswuq7f.mongodb.net/HealthFitness"
client=MongoClient(app.config   ['MONGO_URI'])

db = client['HealthFitness']

users_collection=db.users
Fitness_Program=db.Fitness_program



from App import routes