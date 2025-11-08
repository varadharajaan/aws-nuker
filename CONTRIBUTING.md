# Contributing to AWS Nuker

Thank you for your interest in contributing to AWS Nuker! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and professional
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/varadharajaan/aws-nuker/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - AWS Nuker version
   - Python version
   - Relevant log files

### Suggesting Features

1. Check if the feature has already been requested
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach

### Adding New Service Handlers

We welcome contributions for new AWS service handlers!

#### Steps:

1. **Fork the repository**

2. **Create a new branch**
   ```bash
   git checkout -b feature/add-kinesis-handler
   ```

3. **Create the handler file**
   
   Create `aws_nuker/handlers/kinesis_handler.py`:
   
   ```python
   """Kinesis resource handler."""
   
   from typing import List, Dict, Any
   from botocore.exceptions import ClientError
   
   from ..base_handler import ResourceHandler
   
   
   class KinesisHandler(ResourceHandler):
       """Handler for Kinesis streams."""
   
       @property
       def service_name(self) -> str:
           return "kinesis"
   
       def list_resources(self) -> List[Dict[str, Any]]:
           """List all Kinesis streams."""
           kinesis = self.session.client("kinesis")
           resources = []
   
           try:
               paginator = kinesis.get_paginator("list_streams")
               for page in paginator.paginate():
                   for stream_name in page.get("StreamNames", []):
                       resources.append({
                           "id": stream_name,
                           "name": stream_name,
                           "type": "stream",
                       })
           except ClientError as e:
               self.logger.error(f"Error listing Kinesis streams: {str(e)}")
   
           return resources
   
       def delete_resource(self, resource: Dict[str, Any]) -> bool:
           """Delete a Kinesis stream."""
           kinesis = self.session.client("kinesis")
           stream_name = resource.get("name")
   
           try:
               kinesis.delete_stream(
                   StreamName=stream_name,
                   EnforceConsumerDeletion=True,  # Force delete consumers
               )
               return True
           except ClientError as e:
               self.logger.error(
                   f"Error deleting Kinesis stream {stream_name}: {str(e)}"
               )
               return False
   ```

4. **Register the handler**
   
   Edit `aws_nuker/handlers/__init__.py`:
   ```python
   from .kinesis_handler import KinesisHandler
   
   __all__ = [
       # ... existing handlers ...
       "KinesisHandler",
   ]
   ```
   
   Edit `aws_nuker/registry.py`:
   ```python
   from .handlers import (
       # ... existing imports ...
       KinesisHandler,
   )
   
   HANDLER_REGISTRY = {
       # ... existing mappings ...
       "kinesis": KinesisHandler,
   }
   ```

5. **Update configuration**
   
   Add service to `aws_nuker/config.py` in `ALL_AWS_SERVICES` list:
   ```python
   ALL_AWS_SERVICES = [
       # ... existing services ...
       "kinesis",          # Kinesis
       # ... more services ...
   ]
   ```

6. **Test your handler**
   ```bash
   # Syntax check
   python3 -m py_compile aws_nuker/handlers/kinesis_handler.py
   
   # Test CLI
   python3 -m aws_nuker.cli list-services  # Should show kinesis
   
   # Dry run test (requires AWS credentials)
   python3 -m aws_nuker.cli nuke --regions us-east-1 --services kinesis --dry-run
   ```

7. **Update documentation**
   
   Add the service to README.md under "Supported AWS Services"

8. **Commit and push**
   ```bash
   git add .
   git commit -m "Add Kinesis service handler"
   git push origin feature/add-kinesis-handler
   ```

9. **Create Pull Request**

### Coding Standards

#### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all classes and methods
- Use type hints where possible

#### Handler Implementation Guidelines

1. **Always inherit from ResourceHandler**
   ```python
   class MyServiceHandler(ResourceHandler):
       pass
   ```

2. **Implement required methods**
   - `service_name` property
   - `list_resources()` method
   - `delete_resource()` method

3. **Optional method**
   - `is_default_resource()` - Override to identify default resources

4. **Error Handling**
   - Use try-except blocks for AWS API calls
   - Log errors appropriately
   - Return False from `delete_resource()` on failure
   - Don't raise exceptions (let base class handle retries)

5. **Logging**
   - Use `self.logger` for logging
   - Log important operations at INFO level
   - Log detailed operations at DEBUG level
   - Log failures at ERROR level

6. **Resource Dictionary Format**
   ```python
   {
       "id": "resource-identifier",      # Required: unique identifier
       "name": "resource-name",          # Required: human-readable name
       "type": "resource-type",          # Required: type of resource
       # ... optional additional fields
   }
   ```

#### Testing

Before submitting:

1. Test syntax: `python3 -m py_compile your_file.py`
2. Test imports: `python3 -c "from aws_nuker.handlers import YourHandler"`
3. Test CLI: `python3 -m aws_nuker.cli list-services`
4. Test dry-run: `python3 -m aws_nuker.cli nuke --services your-service --dry-run`
5. Test actual deletion in a safe test account

### Pull Request Guidelines

1. **One feature per PR** - Keep PRs focused
2. **Clear description** - Explain what and why
3. **Update documentation** - Keep README.md current
4. **Test thoroughly** - Include test results
5. **Follow conventions** - Match existing code style

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature (new service handler)
- [ ] Enhancement (improvement to existing feature)
- [ ] Documentation update

## Service Handler Details (if applicable)
- **Service Name**: 
- **Resources Handled**: 
- **Special Considerations**: 

## Testing
- [ ] Syntax validation passed
- [ ] Import test passed
- [ ] CLI list-services shows new service
- [ ] Dry-run test completed
- [ ] Actual deletion tested (in safe environment)

## Checklist
- [ ] Code follows PEP 8 style guidelines
- [ ] Docstrings added to all methods
- [ ] Handler registered in registry.py
- [ ] Service added to config.py
- [ ] Documentation updated
- [ ] No breaking changes
```

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip
- Git
- AWS account (for testing)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/varadharajaan/aws-nuker.git
   cd aws-nuker
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install in development mode**
   ```bash
   pip install -e .
   ```

5. **Configure AWS credentials**
   ```bash
   aws configure
   # Or set environment variables
   ```

6. **Test installation**
   ```bash
   aws-nuker --help
   aws-nuker list-services
   ```

## Questions?

- Open an issue for questions
- Join discussions in GitHub Discussions
- Review existing issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation
