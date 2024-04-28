import http.client

class ExerciseAPI:
    def __init__(self, rapidapi_key):
        self.conn = http.client.HTTPSConnection("exercisedb.p.rapidapi.com")
        self.headers = {
            'X-RapidAPI-Key': rapidapi_key,
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
