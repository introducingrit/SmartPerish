
from pathlib import Path
import sys

# Add SmartPerish project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from webapp.app import app

print("\nSMARTPERISH - SYSTEM TESTING")
print("=" * 55)

client = app.test_client()

tests = [
    ("/", "Dashboard Homepage"),
    ("/api/health", "Backend Health"),
    ("/api/overview", "Overview API"),
    ("/api/forecast", "Forecast API"),
    ("/api/inventory", "Inventory API"),
    ("/api/distribution", "Distribution API"),
    ("/api/carbon", "Carbon API"),
    ("/static/css/style.css", "Dashboard CSS"),
    ("/static/js/dashboard.js", "Dashboard JavaScript")
]

passed = 0
failed = 0

for endpoint, description in tests:

    try:
        response = client.get(endpoint)

        success = response.status_code == 200

        if success:
            passed += 1
            status = "PASSED"
        else:
            failed += 1
            status = "FAILED"

        print(
            f"{description:<30} "
            f"{status:<10} "
            f"HTTP {response.status_code}"
        )

        if not success:
            print(
                "   Response:",
                response.get_data(as_text=True)[:250]
            )

        if endpoint.startswith("/api/") and success:
            if not response.is_json:
                print("   WARNING: Response is not JSON.")

    except Exception as error:

        failed += 1

        print(f"{description:<30} FAILED")
        print("   Error:", str(error))


print("\n" + "=" * 55)
print("SYSTEM TEST SUMMARY")
print("=" * 55)

print("Total tests:", len(tests))
print("Passed:", passed)
print("Failed:", failed)

if failed == 0:
    print("\nALL TESTS PASSED!")
else:
    print("\nSOME TESTS FAILED.")
    print("Check the errors above before proceeding.")

print("\nSMARTPERISH TESTING COMPLETED!")
