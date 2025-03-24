# LogWise-Rabii

**LogWise-Rabii** is a Python library for managing and analyzing logs in your applications, with easy integration into frameworks like Flask. It allows capturing, analyzing, and sending logs to an external API (such as the Gemini API for LLM analysis), while managing features like caching and network error handling.

## Main Features
- Log capture and analysis with custom metadata
- Flask integration for simplified web application log management
- Support for asynchronous calls to external API
- Network error handling with simulations (for testing)
- Log caching to prevent duplications

## Prerequisites
- Python 3.8 or higher
- Dependencies:
  - `aiohttp>=3.8.0` (for asynchronous API calls)
  - `flask>=2.0.0` (if used with Flask)

## Installation

To test a version from TestPyPI:

```bash
pip install -i https://test.pypi.org/simple/ logwise-rabii
```

## Configuration

To use LogWise-Rabii, you must provide an API key (e.g., for the Gemini API) and configure the logging level.

### Basic Configuration Example

```python
from logwise import LogWise
import logging

# LogWise initialization
logwise = LogWise(
    framework_context="flask",  # or None if no framework
    api_key="your-api-key",     # Replace with your API key
    log_level=logging.DEBUG     # Logging level (DEBUG, INFO, ERROR, etc.)
)
```

## Flask Integration

If you're using Flask, you can integrate LogWise directly into your application:

```python
from flask import Flask
from logwise import LogWise
import logging

app = Flask(__name__)

# LogWise initialization with Flask
logwise = LogWise(
    framework_context="flask",
    api_key="your-api-key",
    log_level=logging.DEBUG
)
logwise.integrate_with_framework(app)
```

## Usage

### 1. Capturing Errors in a Flask Application

You can capture and log errors in your Flask routes. Here's an example simulating different errors:

```python
import asyncio
from flask import Flask
from logwise import LogWise
import random
import logging

app = Flask(__name__)

logwise = LogWise(
    framework_context="flask",
    api_key="your-api-key",
    log_level=logging.DEBUG
)
logwise.integrate_with_framework(app)

@app.route('/test_errors')
def test_errors():
    scenario = random.randint(1, 3)
    
    if scenario == 1:
        try:
            result = 1 / 0
        except ZeroDivisionError as e:
            asyncio.run(logwise.capture_log(
                message=str(e),
                level="ERROR",
                extra={"pathname": __file__, "lineno": 28}
            ))
            return "Division error captured"
    
    # Similar error handling for IndexError and KeyError
    # ...

if __name__ == "__main__":
    app.run(debug=False, port=5000)
```

### 2. Log Caching

LogWise caches logs to prevent duplications:

```python
def test_cache():
    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        asyncio.run(logwise.capture_log(
            message=str(e),
            level="ERROR",
            extra={"pathname": __file__, "lineno": 64}
        ))
        asyncio.run(logwise.capture_log(
            message=str(e),
            level="ERROR",
            extra={"pathname": __file__, "lineno": 64}
        ))

test_cache()
```

### 3. Network Failure Simulation

Test network error handling by simulating connection failures:

```python
async def simulate_network_failure():
    await asyncio.sleep(2)
    if random.random() < 0.3:
        raise ConnectionError("Simulated network failure")

async def test_network_failure():
    # Network failure simulation code
    # ...

asyncio.run(test_network_failure())
```

## Testing

Install test dependencies:

```bash
pip install pytest pytest-asyncio
```

Run tests:

```bash
pytest tests/test_advanced.py
```

Tests include:
- Flask application error simulation
- Log caching verification
- Network error simulation

## Contributing

1. Fork the repository: https://github.com/rabiizahnoune/logwise
2. Create a branch for your modifications:
   ```bash
   git checkout -b my-new-feature
   ```
3. Make your modifications and add tests if necessary
4. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

If you encounter issues or have questions, open an issue on GitHub: https://github.com/rabiizahnoune/logwise/issues

## Author
- **Rabii Zahnoune**
  - Email: rabiizahnoune7@gmail.com
  - Version: 0.1.3
