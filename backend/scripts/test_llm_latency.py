#!/usr/bin/env python3
"""
Comprehensive LLM Latency Testing Script for FlavorLab

This script performs detailed latency and reliability testing of the Claude Haiku
LLM meal plan generation system, testing various scenarios and measuring:
- Response times
- Success/failure rates
- Token usage
- Validation errors
- API rate limiting behavior

Usage:
    python -m scripts.test_llm_latency
"""

import asyncio
import time
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.llm_service import generate_llm_meal_plan, LLMResponseError
from app.models.user import User
from app.database import SessionLocal


class LLMLatencyTester:
    """Comprehensive LLM latency and reliability tester"""

    def __init__(self):
        self.results = []
        self.errors = []

    def create_test_user(self, test_scenario: Dict[str, Any]) -> User:
        """Create a mock user for testing"""
        user = User(
            id=999,
            email="test@latency.com",
            username="latency_test",
            preferences={
                "health_goals": test_scenario.get("health_goals", [1, 2]),
                "survey_data": test_scenario.get("survey_data", {
                    "healthPillars": ["Increased Energy", "Improved Digestion"],
                    "dietaryRestrictions": test_scenario.get("diet", ["paleo"]),
                    "mealComplexity": test_scenario.get("complexity", "moderate"),
                    "dislikedIngredients": test_scenario.get("disliked", []),
                    "mealsPerDay": test_scenario.get("meals_per_day", "3-meals-2-snacks"),
                    "allergies": test_scenario.get("allergies", []),
                    "primaryGoal": test_scenario.get("goal", "General wellness")
                })
            }
        )
        return user

    async def test_single_request(
        self,
        user: User,
        scenario_name: str,
        include_recipes: bool = True,
        num_days: int = 1
    ) -> Dict[str, Any]:
        """Test a single LLM request and measure latency"""

        result = {
            "scenario": scenario_name,
            "timestamp": datetime.now().isoformat(),
            "include_recipes": include_recipes,
            "num_days": num_days,
            "success": False,
            "latency_ms": 0,
            "error": None
        }

        start_time = time.time()

        try:
            db = SessionLocal()
            meal_plans = await generate_llm_meal_plan(
                user=user,
                num_days=num_days,
                include_recipes=include_recipes,
                db=db
            )

            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            result["success"] = True
            result["latency_ms"] = round(latency_ms, 2)
            result["num_meals"] = len(meal_plans[0].meals) if meal_plans else 0

            db.close()

        except LLMResponseError as e:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            result["latency_ms"] = round(latency_ms, 2)
            result["error"] = str(e)
            result["error_type"] = "LLMResponseError"

        except Exception as e:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            result["latency_ms"] = round(latency_ms, 2)
            result["error"] = str(e)
            result["error_type"] = type(e).__name__

        return result

    async def test_scenario(
        self,
        scenario_name: str,
        test_config: Dict[str, Any],
        num_iterations: int = 3
    ):
        """Test a specific scenario multiple times"""

        print(f"\n{'='*80}")
        print(f"Testing Scenario: {scenario_name}")
        print(f"{'='*80}")
        print(f"Config: {json.dumps(test_config, indent=2)}")
        print(f"Iterations: {num_iterations}")
        print()

        user = self.create_test_user(test_config)

        for i in range(num_iterations):
            print(f"  Iteration {i+1}/{num_iterations}...", end=" ", flush=True)

            result = await self.test_single_request(
                user=user,
                scenario_name=scenario_name,
                include_recipes=test_config.get("include_recipes", True),
                num_days=test_config.get("num_days", 1)
            )

            self.results.append(result)

            if result["success"]:
                print(f"✅ Success ({result['latency_ms']}ms)")
            else:
                print(f"❌ Failed ({result['latency_ms']}ms) - {result['error_type']}")
                self.errors.append(result)

            # Add delay between requests to avoid rate limiting
            if i < num_iterations - 1:
                await asyncio.sleep(2)

    async def run_all_tests(self):
        """Run comprehensive test suite"""

        print("\n" + "="*80)
        print(" FLAVORLAB LLM LATENCY & RELIABILITY TEST SUITE")
        print("="*80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Test Scenario 1: Simple paleo diet
        await self.test_scenario(
            "Simple Paleo Diet",
            {
                "diet": ["paleo"],
                "allergies": [],
                "disliked": [],
                "health_goals": [1, 2],
                "include_recipes": True,
                "num_days": 1
            },
            num_iterations=5
        )

        # Test Scenario 2: Complex restrictions (multiple allergies)
        await self.test_scenario(
            "Complex Allergies + Pescatarian",
            {
                "diet": ["pescatarian"],
                "allergies": ["Shellfish", "Soy", "Gluten"],
                "disliked": ["salmon"],
                "health_goals": [3, 5, 6],
                "include_recipes": True,
                "num_days": 1
            },
            num_iterations=5
        )

        # Test Scenario 3: Vegetarian with multiple disliked ingredients
        await self.test_scenario(
            "Vegetarian + Multiple Dislikes",
            {
                "diet": ["vegetarian"],
                "allergies": ["Dairy"],
                "disliked": ["tomatoes", "mushrooms", "onions"],
                "health_goals": [1, 4, 8],
                "include_recipes": True,
                "num_days": 1
            },
            num_iterations=5
        )

        # Test Scenario 4: Keto diet (low carb)
        await self.test_scenario(
            "Keto Diet",
            {
                "diet": ["keto"],
                "allergies": ["Peanuts"],
                "disliked": [],
                "health_goals": [1, 7],
                "include_recipes": True,
                "num_days": 1
            },
            num_iterations=5
        )

        # Test Scenario 5: Without recipes (faster)
        await self.test_scenario(
            "Paleo - No Recipes",
            {
                "diet": ["paleo"],
                "allergies": [],
                "disliked": [],
                "health_goals": [1, 2],
                "include_recipes": False,
                "num_days": 1
            },
            num_iterations=3
        )

        # Test Scenario 6: Stress test - rapid fire requests
        print(f"\n{'='*80}")
        print("Stress Test: Rapid Fire Requests")
        print(f"{'='*80}\n")

        user = self.create_test_user({
            "diet": ["mediterranean"],
            "allergies": [],
            "disliked": [],
            "health_goals": [1, 6]
        })

        stress_tasks = []
        for i in range(5):
            task = self.test_single_request(
                user=user,
                scenario_name="Stress Test - Concurrent",
                include_recipes=True,
                num_days=1
            )
            stress_tasks.append(task)

        print("  Sending 5 concurrent requests...")
        stress_results = await asyncio.gather(*stress_tasks, return_exceptions=True)

        for i, result in enumerate(stress_results):
            if isinstance(result, Exception):
                print(f"  Request {i+1}: ❌ Exception - {str(result)}")
            elif result["success"]:
                print(f"  Request {i+1}: ✅ Success ({result['latency_ms']}ms)")
                self.results.append(result)
            else:
                print(f"  Request {i+1}: ❌ Failed - {result['error_type']}")
                self.results.append(result)
                self.errors.append(result)

    def generate_report(self):
        """Generate comprehensive test report"""

        print("\n" + "="*80)
        print(" TEST RESULTS SUMMARY")
        print("="*80)

        successful_results = [r for r in self.results if r["success"]]
        failed_results = [r for r in self.results if not r["success"]]

        print(f"\nTotal Requests: {len(self.results)}")
        print(f"Successful: {len(successful_results)} ({len(successful_results)/len(self.results)*100:.1f}%)")
        print(f"Failed: {len(failed_results)} ({len(failed_results)/len(self.results)*100:.1f}%)")

        if successful_results:
            latencies = [r["latency_ms"] for r in successful_results]

            print(f"\n{'─'*40}")
            print("Latency Statistics (Successful Requests)")
            print(f"{'─'*40}")
            print(f"  Mean:     {statistics.mean(latencies):.2f}ms")
            print(f"  Median:   {statistics.median(latencies):.2f}ms")
            print(f"  Min:      {min(latencies):.2f}ms")
            print(f"  Max:      {max(latencies):.2f}ms")
            if len(latencies) > 1:
                print(f"  Std Dev:  {statistics.stdev(latencies):.2f}ms")

        if failed_results:
            print(f"\n{'─'*40}")
            print("Error Analysis")
            print(f"{'─'*40}")

            error_types = {}
            for error in failed_results:
                error_type = error.get("error_type", "Unknown")
                error_types[error_type] = error_types.get(error_type, 0) + 1

            for error_type, count in error_types.items():
                print(f"  {error_type}: {count}")

            print(f"\n{'─'*40}")
            print("Sample Errors (first 3)")
            print(f"{'─'*40}")
            for i, error in enumerate(failed_results[:3]):
                print(f"\n  Error {i+1}:")
                print(f"    Scenario: {error['scenario']}")
                print(f"    Type: {error['error_type']}")
                print(f"    Message: {error['error'][:200]}...")

        # Save detailed results to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"/home/holberton/FlavorLab/backend/llm_latency_report_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_requests": len(self.results),
                    "successful": len(successful_results),
                    "failed": len(failed_results),
                    "success_rate": len(successful_results)/len(self.results)*100 if self.results else 0
                },
                "latency_stats": {
                    "mean": statistics.mean(latencies) if successful_results else None,
                    "median": statistics.median(latencies) if successful_results else None,
                    "min": min(latencies) if successful_results else None,
                    "max": max(latencies) if successful_results else None,
                    "stdev": statistics.stdev(latencies) if len(latencies) > 1 else None
                },
                "detailed_results": self.results,
                "errors": self.errors
            }, f, indent=2)

        print(f"\n{'='*80}")
        print(f"Detailed report saved to: {report_file}")
        print(f"{'='*80}\n")


async def main():
    """Main test execution"""
    tester = LLMLatencyTester()

    try:
        await tester.run_all_tests()
        tester.generate_report()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        tester.generate_report()
    except Exception as e:
        print(f"\n\nFatal error during testing: {e}")
        import traceback
        traceback.print_exc()
        tester.generate_report()


if __name__ == "__main__":
    asyncio.run(main())
