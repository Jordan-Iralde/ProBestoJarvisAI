# skills/auto_programming.py
"""
Auto Programming Skill - Jarvis self-improvement proposals
Analyzes JarvisAI behavior and proposes code improvements without auto-execution.
All changes require explicit user approval.
"""

import os
import re
from typing import Dict, Any, List
from datetime import datetime
import json


class AutoProgrammingSkill:
    """
    Skill for proposing self-improvements to JarvisAI.
    Analyzes code, identifies issues, and suggests improvements safely.
    NEVER executes code automatically - only proposes changes.
    """

    def __init__(self, storage=None, active_learning=None, logger=None):
        self.storage = storage
        self.active_learning = active_learning
        self.logger = logger
        self.jarvis_root = self._find_jarvis_root()
        self.proposals_file = os.path.join(self.jarvis_root, 'data', 'improvement_proposals.json')
        self._ensure_proposals_file()

    def run(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute auto-programming analysis commands (read-only).

        Args:
            command: The analysis command ("analyze", "propose_improvements", "review_proposals", "get_proposal")
            **kwargs: Additional parameters for the command

        Returns:
            Analysis results or proposal information
        """
        try:
            if command == "analyze":
                return self._analyze_codebase()
            elif command == "propose_improvements":
                return self._propose_improvements()
            elif command == "review_proposals":
                return self._review_proposals()
            elif command == "get_proposal":
                return self._get_proposal(kwargs.get("proposal_id", ""))
            elif command == "approve_proposal":
                return self._approve_proposal(kwargs.get("proposal_id", ""))
            elif command == "reject_proposal":
                return self._reject_proposal(kwargs.get("proposal_id", ""))
            else:
                return {
                    "success": False,
                    "error": f"Comando desconocido: {command}",
                    "available_commands": ["analyze", "propose_improvements", "review_proposals", "get_proposal", "approve_proposal", "reject_proposal"]
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en auto-programación: {str(e)}",
                "command": command
            }

    def _find_jarvis_root(self) -> str:
        """Find the Jarvis root directory"""
        current = os.path.dirname(os.path.abspath(__file__))
        # Go up until we find the jarvis directory
        while current and os.path.basename(current) != 'jarvis':
            current = os.path.dirname(current)
        return current or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _ensure_proposals_file(self):
        """Ensure the proposals file exists"""
        os.makedirs(os.path.dirname(self.proposals_file), exist_ok=True)
        if not os.path.exists(self.proposals_file):
            with open(self.proposals_file, 'w', encoding='utf-8') as f:
                json.dump({"proposals": [], "next_id": 1}, f, indent=2)

    def _load_proposals(self) -> Dict[str, Any]:
        """Load proposals from file"""
        try:
            with open(self.proposals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"proposals": [], "next_id": 1}

    def _save_proposals(self, data: Dict[str, Any]):
        """Save proposals to file"""
        with open(self.proposals_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the current codebase structure and health (read-only)"""
        analysis = {
            "total_files": 0,
            "total_lines": 0,
            "languages": {},
            "skills_count": 0,
            "test_coverage": 0,
            "issues": [],
            "recommendations": [],
            "security_concerns": []
        }

        try:
            for root, dirs, files in os.walk(self.jarvis_root):
                # Skip certain directories for security
                if any(skip in root for skip in ['__pycache__', '.git', 'node_modules']):
                    continue

                for file in files:
                    if file.endswith(('.py', '.js', '.html', '.css', '.md')):
                        filepath = os.path.join(root, file)
                        analysis["total_files"] += 1

                        # Count lines
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                analysis["total_lines"] += len(lines)
                        except:
                            pass

                        # Language detection
                        ext = os.path.splitext(file)[1]
                        analysis["languages"][ext] = analysis["languages"].get(ext, 0) + 1

                        # Count skills
                        if 'skills/' in root and file.endswith('.py') and not file.startswith('__'):
                            analysis["skills_count"] += 1

                        # Security analysis
                        if file.endswith('.py'):
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    content = f.read()

                                # Check for security issues
                                if 'eval(' in content:
                                    analysis["security_concerns"].append(f"eval() usage in {file} - potential security risk")
                                if 'exec(' in content:
                                    analysis["security_concerns"].append(f"exec() usage in {file} - potential security risk")
                                if 'subprocess' in content and 'shell=True' in content:
                                    analysis["security_concerns"].append(f"shell=True in subprocess call in {file}")

                            except:
                                pass

            # Generate recommendations
            if analysis["skills_count"] < 10:
                analysis["recommendations"].append("Consider expanding the available skill set")

            if analysis["total_lines"] > 10000:
                analysis["recommendations"].append("Codebase is growing - consider additional modularization")

            if '.py' in analysis["languages"] and analysis["languages"]['.py'] > 20:
                analysis["issues"].append("Multiple Python files - ensure code style consistency")

            if not analysis["security_concerns"]:
                analysis["security_concerns"].append("No immediate security concerns detected")

            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error analyzing codebase: {str(e)}"
            }

    def _propose_improvements(self) -> Dict[str, Any]:
        """Generate improvement proposals based on analysis"""
        proposals = []

        try:
            # Get analysis data
            analysis_result = self._analyze_codebase()
            if not analysis_result["success"]:
                return analysis_result

            analysis = analysis_result["analysis"]

            # Generate skill improvement proposals
            if analysis["skills_count"] < 15:
                proposals.append({
                    "id": None,  # Will be set when saved
                    "type": "new_skill",
                    "title": "Expand Core Skills",
                    "description": f"Add {15 - analysis['skills_count']} new skills to enhance JarvisAI capabilities",
                    "priority": "medium",
                    "category": "functionality",
                    "proposed_changes": [
                        "Identify common user needs not covered by current skills",
                        "Create new skill templates for missing functionality",
                        "Ensure new skills follow security guidelines"
                    ],
                    "estimated_effort": "medium",
                    "risk_level": "low",
                    "status": "proposed",
                    "created_at": datetime.now().isoformat()
                })

            # Code quality improvements
            if analysis["issues"]:
                proposals.append({
                    "id": None,
                    "type": "code_quality",
                    "title": "Address Code Quality Issues",
                    "description": f"Fix {len(analysis['issues'])} identified code quality issues",
                    "priority": "high",
                    "category": "maintenance",
                    "proposed_changes": analysis["issues"],
                    "estimated_effort": "low",
                    "risk_level": "low",
                    "status": "proposed",
                    "created_at": datetime.now().isoformat()
                })

            # Security improvements
            if analysis["security_concerns"]:
                security_issues = [issue for issue in analysis["security_concerns"] if "No immediate" not in issue]
                if security_issues:
                    proposals.append({
                        "id": None,
                        "type": "security",
                        "title": "Address Security Concerns",
                        "description": f"Fix {len(security_issues)} potential security vulnerabilities",
                        "priority": "critical",
                        "category": "security",
                        "proposed_changes": security_issues,
                        "estimated_effort": "high",
                        "risk_level": "medium",
                        "status": "proposed",
                        "created_at": datetime.now().isoformat()
                    })

            # Performance optimizations
            if analysis["total_lines"] > 5000:
                proposals.append({
                    "id": None,
                    "type": "performance",
                    "title": "Performance Optimization",
                    "description": "Optimize codebase performance and memory usage",
                    "priority": "medium",
                    "category": "performance",
                    "proposed_changes": [
                        "Implement caching for repeated operations",
                        "Optimize database queries with proper indexing",
                        "Review and optimize memory-intensive operations"
                    ],
                    "estimated_effort": "medium",
                    "risk_level": "low",
                    "status": "proposed",
                    "created_at": datetime.now().isoformat()
                })

            # Save proposals
            data = self._load_proposals()
            for proposal in proposals:
                proposal["id"] = f"prop_{data['next_id']}"
                data["proposals"].append(proposal)
                data["next_id"] += 1

            self._save_proposals(data)

            return {
                "success": True,
                "message": f"Generated {len(proposals)} improvement proposals",
                "proposals_count": len(proposals),
                "proposals": [{"id": p["id"], "title": p["title"], "priority": p["priority"]} for p in proposals]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating proposals: {str(e)}"
            }

    def _review_proposals(self) -> Dict[str, Any]:
        """Review all pending proposals"""
        try:
            data = self._load_proposals()
            proposals = data["proposals"]

            # Group by status
            pending = [p for p in proposals if p["status"] == "proposed"]
            approved = [p for p in proposals if p["status"] == "approved"]
            rejected = [p for p in proposals if p["status"] == "rejected"]

            return {
                "success": True,
                "summary": {
                    "total": len(proposals),
                    "pending": len(pending),
                    "approved": len(approved),
                    "rejected": len(rejected)
                },
                "pending_proposals": [
                    {
                        "id": p["id"],
                        "title": p["title"],
                        "type": p["type"],
                        "priority": p["priority"],
                        "category": p["category"],
                        "created_at": p["created_at"]
                    } for p in pending
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error reviewing proposals: {str(e)}"
            }

    def _get_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific proposal"""
        if not proposal_id:
            return {
                "success": False,
                "error": "Proposal ID is required"
            }

        try:
            data = self._load_proposals()
            proposal = next((p for p in data["proposals"] if p["id"] == proposal_id), None)

            if not proposal:
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} not found"
                }

            return {
                "success": True,
                "proposal": proposal
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting proposal: {str(e)}"
            }

    def _approve_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Mark a proposal as approved (requires manual implementation)"""
        if not proposal_id:
            return {
                "success": False,
                "error": "Proposal ID is required"
            }

        try:
            data = self._load_proposals()
            proposal = next((p for p in data["proposals"] if p["id"] == proposal_id), None)

            if not proposal:
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} not found"
                }

            if proposal["status"] != "proposed":
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} is already {proposal['status']}"
                }

            proposal["status"] = "approved"
            proposal["approved_at"] = datetime.now().isoformat()

            self._save_proposals(data)

            return {
                "success": True,
                "message": f"Proposal {proposal_id} approved. Manual implementation required.",
                "next_steps": [
                    "Review the proposed changes carefully",
                    "Implement changes manually in the codebase",
                    "Test thoroughly before deployment",
                    "Update proposal status after implementation"
                ],
                "proposal": proposal
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error approving proposal: {str(e)}"
            }

    def _reject_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Mark a proposal as rejected with reason"""
        if not proposal_id:
            return {
                "success": False,
                "error": "Proposal ID is required"
            }

        try:
            data = self._load_proposals()
            proposal = next((p for p in data["proposals"] if p["id"] == proposal_id), None)

            if not proposal:
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} not found"
                }

            if proposal["status"] != "proposed":
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} is already {proposal['status']}"
                }

            proposal["status"] = "rejected"
            proposal["rejected_at"] = datetime.now().isoformat()

            self._save_proposals(data)

            return {
                "success": True,
                "message": f"Proposal {proposal_id} rejected.",
                "proposal": proposal
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error rejecting proposal: {str(e)}"
            }

    def _find_jarvis_root(self) -> str:
        """Find the Jarvis root directory"""
        current = os.path.dirname(os.path.abspath(__file__))
        # Go up until we find the jarvis directory
        while current and os.path.basename(current) != 'jarvis':
            current = os.path.dirname(current)
        return current or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _ensure_proposals_file(self):
        """Ensure the proposals file exists"""
        os.makedirs(os.path.dirname(self.proposals_file), exist_ok=True)
        if not os.path.exists(self.proposals_file):
            with open(self.proposals_file, 'w', encoding='utf-8') as f:
                json.dump({"proposals": [], "next_id": 1}, f, indent=2)

    def _load_proposals(self) -> Dict[str, Any]:
        """Load proposals from file"""
        try:
            with open(self.proposals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"proposals": [], "next_id": 1}

    def _save_proposals(self, data: Dict[str, Any]):
        """Save proposals to file"""
        with open(self.proposals_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the current codebase structure and health (read-only)"""
        analysis = {
            "total_files": 0,
            "total_lines": 0,
            "languages": {},
            "skills_count": 0,
            "test_coverage": 0,
            "issues": [],
            "recommendations": [],
            "security_concerns": []
        }

        try:
            for root, dirs, files in os.walk(self.jarvis_root):
                # Skip certain directories for security
                if any(skip in root for skip in ['__pycache__', '.git', 'node_modules']):
                    continue

                for file in files:
                    if file.endswith(('.py', '.js', '.html', '.css', '.md')):
                        filepath = os.path.join(root, file)
                        analysis["total_files"] += 1

                        # Count lines
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                analysis["total_lines"] += len(lines)
                        except:
                            pass

                        # Language detection
                        ext = os.path.splitext(file)[1]
                        analysis["languages"][ext] = analysis["languages"].get(ext, 0) + 1

                        # Count skills
                        if 'skills/' in root and file.endswith('.py') and not file.startswith('__'):
                            analysis["skills_count"] += 1

                        # Security analysis
                        if file.endswith('.py'):
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    content = f.read()

                                # Check for security issues
                                if 'eval(' in content:
                                    analysis["security_concerns"].append(f"eval() usage in {file} - potential security risk")
                                if 'exec(' in content:
                                    analysis["security_concerns"].append(f"exec() usage in {file} - potential security risk")
                                if 'subprocess' in content and 'shell=True' in content:
                                    analysis["security_concerns"].append(f"shell=True in subprocess call in {file}")

                            except:
                                pass

            # Generate recommendations
            if analysis["skills_count"] < 10:
                analysis["recommendations"].append("Consider expanding the available skill set")

            if analysis["total_lines"] > 10000:
                analysis["recommendations"].append("Codebase is growing - consider additional modularization")

            if '.py' in analysis["languages"] and analysis["languages"]['.py'] > 20:
                analysis["issues"].append("Multiple Python files - ensure code style consistency")

            if not analysis["security_concerns"]:
                analysis["security_concerns"].append("No immediate security concerns detected")

            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error analyzing codebase: {str(e)}"
            }

    def _propose_improvements(self) -> Dict[str, Any]:
        """Generate improvement proposals based on analysis"""
        proposals = []

        try:
            # Get analysis data
            analysis_result = self._analyze_codebase()
            if not analysis_result["success"]:
                return analysis_result

            analysis = analysis_result["analysis"]

            # Generate skill improvement proposals
            if analysis["skills_count"] < 15:
                proposals.append({
                    "id": None,  # Will be set when saved
                    "type": "new_skill",
                    "title": "Expand Core Skills",
                    "description": f"Add {15 - analysis['skills_count']} new skills to enhance JarvisAI capabilities",
                    "priority": "medium",
                    "category": "functionality",
                    "proposed_changes": [
                        "Identify common user needs not covered by current skills",
                        "Create new skill templates for missing functionality",
                        "Ensure new skills follow security guidelines"
                    ],
                    "estimated_effort": "medium",
                    "risk_level": "low",
                    "status": "proposed",
                    "created_at": datetime.now().isoformat()
                })

            # Code quality improvements
            if analysis["issues"]:
                proposals.append({
                    "id": None,
                    "type": "code_quality",
                    "title": "Address Code Quality Issues",
                    "description": f"Fix {len(analysis['issues'])} identified code quality issues",
                    "priority": "high",
                    "category": "maintenance",
                    "proposed_changes": analysis["issues"],
                    "estimated_effort": "low",
                    "risk_level": "low",
                    "status": "proposed",
                    "created_at": datetime.now().isoformat()
                })

            # Security improvements
            if analysis["security_concerns"]:
                security_issues = [issue for issue in analysis["security_concerns"] if "No immediate" not in issue]
                if security_issues:
                    proposals.append({
                        "id": None,
                        "type": "security",
                        "title": "Address Security Concerns",
                        "description": f"Fix {len(security_issues)} potential security vulnerabilities",
                        "priority": "critical",
                        "category": "security",
                        "proposed_changes": security_issues,
                        "estimated_effort": "high",
                        "risk_level": "medium",
                        "status": "proposed",
                        "created_at": datetime.now().isoformat()
                    })

            # Performance optimizations
            if analysis["total_lines"] > 5000:
                proposals.append({
                    "id": None,
                    "type": "performance",
                    "title": "Performance Optimization",
                    "description": "Optimize codebase performance and memory usage",
                    "priority": "medium",
                    "category": "performance",
                    "proposed_changes": [
                        "Implement caching for repeated operations",
                        "Optimize database queries with proper indexing",
                        "Review and optimize memory-intensive operations"
                    ],
                    "estimated_effort": "medium",
                    "risk_level": "low",
                    "status": "proposed",
                    "created_at": datetime.now().isoformat()
                })

            # Save proposals
            data = self._load_proposals()
            for proposal in proposals:
                proposal["id"] = f"prop_{data['next_id']}"
                data["proposals"].append(proposal)
                data["next_id"] += 1

            self._save_proposals(data)

            return {
                "success": True,
                "message": f"Generated {len(proposals)} improvement proposals",
                "proposals_count": len(proposals),
                "proposals": [{"id": p["id"], "title": p["title"], "priority": p["priority"]} for p in proposals]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating proposals: {str(e)}"
            }

    def _review_proposals(self) -> Dict[str, Any]:
        """Review all pending proposals"""
        try:
            data = self._load_proposals()
            proposals = data["proposals"]

            # Group by status
            pending = [p for p in proposals if p["status"] == "proposed"]
            approved = [p for p in proposals if p["status"] == "approved"]
            rejected = [p for p in proposals if p["status"] == "rejected"]

            return {
                "success": True,
                "summary": {
                    "total": len(proposals),
                    "pending": len(pending),
                    "approved": len(approved),
                    "rejected": len(rejected)
                },
                "pending_proposals": [
                    {
                        "id": p["id"],
                        "title": p["title"],
                        "type": p["type"],
                        "priority": p["priority"],
                        "category": p["category"],
                        "created_at": p["created_at"]
                    } for p in pending
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error reviewing proposals: {str(e)}"
            }

    def _get_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific proposal"""
        if not proposal_id:
            return {
                "success": False,
                "error": "Proposal ID is required"
            }

        try:
            data = self._load_proposals()
            proposal = next((p for p in data["proposals"] if p["id"] == proposal_id), None)

            if not proposal:
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} not found"
                }

            return {
                "success": True,
                "proposal": proposal
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting proposal: {str(e)}"
            }

    def _approve_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Mark a proposal as approved (requires manual implementation)"""
        if not proposal_id:
            return {
                "success": False,
                "error": "Proposal ID is required"
            }

        try:
            data = self._load_proposals()
            proposal = next((p for p in data["proposals"] if p["id"] == proposal_id), None)

            if not proposal:
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} not found"
                }

            if proposal["status"] != "proposed":
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} is already {proposal['status']}"
                }

            proposal["status"] = "approved"
            proposal["approved_at"] = datetime.now().isoformat()

            self._save_proposals(data)

            return {
                "success": True,
                "message": f"Proposal {proposal_id} approved. Manual implementation required.",
                "next_steps": [
                    "Review the proposed changes carefully",
                    "Implement changes manually in the codebase",
                    "Test thoroughly before deployment",
                    "Update proposal status after implementation"
                ],
                "proposal": proposal
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error approving proposal: {str(e)}"
            }

    def _reject_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Mark a proposal as rejected with reason"""
        if not proposal_id:
            return {
                "success": False,
                "error": "Proposal ID is required"
            }

        try:
            data = self._load_proposals()
            proposal = next((p for p in data["proposals"] if p["id"] == proposal_id), None)

            if not proposal:
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} not found"
                }

            if proposal["status"] != "proposed":
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} is already {proposal['status']}"
                }

            proposal["status"] = "rejected"
            proposal["rejected_at"] = datetime.now().isoformat()

            self._save_proposals(data)

            return {
                "success": True,
                "message": f"Proposal {proposal_id} rejected.",
                "proposal": proposal
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error rejecting proposal: {str(e)}"
            }