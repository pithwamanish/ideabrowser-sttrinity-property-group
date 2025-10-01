import requests
import sys
import json
from datetime import datetime

class IdeaBoardAPITester:
    def __init__(self, base_url="https://ideaboard-demo.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_idea_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_get_ideas_empty(self):
        """Test getting ideas when database might be empty"""
        success, response = self.run_test("Get Ideas (Initial)", "GET", "ideas", 200)
        if success:
            print(f"   Found {len(response)} existing ideas")
        return success, response

    def test_create_idea(self, text):
        """Test creating a new idea"""
        success, response = self.run_test(
            f"Create Idea: '{text[:30]}...'",
            "POST",
            "ideas",
            200,
            data={"text": text}
        )
        if success and 'id' in response:
            self.created_idea_ids.append(response['id'])
            print(f"   Created idea with ID: {response['id']}")
        return success, response

    def test_create_idea_validation(self):
        """Test idea creation validation"""
        # Test empty text
        success1, _ = self.run_test(
            "Create Idea - Empty Text",
            "POST",
            "ideas",
            422,  # Validation error
            data={"text": ""}
        )
        
        # Test text too long (over 280 chars)
        long_text = "a" * 281
        success2, _ = self.run_test(
            "Create Idea - Too Long",
            "POST",
            "ideas",
            422,  # Validation error
            data={"text": long_text}
        )
        
        return success1 and success2

    def test_upvote_idea(self, idea_id):
        """Test upvoting an idea"""
        success, response = self.run_test(
            f"Upvote Idea: {idea_id}",
            "PATCH",
            f"ideas/{idea_id}/upvote",
            200
        )
        if success:
            print(f"   New upvote count: {response.get('upvotes', 'unknown')}")
        return success, response

    def test_upvote_nonexistent_idea(self):
        """Test upvoting a non-existent idea"""
        fake_id = "non-existent-id-12345"
        return self.run_test(
            "Upvote Non-existent Idea",
            "PATCH",
            f"ideas/{fake_id}/upvote",
            404
        )

    def test_get_ideas_after_creation(self):
        """Test getting ideas after creating some"""
        success, response = self.run_test("Get Ideas (After Creation)", "GET", "ideas", 200)
        if success:
            print(f"   Total ideas: {len(response)}")
            if response:
                # Check if ideas are sorted by upvotes (descending)
                upvotes = [idea.get('upvotes', 0) for idea in response]
                is_sorted = all(upvotes[i] >= upvotes[i+1] for i in range(len(upvotes)-1))
                print(f"   Sorted by upvotes: {'✅' if is_sorted else '❌'}")
                
                # Show first few ideas
                for i, idea in enumerate(response[:3]):
                    print(f"   Idea {i+1}: {idea.get('text', '')[:50]}... (upvotes: {idea.get('upvotes', 0)})")
        return success, response

def main():
    print("🚀 Starting Idea Board API Testing...")
    print("=" * 60)
    
    tester = IdeaBoardAPITester()
    
    # Test API root
    tester.test_api_root()
    
    # Test getting initial ideas
    tester.test_get_ideas_empty()
    
    # Test creating ideas
    test_ideas = [
        "Build a sustainable city on Mars with renewable energy sources",
        "Create an AI-powered personal health assistant that monitors vitals 24/7",
        "Develop a blockchain-based voting system for transparent elections",
        "Design floating gardens for urban food production in small spaces"
    ]
    
    created_ideas = []
    for idea_text in test_ideas:
        success, response = tester.test_create_idea(idea_text)
        if success:
            created_ideas.append(response)
    
    # Test idea creation validation
    tester.test_create_idea_validation()
    
    # Test upvoting ideas
    if created_ideas:
        # Upvote the first idea multiple times to test sorting
        first_idea_id = created_ideas[0]['id']
        for i in range(3):
            tester.test_upvote_idea(first_idea_id)
        
        # Upvote second idea once
        if len(created_ideas) > 1:
            second_idea_id = created_ideas[1]['id']
            tester.test_upvote_idea(second_idea_id)
    
    # Test upvoting non-existent idea
    tester.test_upvote_nonexistent_idea()
    
    # Test getting ideas after all operations
    tester.test_get_ideas_after_creation()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! API is working correctly.")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())