import http.client

class ExerciseAPI:
    def __init__(self, rapidapi_key):
        self.conn = http.client.HTTPSConnection("exercisedb.p.rapidapi.com")
        self.headers = {
            'X-RapidAPI-Key': "4f29af3280msh23b2e89045c733dp191baajsne20fd121c3f9",
            'X-RapidAPI-Host': "exercisedb.p.rapidapi.com"
        }

    def get_body_part_list(self):
        self.conn.request("GET", "/exercises/bodyPartList", headers=self.headers)
        res = self.conn.getresponse()
        data = res.read()
        return data.decode("utf-8")

    def get_body_part_exercises(self, body_part, limit=15):
        endpoint = f"/exercises/bodyPart/{body_part}?limit={limit}"
        self.conn.request("GET", endpoint, headers=self.headers)
        res = self.conn.getresponse()
        data = res.read()
        return data.decode("utf-8")


class FitnessProgramProgressCalculator:
    def __init__(self, user_fitness_programs):
        self.user_fitness_programs = user_fitness_programs

    def calculate_progress(self, user_id, program_name):
        program_exists = False
        for program in self.user_fitness_programs.get(user_id, []):
            if program['program_name'] == program_name:
                program_exists = True
                category_weights = program.get('weights', [])
                body_part = program.get('body_part')
                if body_part:  # Body part program
                    progress = sum(category_weights) * (1/15) * 100
                else:  # Category-based program
                    progress = sum(category_weights)
                return progress
        if not program_exists:
            return None

    def update_progress(self, user_id, program_name, exercise_type, status):
        for program in self.user_fitness_programs.get(user_id, []):
            if program['program_name'] == program_name:
                category_weights = program.get('weights', [])
                body_part = program.get('body_part')

                # Check if the given exercise type exists in the program
                if exercise_type not in [exercise['name'] for exercise in program.get('exercise_types', [])]:
                    return {"error": f"Exercise type '{exercise_type}' not found in program '{program_name}'"}, 404

                # Update the progress based on the status
                if status == "done":
                    if body_part:  # Body part program
                        for i in range(len(category_weights)):
                            category_weights[i] += (1 / 15) if i == exercise_type else 0
                    else:  # Category-based program
                        for exercise in program.get('exercise_types', []):
                            if exercise['name'] == exercise_type:
                                weight = exercise.get('weight', 0)
                                for i in range(len(category_weights)):
                                    category_weights[i] += weight if program['exercise_types'][i]['name'] == exercise_type else 0

                    program['weights'] = category_weights
                    return {"message": "Progress updated successfully"}, 200
                else:
                    return {"error": "Invalid status. Only 'done' status is allowed"}, 400

        # If the program with the given name is not found for the user
        return {"error": f"Fitness program '{program_name}' not found for user '{user_id}'"}, 404
