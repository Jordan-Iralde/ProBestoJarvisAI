# 🤝 Contributing to JarvisAI

> Guidelines for developing, testing, and contributing to JarvisAI

---

## 🚀 Getting Started

### 1. **Setup Development Environment**

```bash
# Clone repository
git clone https://github.com/your-username/ProBestoJarvisAI.git
cd ProBestoJarvisAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python jarvis/verify_phase_8_final.py
```

### 2. **Project Structure**
See [ARCHITECTURE.md](./architecture.md) for complete structure overview.

Key directories:
- `jarvis/core/` - Core system components
- `jarvis/jarvis_io/` - Input/output interfaces
- `jarvis/brain/` - NLU and intelligence
- `jarvis/skills/` - Skill implementations
- `jarvis/data/` - Data layer
- `jarvis/docs/` - Documentation

---

## 💡 Contributing Skills

### Creating a New Skill

**1. Create skill file:**
```
jarvis/skills/category/my_skill.py
```

**2. Implement skill:**
```python
from skills.base.skill import Skill

class MySkill(Skill):
    def __init__(self):
        self.name = "my_skill"
        self.description = "Brief description of what skill does"
        self.keywords = ["keyword1", "keyword2"]
    
    def execute(self, user_input: str, core=None) -> str:
        """
        Execute the skill
        
        Args:
            user_input: User's input text
            core: JarvisCore instance (optional)
        
        Returns:
            Response string to user
        """
        try:
            # Your implementation here
            result = self._process(user_input)
            
            # Log if core available
            if core:
                core.logger.logger.info(f"{self.name} executed successfully")
            
            return result
        except Exception as e:
            return f"Error in {self.name}: {str(e)}"
    
    def _process(self, user_input: str) -> str:
        """Helper method for processing"""
        # Implementation
        return "Result"
```

**3. Register in engine:**
Edit `system/core/engine.py`, in `_register_skills()`:
```python
from skills.category.my_skill import MySkill

skills = {
    # ... existing skills ...
    "my_skill": MySkill()
}
```

**4. Test skill:**
```bash
cd jarvis
python -c "from skills.category.my_skill import MySkill; s = MySkill(); print(s.execute('test'))"
```

### Skill Best Practices

- **Error handling**: Always wrap in try-except
- **Logging**: Use `core.logger` when available
- **Context**: Access `core.storage` for persistent data
- **Events**: Emit events via `core.events.publish()`
- **Documentation**: Include docstrings for all methods
- **Testing**: Test with various inputs
- **Performance**: Avoid blocking operations

---

## 🧪 Testing

### Running Tests
```bash
cd jarvis

# Quick import verification (10 tests)
python verify_phase_7_8.py

# Comprehensive system test (22 tests)
python verify_phase_8_final.py
```

### Writing Tests
Create test files in `jarvis/tests/`:

```python
# tests/test_my_feature.py
import unittest
from skills.category.my_skill import MySkill

class TestMySkill(unittest.TestCase):
    def setUp(self):
        self.skill = MySkill()
    
    def test_execute_basic(self):
        result = self.skill.execute("test input")
        self.assertIsNotNone(result)
    
    def test_execute_error_handling(self):
        result = self.skill.execute("")
        self.assertIn("Error", result)

if __name__ == '__main__':
    unittest.main()
```

---

## 📝 Code Style

### Python Style Guide
- Follow **PEP 8** standards
- Use type hints where possible
- Max line length: 100 characters
- Use docstrings for all classes and functions

### Naming Conventions
- Classes: `PascalCase` (e.g., `MySkill`)
- Functions/methods: `snake_case` (e.g., `my_function`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_WORKERS`)
- Private members: prefix with `_` (e.g., `_internal_method`)

### Documentation
```python
def my_function(param1: str, param2: int) -> str:
    """
    Brief description of function.
    
    Longer description if needed, explaining behavior,
    edge cases, or special considerations.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
    """
    pass
```

---

## 🔄 Git Workflow

### 1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

### 2. **Commit Changes**
```bash
git add .
git commit -m "Clear, descriptive commit message"
```

**Commit message format:**
```
<type>: <subject>

<body (optional)>

Fixes #<issue_number> (if applicable)
```

**Types:** feat, fix, docs, style, refactor, test, chore

**Example:**
```
feat: Add context awareness skill

Implement pattern learning from user interactions.
Predict next actions based on historical usage.

Fixes #42
```

### 3. **Push and Create PR**
```bash
git push origin feature/your-feature-name
```

Then create pull request on GitHub.

---

## ✅ Pull Request Checklist

Before submitting PR, ensure:
- [ ] Code follows PEP 8 style guide
- [ ] All tests pass (`verify_phase_8_final.py`)
- [ ] New code includes docstrings
- [ ] No breaking changes to existing APIs
- [ ] README/docs updated if needed
- [ ] Commit messages are clear
- [ ] No sensitive data in code
- [ ] All imports are used

---

## 🐛 Reporting Issues

### Issue Template
```markdown
## Description
Clear description of issue

## Steps to Reproduce
1. Run command X
2. Input Y
3. Observe Z

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows/Linux/Mac
- Python: 3.8/3.9/3.10
- JarvisAI: 0.0.4

## Screenshots
If applicable
```

---

## 📚 Documentation Updates

### When to Update Docs
- Adding new features → Update README.md and relevant docs
- Changing APIs → Update docs/api.md
- New architectural changes → Update docs/architecture.md
- Adding skills → Document in skills list

### Documentation Structure
JarvisAI maintains 4 core documentation files:

1. **README.md** - Overview and quick start
2. **docs/ARCHITECTURE.md** - System design
3. **docs/API.md** - API reference
4. **docs/CONTRIBUTING.md** - This file

---

## 🆘 Troubleshooting Development

### Issue: "Module not found" errors
```bash
# Ensure you're in jarvis directory
cd jarvis

# Reinstall dependencies
pip install -r ../requirements.txt
```

### Issue: Tests failing
```bash
# Check import paths
python -c "from system.core import JarvisCore; print('OK')"

# Run verbose test
python verify_phase_8_final.py
```

### Issue: Voice pipeline not available
- Check Vosk model installed
- Verify `jarvis_io` package imported correctly
- Check `config.json` has `voice_enabled: true`

### Issue: Skills not registering
- Check skill is registered in `_register_skills()`
- Verify class has `execute()` method
- Check for import errors: `python -c "from skills.category.skill import SkillClass"`

---

## 🎓 Learning Resources

- **Python Style**: https://peps.python.org/pep-0008/
- **Git Guide**: https://git-scm.com/doc
- **Python Best Practices**: https://docs.python-guide.org/

---

## 📞 Getting Help

1. Check existing issues and discussions
2. Review [ARCHITECTURE.md](./architecture.md) for design questions
3. Review [API.md](./api.md) for API questions
4. Open an issue with details
5. Discuss in pull request comments

---

## 🌟 Code Review Criteria

Your PR will be reviewed on:

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it clean, readable, maintainable?
- **Testing**: Are all scenarios covered?
- **Documentation**: Is it well documented?
- **Performance**: Does it impact system performance?
- **Security**: Are there any security issues?
- **Compatibility**: Does it work with existing code?

---

## 🎉 Contributor Recognition

Contributors are recognized in:
- GitHub contribution graph
- Project README acknowledgments
- Release notes

---

**Last Updated:** January 23, 2026
**Version:** 0.0.4

Thank you for contributing to JarvisAI! 🙏

- Keep functions short and modular.
- Document your code.

## 🧪 Tests
- Include unit tests for new features.
- Run all tests before submitting:
pytest


## 🚨 Reporting Bugs
Please use the templates in `.github/ISSUE_TEMPLATE/` to report issues properly.

---

Thank you for helping improve JarvisAI!
