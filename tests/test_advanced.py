# test_advanced.py (version synchrone)

import logging
from flask import Flask
from logwise import LogWise
import random
import asyncio

app = Flask(__name__)

logwise = LogWise(
    framework_context="flask",
    api_key="AIzaSyBqnMwcPJZqySSrdrcqnG828KmW_f7KkfE",  # Remplacez par votre vraie clé
    log_level=logging.DEBUG
)
logwise.integrate_with_framework(app)

async def simulate_network_failure():
    await asyncio.sleep(2)
    if random.random() < 0.3:
        raise ConnectionError("Simulated network failure")

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
            return "Erreur de division capturée"
    
    elif scenario == 2:
        my_list = [1, 2, 3]
        try:
            value = my_list[5]
        except IndexError as e:
            asyncio.run(logwise.capture_log(
                message=str(e),
                level="ERROR",
                extra={"pathname": __file__, "lineno": 40}
            ))
            return "Erreur d'index capturée"
    
    else:
        my_dict = {"a": 1, "b": 2}
        try:
            value = my_dict["c"]
        except KeyError as e:
            asyncio.run(logwise.capture_log(
                message=str(e),
                level="ERROR",
                extra={"pathname": __file__, "lineno": 52}
            ))
            return "Erreur de clé capturée"

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

async def test_network_failure():
    original_call_llm = logwise._call_llm
    
    async def mock_call_llm(prompt):
        await simulate_network_failure()
        return await original_call_llm(prompt)
    
    logwise._call_llm = mock_call_llm
    try:
        1 / 0
    except ZeroDivisionError as e:
        await logwise.capture_log(
            message=str(e),
            level="ERROR",
            extra={"pathname": __file__, "lineno": 84}
        )
    logwise._call_llm = original_call_llm

if __name__ == "__main__":
    print("Test 1 : Simulation d'erreurs via Flask")
    app.run(debug=False, port=5000)
    
    print("\nTest 2 : Vérification du cache")
    test_cache()
    
    print("\nTest 3 : Simulation d'erreur réseau")
    asyncio.run(test_network_failure())