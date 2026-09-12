import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("--- 1. Testing Health Endpoint ---")
    res = client.get("/api/health")
    assert res.status_code == 200, res.text
    print("Health check passed:", res.json())

    print("\n--- 2. Testing Demo Login ---")
    res = client.post("/api/auth/demo-login?role=student")
    assert res.status_code == 200, res.text
    auth_data = res.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Demo login passed! User:", auth_data["user"]["name"])

    print("\n--- 3. Testing Dashboard Brief ---")
    res = client.get("/api/planner/dashboard-brief", headers=headers)
    assert res.status_code == 200, res.text
    brief = res.json()
    print("Dashboard greeting:", brief["greeting"])
    print("AI Recommendation:", brief["ai_recommendation"])
    print("Planned hours vs available:", brief["planned_hours"], "/", brief["available_hours"])

    print("\n--- 4. Testing Smart Capture NLP Engine ---")
    demo_text = (
        "Tomorrow we have an AI project meeting at 4 PM. Before that I need to finish the database design. "
        "Our DBMS assignment is due Friday and I still need to complete normalization and SQL queries. "
        "I also have an exam next Monday."
    )
    res = client.post("/api/capture/analyze", json={"text": demo_text}, headers=headers)
    assert res.status_code == 200, res.text
    capture_data = res.json()
    print("Smart Capture summary:", capture_data["summary"])
    print(f"Extracted {len(capture_data['extracted_items'])} items:")
    for it in capture_data["extracted_items"]:
        print(f" - [{it['type'].upper()}] {it['title']} (Priority: {it['priority']}, Deadline: {it['deadline']})")
        if it['subtasks']:
            print(f"    Subtasks: {it['subtasks']}")

    print("\n--- 5. Testing Daily Plan & Overload Balancer ---")
    res = client.post("/api/planner/daily-plan", json={"available_hours": 3.0, "start_time_str": "09:00"}, headers=headers)
    assert res.status_code == 200, res.text
    plan = res.json()
    print("Is overloaded:", plan["is_overloaded"])
    if plan["is_overloaded"]:
        print("Overload warning:", plan["overload_message"])
        print("Recommended moves:", plan["recommended_moves"])
    print(f"Generated {len(plan['schedule_blocks'])} schedule blocks (with breaks)")

    print("\n--- 6. Testing Student Exam Countdowns ---")
    res = client.get("/api/student/exam-countdowns", headers=headers)
    assert res.status_code == 200, res.text
    countdowns = res.json()
    print("Exam countdowns:", countdowns)

    print("\n--- 7. Testing Focus Session Logging & Analytics ---")
    # Log a 25-minute focus session
    res = client.post("/api/focus/sessions", json={
        "task_id": None,
        "duration_minutes": 25,
        "completed_task": True,
        "reflection_notes": "Completed high-intensity focus block with zero distractions."
    }, headers=headers)
    assert res.status_code == 200, res.text

    res = client.get("/api/analytics/summary", headers=headers)
    assert res.status_code == 200, res.text
    analytics = res.json()
    print("Analytics completion rate:", analytics["completion_rate"], "%")
    print("Total focus minutes:", analytics["total_focus_minutes"])
    print("AI Insights generated:", len(analytics["insights"]))
    for ins in analytics["insights"]:
        print(f" * [{ins['insight_type']}] {ins['observation']} -> {ins['actionable_tip']}")

    print("\n--- 8. Testing Global Search ---")
    res = client.get("/api/search?q=DBMS", headers=headers)
    assert res.status_code == 200, res.text
    search_data = res.json()
    print(f"Global search for 'DBMS' returned {search_data['total_results']} items:")
    for item in search_data["items"]:
        print(f" - [{item['type']}] {item['title']} ({item['subtitle']})")

    print("\nALL BACKEND TESTS PASSED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    run_tests()

