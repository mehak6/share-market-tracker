"""
Cloud Sync Service for ShareProfitTracker
Handles authentication and data synchronization with cloud backend
"""

import requests
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

class CloudSyncService:
    """Service for syncing data with cloud backend"""

    def __init__(self, api_url: str = None):
        # Load API URL from environment or use default
        self.api_url = api_url or os.getenv("CLOUD_API_URL", "https://your-app.railway.app")
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.display_name: Optional[str] = None
        self.token_file = "cloud_token.json"

        # Try to load existing token
        self._load_token()

    def _load_token(self):
        """Load saved token from file"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.token = data.get('token')
                    self.user_id = data.get('user_id')
                    self.display_name = data.get('display_name')
        except Exception:
            pass

    def _save_token(self):
        """Save token to file"""
        try:
            with open(self.token_file, 'w') as f:
                json.dump({
                    'token': self.token,
                    'user_id': self.user_id,
                    'display_name': self.display_name
                }, f)
        except Exception:
            pass

    def _clear_token(self):
        """Clear saved token"""
        self.token = None
        self.user_id = None
        self.display_name = None
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
        except Exception:
            pass

    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.token is not None

    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self.token:
            raise Exception("Not logged in")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def register(self, email: str, password: str, display_name: str) -> Dict[str, Any]:
        """Register a new cloud account"""
        try:
            response = requests.post(
                f"{self.api_url}/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "display_name": display_name
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.user_id = data['user_id']
                self.display_name = data['display_name']
                self._save_token()
                return {"success": True, "message": "Registration successful"}
            else:
                error = response.json().get('detail', 'Registration failed')
                return {"success": False, "message": error}

        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Cannot connect to cloud server"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login to cloud account"""
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.user_id = data['user_id']
                self.display_name = data['display_name']
                self._save_token()
                return {"success": True, "message": "Login successful", "display_name": self.display_name}
            else:
                error = response.json().get('detail', 'Login failed')
                return {"success": False, "message": error}

        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Cannot connect to cloud server"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def logout(self):
        """Logout from cloud account"""
        self._clear_token()
        return {"success": True, "message": "Logged out"}

    def upload_data(self, stocks: List[Dict], cash_transactions: List[Dict],
                   expenses: List[Dict], dividends: List[Dict]) -> Dict[str, Any]:
        """Upload local data to cloud"""
        if not self.is_logged_in():
            return {"success": False, "message": "Not logged in"}

        try:
            response = requests.post(
                f"{self.api_url}/api/sync/upload",
                headers=self.get_headers(),
                json={
                    "stocks": stocks,
                    "cash_transactions": cash_transactions,
                    "expenses": expenses,
                    "dividends": dividends
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return {"success": True, "message": data.get('message', 'Upload successful')}
            else:
                error = response.json().get('detail', 'Upload failed')
                return {"success": False, "message": error}

        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Cannot connect to cloud server"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def download_data(self) -> Dict[str, Any]:
        """Download cloud data to local"""
        if not self.is_logged_in():
            return {"success": False, "message": "Not logged in"}

        try:
            response = requests.get(
                f"{self.api_url}/api/sync/download",
                headers=self.get_headers(),
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": data.get('message', 'Download successful'),
                    "data": data.get('data')
                }
            else:
                error = response.json().get('detail', 'Download failed')
                return {"success": False, "message": error}

        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Cannot connect to cloud server"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_sync_status(self) -> Dict[str, Any]:
        """Get cloud data counts"""
        if not self.is_logged_in():
            return {"success": False, "message": "Not logged in"}

        try:
            response = requests.get(
                f"{self.api_url}/api/sync/status",
                headers=self.get_headers(),
                timeout=30
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error = response.json().get('detail', 'Status check failed')
                return {"success": False, "message": error}

        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Cannot connect to cloud server"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def test_connection(self) -> bool:
        """Test connection to cloud server"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
