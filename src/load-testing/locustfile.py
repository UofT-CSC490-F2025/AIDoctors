from locust import HttpUser, task, between
import random

predict_input = {
  "patient_uuid": "patient-12345",
  "drug1": "Warfarin",
  "drug2": "Aspirin",
  "drug1_norm": "warfarin",
  "drug2_norm": "aspirin",
  "overlap_start": "2024-01-15",
  "overlap_stop": "2024-02-15",
  "Age": 65,
  "Sex": "M",
  "Comorbidities": [
    "Hypertension",
    "Diabetes"
  ],
  "pair_key": "warfarin_aspirin",
  "unified_severity": "Major",
  "unified_mechanism_text": "Both drugs affect blood clotting mechanisms",
  "ddi_confidence": 0.95,
  "ddi_known": True
}

class APIUser(HttpUser):
    """
    Load test for CSC490 FastAPI backend.
    Simulates realistic user behavior including authentication, profile access, and predictions.
    """
    
    # Wait between 1-3 seconds between tasks to simulate real user behavior
    wait_time = between(1, 3)
    weight = 10
    
    # Store authentication token
    token = None
    
    def on_start(self):
        """
        Called when a simulated user starts.
        Registers and authenticates the user.
        """
        # Generate unique user credentials
        user_id = random.randint(1, 1000)
        self.username = f"loadtest_user_{user_id}"
        self.password = "TestPassword123!"
        self.email = f"loadtest_{user_id}@example.com"
        
        # Register user
        self.register()
        
        # Login to get token
        self.login()
    
    def register(self):
        """Register a new user"""
        response = self.client.post(
            "/users/register",
            json={
                "username": self.username,
                "email": self.email,
                "password": self.password,
                "first_name": "Load",
                "last_name": "Test"
            },
            name="/users/register"
        )
        
        if response.status_code == 200:
            print(f"✓ Registered user: {self.username}")
        elif response.status_code == 400:
            # User might already exist from previous test
            print(f"⚠ User {self.username} already exists")
    
    def login(self):
        """Authenticate and get access token"""
        response = self.client.post(
            "/auth/token",
            data={
                "username": self.username,
                "password": self.password
            },
            name="/auth/token"
        )
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print(f"✓ Logged in user: {self.username}")
        else:
            print(f"✗ Login failed for {self.username}")
    
    @task(5)
    def health_check(self):
        """Health check endpoint - most frequent task"""
        self.client.get("/health", name="/health")
    
    @task(2)
    def get_current_user(self):
        """Get current user profile"""
        if not self.token:
            return
        
        self.client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {self.token}"},
            name="/users/me"
        )
    
    @task(2)
    def predict_ddi(self):
        """
        Make a drug-drug interaction prediction.
        This is the most resource-intensive endpoint.
        """
        if not self.token:
            return
                
        self.client.post(
            "/predict/",
            json=predict_input,
            headers={"Authorization": f"Bearer {self.token}"},
            name="/predict/",
            timeout=30
        )


class UnauthenticatedUser(HttpUser):
    """
    Simulates unauthenticated users accessing public endpoints.
    """
    weight = 1
    wait_time = between(2, 5)
    
    @task(10)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health", name="/health [unauth]")
    
    @task(5)
    def root_endpoint(self):
        """Root endpoint"""
        self.client.get("/", name="/ [unauth]")
    
    @task(1)
    def try_protected_endpoint(self):
        """Attempt to access protected endpoint without auth"""
        self.client.get(
            "/users/me",
            name="/users/me [unauth - expected 401]"
        )
