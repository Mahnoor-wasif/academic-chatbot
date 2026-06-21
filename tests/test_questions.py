import requests
import time

BASE_URL = "http://127.0.0.1:5000/chat"

test_questions = [
    # Attendance Policy
    {"id": 1, "question": "What is the attendance policy?", "category": "Attendance"},
    {"id": 2, "question": "How many absences are allowed per semester?", "category": "Attendance"},
    {"id": 3, "question": "What happens if a student misses more than allowed classes?", "category": "Attendance"},

    # Grading Policy
    {"id": 4, "question": "What is the grading policy?", "category": "Grading"},
    {"id": 5, "question": "How is the final grade calculated?", "category": "Grading"},
    {"id": 6, "question": "What is the minimum passing grade?", "category": "Grading"},
    {"id": 7, "question": "Can a student repeat a failed course?", "category": "Grading"},

    # Examination Policy
    {"id": 8, "question": "What is the exam policy?", "category": "Examination"},
    {"id": 9, "question": "What happens if a student misses an exam?", "category": "Examination"},
    {"id": 10, "question": "Are makeup exams allowed?", "category": "Examination"},
    {"id": 11, "question": "What are the rules during examinations?", "category": "Examination"},

    # Academic Integrity
    {"id": 12, "question": "What is the plagiarism policy?", "category": "Academic Integrity"},
    {"id": 13, "question": "What are the consequences of cheating?", "category": "Academic Integrity"},
    {"id": 14, "question": "How is academic dishonesty handled?", "category": "Academic Integrity"},

    # Fee & Scholarship
    {"id": 15, "question": "What is the fee refund policy?", "category": "Fee"},
    {"id": 16, "question": "Are there any scholarships available?", "category": "Scholarship"},
    {"id": 17, "question": "What is the deadline for fee submission?", "category": "Fee"},

    # General
    {"id": 18, "question": "What is the leave of absence policy?", "category": "General"},
    {"id": 19, "question": "How can a student apply for re-checking of marks?", "category": "General"},
    {"id": 20, "question": "What is the dress code policy?", "category": "General"},
]


def run_tests():
    print("=" * 60)
    print("Academic Chatbot - Test Evaluation")
    print("=" * 60)

    passed = 0
    failed = 0
    results = []

    for test in test_questions:
        try:
            start_time = time.time()
            response = requests.post(BASE_URL, json={"message": test["question"]})
            latency = round((time.time() - start_time) * 1000)

            data = response.json()
            answer = data.get("answer", "")
            sources = data.get("sources", [])

            has_answer = len(answer) > 20
            has_sources = len(sources) > 0
            not_error = "went wrong" not in answer.lower() and "not found" not in answer.lower()

            status = "PASS" if (has_answer and not_error) else "FAIL"
            if status == "PASS":
                passed += 1
            else:
                failed += 1

            results.append({
                "id": test["id"],
                "category": test["category"],
                "question": test["question"],
                "status": status,
                "latency_ms": latency,
                "has_sources": has_sources,
                "answer_preview": answer[:80] + "..." if len(answer) > 80 else answer
            })

            print(f"[{status}] Q{test['id']} ({test['category']}) - {latency}ms")
            print(f"  Q: {test['question']}")
            print(f"  A: {results[-1]['answer_preview']}")
            print()

        except Exception as e:
            failed += 1
            print(f"[ERROR] Q{test['id']}: {e}")

    print("=" * 60)
    print(f"Results: {passed} PASSED / {failed} FAILED / {len(test_questions)} TOTAL")
    print(f"Pass Rate: {round(passed/len(test_questions)*100)}%")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()