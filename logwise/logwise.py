import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
import aiohttp
import traceback
import linecache

class LogWise:
    """
    Bibliothèque intelligente de gestion des logs avec analyse LLM via Gemini (API REST)
    """
    
    def __init__(
        self,
        llm_provider: str = "gemini",
        api_key: Optional[str] = None,
        log_level: int = logging.INFO,
        framework_context: str = "generic"
    ):
        self.logger = logging.getLogger("LogWise")
        self.logger.setLevel(log_level)
        
        self.handler = logging.StreamHandler(sys.stdout)
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - '
            '%(custom_pathname)s:%(custom_lineno)d',
            defaults={"custom_pathname": "unknown", "custom_lineno": 0}
        )
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        
        self.llm_provider = llm_provider
        self.api_key = api_key or "votre_clé_api_gemini"  # Remplacez par votre clé
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-1.5-flash"
        self.framework_context = framework_context
        
        self.recommendation_cache: Dict[str, str] = {}

    async def capture_log(self, message: str, level: str, extra: Dict[str, Any] = None):
        """
        Capture un log et déclenche l'analyse si nécessaire, incluant le code source (asynchrone)
        """
        extra = extra or {}
        log_entry = {
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "file": extra.get("pathname", "unknown"),
            "line": extra.get("lineno", 0),
            "framework": self.framework_context
        }
        
        filename = log_entry["file"]
        lineno = log_entry["line"]
        if filename != "unknown" and lineno > 0:
            code_lines = []
            for i in range(max(1, lineno - 1), lineno + 2):
                line = linecache.getline(filename, i).strip()
                if line:
                    code_lines.append(f"Ligne {i}: {line}")
            log_entry["code_context"] = "\n".join(code_lines) if code_lines else "Code non disponible"
        else:
            log_entry["code_context"] = "Code non disponible"
        
        log_extra = {
            "custom_pathname": log_entry["file"],
            "custom_lineno": log_entry["line"]
        }
        
        self.logger.log(
            getattr(logging, level),
            message,
            extra=log_extra
        )
        
        if level in ["ERROR", "EXCEPTION", "CRITICAL"]:
            await self.analyze_error(log_entry)

    async def analyze_error(self, log_entry: Dict[str, Any]) -> str:
        """
        Analyse une erreur avec le LLM Gemini et retourne une recommandation
        """
        error_key = f"{log_entry['file']}:{log_entry['line']}:{log_entry['message']}"
        
        if error_key in self.recommendation_cache:
            recommendation = self.recommendation_cache[error_key]
            self.logger.info(
                f"Recommandation depuis le cache: {recommendation}",
                extra={"custom_pathname": log_entry["file"], "custom_lineno": log_entry["line"]}
            )
            return recommendation

        prompt = f"""
        Analyse cette erreur dans un contexte {self.framework_context}:
        
        Fichier: {log_entry['file']}
        Ligne: {log_entry['line']}
        Message: {log_entry['message']}
        Timestamp: {log_entry['timestamp']}
        Contexte du code:

        {log_entry['code_context']}

        1. Une explication probable de l'erreur
        2. Une solution concrète avec exemple de code si possible
        3. Une prévention pour éviter que cela se reproduise
        """

        self.logger.debug(
            "Envoi du prompt à Gemini",
            extra={"custom_pathname": log_entry["file"], "custom_lineno": log_entry["line"]}
        )

        recommendation = await self._call_llm(prompt)
        self.recommendation_cache[error_key] = recommendation

        self.logger.info(
            f"Recommandation LLM: {recommendation}",
            extra={"custom_pathname": log_entry["file"], "custom_lineno": log_entry["line"]}
        )

        return recommendation

    async def _call_llm(self, prompt: str) -> str:
        """
        Appel asynchrone à l'API REST Gemini
        """
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status != 200:
                        error_msg = f"Erreur Gemini: {response.status} - {await response.text()}"
                        self.logger.error(
                            error_msg,
                            extra={"custom_pathname": "unknown", "custom_lineno": 0}
                        )
                        return error_msg

                    result = await response.json()
                    text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Pas de réponse")
                    
                    self.logger.debug(
                        f"Réponse brute de Gemini: {text}",
                        extra={"custom_pathname": "unknown", "custom_lineno": 0}
                    )

                    return text
            except Exception as e:
                error_msg = f"Erreur lors de l'appel à Gemini: {str(e)}"
                self.logger.error(
                    error_msg,
                    extra={"custom_pathname": "unknown", "custom_lineno": 0}
                )
                return error_msg

    def integrate_with_framework(self, app: Any):
        """
        Intégration avec différents frameworks
        """
        if self.framework_context.lower() == "flask":
            app.logger.handlers = []
            app.logger.addHandler(self.handler)
        elif self.framework_context.lower() == "django":
            logging.getLogger().handlers = []
            logging.getLogger().addHandler(self.handler)
        elif self.framework_context.lower() == "airflow":
            from airflow.utils.log.logging_mixin import LoggingMixin
            LoggingMixin().log.handlers = [self.handler]
