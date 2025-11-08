# Contributing to AWS Nuker

Thank you for your interest in contributing to AWS Nuker! This guide will help you get started.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (Python version, AWS region, etc.)

### Suggesting Enhancements

We welcome suggestions for new features! Please open an issue with:
- A clear description of the enhancement
- Why this enhancement would be useful
- Any implementation ideas you have

### Adding New AWS Services

To add support for a new AWS service:

1. Create a new service class in the appropriate file under `aws_nuker/services/`
2. Inherit from `BaseService`
3. Implement the required methods:
   - `get_service_name()` - Return the service name
   - `list_resources()` - List all resources for the service
   - `delete_resource()` - Delete a single resource

4. Add the service to `ALL_SERVICES` dict in `aws_nuker/cli.py`
5. Update the README to include the new service
6. Test your implementation

Example:

```python
from .base import BaseService
import boto3

class MyNewService(BaseService):
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('myservice', region_name=region)
    
    def get_service_name(self) -> str:
        return "My New Service"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        resources = []
        try:
            # List resources using boto3
            response = self.client.list_resources()
            for resource in response.get('Resources', []):
                resources.append({
                    'id': resource['Id'],
                    'name': resource.get('Name', 'N/A')
                })
        except Exception as e:
            self.log_error("Error listing resources", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        try:
            self.client.delete_resource(ResourceId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting resource {resource['id']}", e)
            return False
```

### Pull Request Process

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide for Python code
- Add docstrings to all classes and methods
- Include type hints where appropriate
- Keep functions focused and single-purpose
- Add error handling with appropriate logging

### Testing Guidelines

- Test with `--dry-run` first
- Test in a development/sandbox AWS account only
- Verify that default resources are not deleted
- Test error handling (e.g., permissions issues, missing resources)
- Test with multiple regions

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions professional

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/aws-nuker.git
cd aws-nuker

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Make your changes
# ...

# Test your changes
aws-nuker --list-services
```

## Questions?

If you have questions about contributing, feel free to open an issue or reach out to the maintainers.

Thank you for contributing to AWS Nuker!
