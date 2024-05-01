from flask import render_template, request, jsonify, make_response,session
from flask_bcrypt import Bcrypt
from App import app, users_collection,Categories,Fitness_Program
from App import Fitness
import requests


bcrypt = Bcrypt(app)

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if users_collection.find_one({'email': email}):
        return make_response(jsonify({'error': 'Email already exists'}), 400)
    
    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Register the user by inserting into the database
    new_user = {'username': username, 
                'email': email,
                'password': hashed_password}
    users_collection.insert_one(new_user)
    
    # Return success message
    return make_response(jsonify({'message': 'User registered successfully'}), 201)


@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    

    user = users_collection.find_one({"email": email})
    if user:
   
        if bcrypt.check_password_hash(user['password'], password):
           
            session['email'] = user['email']
        
            return make_response(jsonify({'message': 'Login successful'}), 200)
        else:
          
            return make_response(jsonify({'error': 'Incorrect password'}), 401)
    else:
        
        return make_response(jsonify({'error': 'User does not exist'}), 404)
 

#categories to achieve  a healthy lifestyle (objective)
#retreives all catgories with their data
@app.route("/categories", methods=["GET"])
def get_all_categories():
    categories = Categories.find()
    category_list = []
    for category in categories:
        category_data = {
            "_id": str(category['_id']), 
            "id": category['id'], 
            "name": category['name'],
            "description": category['description'],
            "exercise_types": []
        }
        # Check if the 'exercise_types' field exists and is not empty
        if 'exercise_types' in category and category['exercise_types']:
            for exercise_type in category['exercise_types']:
                exercise_type_data = {
                  
                    "id": exercise_type['id'], 
                    "name": exercise_type['name'],
                    "weight": exercise_type['weight'],
                    "instructions": exercise_type['instructions']
                }
                category_data['exercise_types'].append(exercise_type_data)
        
        category_list.append(category_data)

    response_data = jsonify(category_list)
    return make_response(response_data, 200)

# body parts to get fit (subjective) to bodypart
@app.route("/categories/bodypart", methods=["GET"])
def get_body_part():
    exercise_api=Fitness.ExerciseAPI()
    body_part_list = exercise_api.get_body_part_list()
    
    return jsonify({"body_parts": body_part_list})



# get exercise types of particular objective category
@app.route("/categories/<string:category_name>", methods=["GET"])
def get_category_details(category_name):
    category = Categories.find_one({"name": category_name})
    if category:
        category_data = {
            "id": str(category['_id']),
            "name": category['name'],
             "exercise_types": []
        }
        # Check if the 'exercise_types' field exists and is not empty
        if 'exercise_types' in category and category['exercise_types']:
            for exercise_type in category['exercise_types']:
                category_data['exercise_types'].append({"name": exercise_type['name']})
        
        response_data = jsonify(category_data)
        return make_response(response_data, 200)
    else:
        error_message = {"error": "Category not found"}
        response_data = jsonify(error_message)
        return make_response(response_data, 404)
    

#exercises for specific body part
@app.route("/exercise/<body_part>", methods=["GET"])
def get_body_part_exercise(body_part):
    exercise_api=Fitness.ExerciseAPI()
    
    try:
        exercise_data = exercise_api.get_body_part_exercises(body_part, limit=15)
        return make_response(exercise_data, 200)  # Assuming exercise_data is already JSON
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

#create a fitness program for a particular objective category
@app.route("/fitness_program/<string:category_name>", methods=["POST"])
def create_fitness_program_categories(category_name):
    
    data = request.json
    user_id=data.get("user_id")
    user_email=data.get("user_email")
    program_name = category_name
    
   # if 'email' not in session:
     #   return jsonify({"error": "User session not found"}), 401

    
    # Check if the category exists
    category = Categories.find_one({"name": category_name})
    if not category:
        return jsonify({"error": "Category not found"}), 404

      # Check if a similar program already exists for the user in the database
    existing_program = Fitness_Program.find_one({"user_id": user_id, "program_name": program_name})
    if existing_program:
        return jsonify({"message": "Program already exists. Finish the currently enrolled program."}), 400

    # Initialize category weights based on the number of exercise types in the category
    exercise_types = category.get('exercise_types', [])
    category_weights =  {exercise['name']: False for exercise in exercise_types}

    
    # Create fitness program
    fitness_program = {
        "user_id": user_id,
        "user_email":user_email,
        "program_name": program_name,
        "weights": category_weights,
        "progress": 0,
        
        
    }

   
    Fitness_Program.insert_one(fitness_program)
    return jsonify({"message": "Fitness program created successfully"}), 201


#create a fitness program for a particular body part
@app.route("/fitness_program/bodypart/<string:body_part>", methods=["POST"])
def create_fitness_program_bodypart(body_part):
    #if 'email' not in session:
       # return jsonify({"error": "User session not found"}), 401
    data = request.json
    user_id =data.get("user_id")
    user_email = data.get("user_email")
    program_name = "bodypart"

    
    exercise_endpoint = f"http://127.0.0.1:5000/exercise/{body_part}" 
    response = requests.get(exercise_endpoint)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch exercise data"}), 500
    
    exercise_data = response.json()
    
    exercise_types = [exercise['name'] for exercise in exercise_data]

    
 
    
       
    
    # Check if a similar program already exists for the user
    existing_program = Fitness_Program.find_one({"user_id": user_id, "body_part": body_part})
    if existing_program:
        return jsonify({"message": "Program already exists. Finish the current enrolled program."}), 400
    
     # Initialize weights dictionary with exercise types and their weights as 0
    exercise_type_weights = {exercise_type: False for exercise_type in exercise_types}

  
    
    # Create fitness program
    fitness_program = {
        "user_id": user_id,
        "user_email": user_email,
        "program_name": program_name,
        "body_part": body_part,
        "weights": exercise_type_weights,
        "progress": 0,
    }

    Fitness_Program.insert_one(fitness_program)
    return jsonify({"message": "Fitness program created successfully"}), 201

@app.route("/fitness_programs/<string:user_id>", methods=["GET"])
def get_user_fitness_programs(user_id):
    data = request.json
    user_id = data.get("user_id")
   

    user_programs = list(Fitness_Program.find({"user_id": user_id}))
    if len(user_programs) == 0:
        return jsonify({"error": "User has no fitness programs"}), 404

    fitness_programs_data = []
    for program in user_programs:
        program_data = {
            "user_id": program["user_id"],
            "program_name": program["program_name"],
            "weights": program["weights"],
            "progress": program["progress"]
        }
        if "body_part" in program:
            program_data["body_part"] = program["body_part"]
        fitness_programs_data.append(program_data)

    return jsonify(fitness_programs_data), 200

@app.route("/fitnessProgress", methods=["GET", "PUT", "DELETE"])
def fitness_progress():

    data = request.json
    user_id = data.get("user_id")
    user_email = data.get("user_email")
   

    '''
    if request.method == "GET":
        program_name = data.get("program_name")
        # Calculate progress for the given user and program name
        progress = (user_id, program_name)
        return jsonify({"progress": progress}), 200
    '''
    
    if request.method == "PUT":
        program_name = data.get("program_name")
        exercise_type = data.get("exercise_type")
        status = data.get("status")

        if not program_name or not exercise_type or not status:
             return jsonify({"error": "Missing required data"}), 400   

        if status == "done":
         
            Fitness_Program.update_one(
                {"user_id": user_id, "program_name": program_name},
                {"$set": {"weights.{}".format(exercise_type): True}}
            )

            # Calculate the progress percentage
            program = Fitness_Program.find_one({"user_id": user_id, "program_name": program_name})
            weights = program.get("weights", {})
            num_true_exercises = sum(1 for value in weights.values() if value)  # Count True values in weights
            total_exercises = len(weights)
            progress_percentage = (num_true_exercises / total_exercises) * 100

            # Update the progress value
            Fitness_Program.update_one(
                {"user_id": user_id, "program_name": program_name},
                {"$set": {"progress": progress_percentage}}
            )

            return jsonify({"message": result}), 200 if status == "done" else 400

    elif request.method == "DELETE":
        data = request.json
        program_name = data.get("program_name")

        # Delete the fitness program
        result = delete_fitness_program(user_id, user_email, program_name)
        return jsonify(result), result.get("status")

def delete_fitness_program(user_id, user_email, program_name):
    # Define the query to find the document to delete
    query = {"user_id": user_id, "user_email": user_email, "program_name": program_name}

    # Delete the document that matches the query
    result = Fitn.delete_one(query)

    # Check if the deletion was successful
    if result.deleted_count == 1:
        return {"message": "Fitness program deleted successfully", "status": 200}
    else:
        return {"error": "Fitness program not found or could not be deleted", "status": 404}

    
    

    