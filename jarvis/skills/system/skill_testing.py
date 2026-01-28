# skills/system/skill_testing.py
"""
Skill Testing Framework - Test and verify each skill works correctly
User trains Jarvis by validating skill results
"""

import time
from typing import Dict, List, Any, Callable
from skills.actions.base.skill import Skill


class SkillTestCase:
    """Single test case for a skill"""
    
    def __init__(self, skill_name: str, input_text: str, expected_intent: str, 
                 entities: Dict = None, should_succeed: bool = True):
        self.skill_name = skill_name
        self.input_text = input_text
        self.expected_intent = expected_intent
        self.entities = entities or {}
        self.should_succeed = should_succeed
        self.result = None
        self.passed = False
        self.execution_time = 0.0
        self.feedback = ""
    
    def execute(self, dispatcher) -> bool:
        """Execute the test case"""
        start = time.time()
        
        try:
            self.result = dispatcher.dispatch(self.expected_intent, self.entities)
            self.execution_time = time.time() - start
            
            # Verify result
            if self.should_succeed:
                self.passed = self.result and self.result.get("success", False)
            else:
                self.passed = self.result and not self.result.get("success", True)
            
            return self.passed
        
        except Exception as e:
            self.result = {"error": str(e)}
            self.execution_time = time.time() - start
            self.passed = not self.should_succeed  # Expected to fail
            return self.passed


class SkillTestSuite:
    """Test suite for multiple skills"""
    
    def __init__(self):
        self.test_cases: List[SkillTestCase] = []
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "execution_time": 0.0,
            "details": []
        }
    
    def add_test(self, test_case: SkillTestCase) -> None:
        """Add test case"""
        self.test_cases.append(test_case)
    
    def add_test_batch(self, tests: List[SkillTestCase]) -> None:
        """Add multiple test cases"""
        self.test_cases.extend(tests)
    
    def run(self, dispatcher) -> Dict:
        """Run all tests"""
        start_time = time.time()
        
        for test in self.test_cases:
            test.execute(dispatcher)
            
            self.results["total"] += 1
            if test.passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
            
            self.results["details"].append({
                "skill": test.skill_name,
                "input": test.input_text,
                "passed": test.passed,
                "time_ms": test.execution_time * 1000,
                "result": test.result
            })
        
        self.results["execution_time"] = time.time() - start_time
        self.results["pass_rate"] = (self.results["passed"] / max(1, self.results["total"])) * 100
        
        return self.results
    
    def get_report(self) -> str:
        """Get formatted test report"""
        report = f"""
╔════════════════════════════════════════════════════════╗
║           SKILL TEST REPORT                           ║
╚════════════════════════════════════════════════════════╝

Total Tests: {self.results['total']}
Passed: {self.results['passed']} ✓
Failed: {self.results['failed']} ✗
Pass Rate: {self.results.get('pass_rate', 0):.1f}%
Total Time: {self.results['execution_time']:.2f}s

DETAILS:
"""
        for detail in self.results["details"]:
            status = "✓" if detail["passed"] else "✗"
            report += f"\n{status} {detail['skill']}: {detail['input']}"
            report += f"\n   Time: {detail['time_ms']:.1f}ms"
            if not detail["passed"]:
                report += f"\n   Error: {detail['result']}"
        
        return report


class SkillTestingSkill(Skill):
    """Skill to test other skills interactively"""
    
    patterns = [
        r".*test.*skill.*",
        r".*probar.*skill.*",
        r".*verificar.*",
        r".*validate.*",
    ]
    
    def __init__(self):
        self.name = "skill_testing"
        self.test_suite = SkillTestSuite()
        self.test_history = []
    
    def run(self, entities, core=None):
        """Run skill testing"""
        
        action = entities.get("action", ["list"])[0] if entities.get("action") else "list"
        
        if action in ["list", "listar"]:
            return self._list_skills(core)
        elif action in ["test", "probar"]:
            return self._test_skill(entities, core)
        elif action in ["report", "reporte"]:
            return self._get_report()
        else:
            return {"success": True, "message": "Testing framework ready"}
    
    def _list_skills(self, core) -> Dict:
        """List available skills"""
        if not core or not hasattr(core, 'skill_dispatcher'):
            return {"success": False, "error": "No skill dispatcher available"}
        
        skills = list(core.skill_dispatcher.skills.keys())
        
        return {
            "success": True,
            "skills": skills,
            "count": len(skills),
            "message": f"Available skills: {', '.join(skills)}"
        }
    
    def _test_skill(self, entities, core) -> Dict:
        """Test a specific skill"""
        
        if not entities.get("skill_name"):
            return {"success": False, "error": "Skill name required"}
        
        skill_name = entities["skill_name"][0]
        
        if not core or not hasattr(core, 'skill_dispatcher'):
            return {"success": False, "error": "No dispatcher"}
        
        if skill_name not in core.skill_dispatcher.skills:
            return {"success": False, "error": f"Skill not found: {skill_name}"}
        
        # Create test case
        test_input = entities.get("test_input", [""])[0]
        test_case = SkillTestCase(skill_name, test_input, skill_name)
        
        # Run test
        suite = SkillTestSuite()
        suite.add_test(test_case)
        results = suite.run(core.skill_dispatcher)
        
        self.test_history.append(results)
        
        return {
            "success": results["passed"] > 0,
            "skill": skill_name,
            "results": results,
            "report": suite.get_report()
        }
    
    def _get_report(self) -> Dict:
        """Get accumulated test report"""
        
        if not self.test_history:
            return {"message": "No tests run yet"}
        
        total_passed = sum(r["passed"] for r in self.test_history)
        total_failed = sum(r["failed"] for r in self.test_history)
        total_time = sum(r["execution_time"] for r in self.test_history)
        
        return {
            "success": True,
            "total_tests_run": len(self.test_history),
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_time": total_time,
            "history": self.test_history[:10]  # Last 10
        }


# Pre-built test suites for common skills

def create_open_app_tests() -> List[SkillTestCase]:
    """Test cases for open_app skill"""
    return [
        SkillTestCase("open_app", "abrir chrome", "open_app", {"app": ["chrome"]}, True),
        SkillTestCase("open_app", "abre edge", "open_app", {"app": ["edge"]}, True),
        SkillTestCase("open_app", "open notepad", "open_app", {"app": ["notepad"]}, True),
        SkillTestCase("open_app", "explorer", "open_app", {"app": ["explorer"]}, True),
    ]


def create_system_status_tests() -> List[SkillTestCase]:
    """Test cases for system_status skill"""
    return [
        SkillTestCase("system_status", "estado", "system_status", {}, True),
        SkillTestCase("system_status", "info del sistema", "system_status", {}, True),
    ]


def create_get_time_tests() -> List[SkillTestCase]:
    """Test cases for get_time skill"""
    return [
        SkillTestCase("get_time", "que hora es", "get_time", {}, True),
        SkillTestCase("get_time", "dime la hora", "get_time", {}, True),
        SkillTestCase("get_time", "hora actual", "get_time", {}, True),
    ]
