# LogWise
Une bibliothèque intelligente pour gérer les logs avec analyse via LLM.

## Installation
pip install logwise

## Utilisation
```python
from logwise import LogWise
logwise = LogWise(api_key="votre_clé")
await logwise.capture_log("Erreur", "ERROR")