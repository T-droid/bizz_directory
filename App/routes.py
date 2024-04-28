from flask import render_template, request, jsonify, make_response,session
from flask_bcrypt import Bcrypt
from App import app, users_collection,Categories,Fitness_Program
from App import Fitness


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
    
    # Check if email already exists in the database
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
 
 
 
 
 #defined categories with description   

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
                  
                    "id": exercise_type['id'],  # Use the custom id field
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

user_fitness_programs = {}

#create a fitness program for a particular objective category
@app.route("/fitness_program/category_name", methods=["POST"])
def create_fitness_program_categories(category_name):
    if 'email' not in session:
        return jsonify({"error": "User session not found"}), 401

    data = request.json
    user_id = session['id']
    user_email=session['email']
    program_name = data.get("category_name")
    
    # Check if the category exists
    category = Categories.find_one({"name": category_name})
    if not category:
        return jsonify({"error": "Category not found"}), 404

    # Check if a similar program already exists for the user
    for program in user_fitness_programs.get(user_id, []):
        if program['program_name'] == program_name:
            return jsonify({"message": "Program already exists. Finish the currently enrolled program."}), 400

    # Initialize category weights based on the number of exercise types in the category
    category_weights = [0] * len(category.get('exercise_types', []))
    
    # Create fitness program
    fitness_program = {
        "user_id": user_id,
        "user_email":user_email,
        "program_name": program_name,
        "weights": category_weights,
        "progress": 0,
        
        
    }

    # Store fitness program in user's programs
    user_fitness_programs.setdefault(user_id, []).append(fitness_program)

    return jsonify({"message": "Fitness program created successfully"}), 201

#create a fitness program for a particular body part
@app.route("/fitness_program/bodypart", methods=["POST"])
def create_fitness_program_bodypart():
    if 'email' not in session:
        return jsonify({"error": "User session not found"}), 401

    data = request.json
    user_id = session['email']  
    user_email = session['email']  
    program_name = "bodypart" 
    body_part = data.get("bodypart")
    
    # Check if a similar program already exists for the user
    for program in user_fitness_programs.get(user_id, []):
        if program['body_part'] == body_part:
            return jsonify({"message": "Program already exists. Finish the current enrolled program."}), 400
    weight=[0]*15
    # Create fitness program
    fitness_program = {
        "user_id": user_id,
        "user_email": user_email,
        "program_name": program_name,
        "body_part": body_part,
        "weights":weight,
        "progress": 0,
        
    }

    
    user_fitness_programs.setdefault(user_id, []).append(fitness_program)

    return jsonify({"message": "Fitness program created successfully"}), 201


#get user enrolled fitness programm
@app.route("/fitness_programs/user_id", methods=["GET"])
def get_user_fitness_programs(user_id):
    if 'email' not in session:
        return jsonify({"error": "User session not found"}), 401

    if user_id not in user_fitness_programs:
        return jsonify({"error": "User has no fitness programs"}), 404

    return jsonify(user_fitness_programs[user_id]), 200


@app.route("/fitnessProgress", methods=["GET", "POST", "DELETE"])
def fitness_progress():
    if 'email' not in session:
        return jsonify({"error": "User session not found"}), 401

    user_id = session['email']  
    user_email = session['email']  

    if request.method == "GET":
        program_name = request.args.get("program_name")
        # Calculate progress for the given user and program name
        progress = Fitness.FitnessProgramProgressCalculator.calculate_progress(user_id, program_name)
        return jsonify({"progress": progress}), 200

    elif request.method == "POST":
        data = request.json
        program_name = data.get("program_name")
        exercise_type = data.get("exercise_type")
        status = data.get("status")

        # Update progress based on the provided information
        result = Fitness.FitnessProgramProgressCalculator.update_progress(user_id, program_name, exercise_type, status)
        return jsonify(result), result.get("status")

    elif request.method == "DELETE":
        data = request.json
        program_name = data.get("program_name")

        # Delete the fitness program
        result = delete_fitness_program(user_id, user_email, program_name)
        return jsonify(result), result.get("status")

def delete_fitness_program(user_id, user_email, program_name):
    # Check if the user ID exists in the user_fitness_programs dictionary
    if user_id in user_fitness_programs:
        # Iterate over the fitness programs associated with the user
        for program in user_fitness_programs[user_id]:
            # Check if the program name and user email match the provided values
            if program['program_name'] == program_name and program['user_email'] == user_email:
                # If the program is found, remove it from the list
                user_fitness_programs[user_id].remove(program)
                return {"message": "Fitness program deleted successfully"}, 200
    
    # If the program is not found, return an error message
    return {"error": "Fitness program not found"}, 404

    
    

    