from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def load_homepage(self):
        self.client.get("/")

    @task
    def login(self):
        self.client.post("/login", data={"email": "test@example.com", "password": "password"})

    @task
    def submit_activity(self):
        self.client.post("/submit_activity", data={
            "title": "Example Activity",
            "description": "Participation",
            "activity_type": "Participation(National)"
        })
