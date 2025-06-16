"""
Tests de performance y carga para Sumy v2
"""
import asyncio
import aiohttp
import time
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
import os
from dataclasses import dataclass
from typing import List, Dict, Any
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs de servicios
SUMILLER_URL = os.getenv('SUMILLER_URL', 'https://sumiller-service-maitre-550926469911.europe-west1.run.app')
RAG_URL = os.getenv('RAG_URL', 'https://agentic-rag-service-maitre-550926469911.europe-west1.run.app')

@dataclass
class TestResult:
    """Resultado de un test de performance"""
    endpoint: str
    response_time: float
    status_code: int
    success: bool
    error_message: str = None

class PerformanceTestSuite:
    """Suite de tests de performance para Sumy v2"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        
    async def test_rag_service_load(self, concurrent_users=10, requests_per_user=5):
        """Test de carga para el RAG service"""
        logger.info(f"Iniciando test de carga RAG: {concurrent_users} usuarios, {requests_per_user} requests c/u")
        
        queries = [
            "vino tinto rioja",
            "principios del maridaje",
            "vino blanco albariño",
            "taninos en el vino",
            "cata de vinos",
            "vino para carne",
            "fermentación del vino",
            "vinos de españa",
            "maridaje con pescado",
            "denominaciones de origen"
        ]
        
        async def make_rag_request(session, query):
            """Hacer una request al RAG service"""
            start_time = time.time()
            try:
                payload = {
                    "query": query,
                    "max_results": 3
                }
                
                async with session.post(f"{RAG_URL}/search", json=payload) as response:
                    await response.json()
                    response_time = time.time() - start_time
                    
                    result = TestResult(
                        endpoint="RAG /search",
                        response_time=response_time,
                        status_code=response.status,
                        success=response.status == 200
                    )
                    self.results.append(result)
                    return result
                    
            except Exception as e:
                response_time = time.time() - start_time
                result = TestResult(
                    endpoint="RAG /search",
                    response_time=response_time,
                    status_code=0,
                    success=False,
                    error_message=str(e)
                )
                self.results.append(result)
                return result
        
        async def user_session():
            """Simular sesión de usuario"""
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(requests_per_user):
                    query = queries[i % len(queries)]
                    tasks.append(make_rag_request(session, query))
                
                return await asyncio.gather(*tasks)
        
        # Ejecutar usuarios concurrentes
        user_tasks = [user_session() for _ in range(concurrent_users)]
        start_time = time.time()
        
        await asyncio.gather(*user_tasks)
        
        total_time = time.time() - start_time
        logger.info(f"Test RAG completado en {total_time:.2f} segundos")
        
        return self._analyze_results("RAG")
    
    async def test_sumiller_service_load(self, concurrent_users=5, requests_per_user=3):
        """Test de carga para el Sumiller service"""
        logger.info(f"Iniciando test de carga Sumiller: {concurrent_users} usuarios, {requests_per_user} requests c/u")
        
        queries = [
            "Recomiéndame un vino tinto español",
            "¿Qué son los taninos?",
            "¿Qué vino va bien con salmón?",
            "Explícame el proceso de fermentación",
            "Busco un vino de la Rioja",
            "¿Cómo se cata un vino?",
            "Vino para maridar con queso",
            "¿Qué es la denominación de origen?",
            "Diferencia entre crianza y reserva",
            "Vino blanco para aperitivo"
        ]
        
        async def make_sumiller_request(session, query, user_id):
            """Hacer una request al Sumiller service"""
            start_time = time.time()
            try:
                payload = {
                    "query": query,
                    "user_id": f"load_test_user_{user_id}",
                    "conversation_history": []
                }
                
                timeout = aiohttp.ClientTimeout(total=60)
                async with session.post(f"{SUMILLER_URL}/query", json=payload, timeout=timeout) as response:
                    await response.json()
                    response_time = time.time() - start_time
                    
                    result = TestResult(
                        endpoint="Sumiller /query",
                        response_time=response_time,
                        status_code=response.status,
                        success=response.status == 200
                    )
                    self.results.append(result)
                    return result
                    
            except Exception as e:
                response_time = time.time() - start_time
                result = TestResult(
                    endpoint="Sumiller /query",
                    response_time=response_time,
                    status_code=0,
                    success=False,
                    error_message=str(e)
                )
                self.results.append(result)
                return result
        
        async def user_session(user_id):
            """Simular sesión de usuario"""
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(requests_per_user):
                    query = queries[i % len(queries)]
                    tasks.append(make_sumiller_request(session, query, user_id))
                
                return await asyncio.gather(*tasks)
        
        # Ejecutar usuarios concurrentes
        user_tasks = [user_session(i) for i in range(concurrent_users)]
        start_time = time.time()
        
        await asyncio.gather(*user_tasks)
        
        total_time = time.time() - start_time
        logger.info(f"Test Sumiller completado en {total_time:.2f} segundos")
        
        return self._analyze_results("Sumiller")
    
    def test_health_endpoints_stress(self, duration_seconds=60):
        """Test de stress para health endpoints"""
        logger.info(f"Iniciando stress test de {duration_seconds} segundos")
        
        import requests
        
        def make_health_request(url):
            try:
                start_time = time.time()
                response = requests.get(f"{url}/health", timeout=5)
                response_time = time.time() - start_time
                
                result = TestResult(
                    endpoint=f"{url} /health",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=response.status_code == 200
                )
                self.results.append(result)
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                result = TestResult(
                    endpoint=f"{url} /health",
                    response_time=response_time,
                    status_code=0,
                    success=False,
                    error_message=str(e)
                )
                self.results.append(result)
                return result
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            
            while time.time() - start_time < duration_seconds:
                # Alternar entre servicios
                url = SUMILLER_URL if len(futures) % 2 == 0 else RAG_URL
                future = executor.submit(make_health_request, url)
                futures.append(future)
                
                time.sleep(0.1)  # 10 requests per second
            
            # Esperar a que terminen todos
            for future in futures:
                future.result()
        
        logger.info("Stress test completado")
        return self._analyze_results("Health")
    
    def test_memory_usage_simulation(self):
        """Simulación de uso de memoria con conversaciones largas"""
        logger.info("Iniciando test de memoria con conversaciones largas")
        
        import requests
        
        # Simular conversación larga
        conversation_history = []
        user_id = "memory_test_user"
        
        queries = [
            "¿Qué vino me recomiendas?",
            "¿Con qué comida lo puedo maridar?",
            "¿Qué temperatura de servicio tiene?",
            "¿Cuánto tiempo puede guardarse?",
            "¿Qué otros vinos similares tienes?",
            "¿De qué región es este vino?",
            "¿Qué uvas se utilizan?",
            "¿Cómo es el proceso de elaboración?",
            "¿Qué maridajes adicionales me sugieres?",
            "¿Hay alguna curiosidad sobre este vino?"
        ]
        
        for i, query in enumerate(queries):
            start_time = time.time()
            
            try:
                payload = {
                    "query": query,
                    "user_id": user_id,
                    "conversation_history": conversation_history[-10:]  # Últimos 10 mensajes
                }
                
                response = requests.post(f"{SUMILLER_URL}/query", json=payload, timeout=60)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    # Añadir a historial de conversación
                    conversation_history.extend([
                        {"role": "user", "content": query},
                        {"role": "assistant", "content": data["response"]}
                    ])
                
                result = TestResult(
                    endpoint="Sumiller /query (memory)",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=response.status_code == 200
                )
                self.results.append(result)
                
            except Exception as e:
                response_time = time.time() - start_time
                result = TestResult(
                    endpoint="Sumiller /query (memory)",
                    response_time=response_time,
                    status_code=0,
                    success=False,
                    error_message=str(e)
                )
                self.results.append(result)
            
            # Pausa entre mensajes
            time.sleep(1)
        
        return self._analyze_results("Memory")
    
    def _analyze_results(self, test_type: str) -> Dict[str, Any]:
        """Analizar resultados de un tipo de test"""
        test_results = [r for r in self.results if test_type.lower() in r.endpoint.lower()]
        
        if not test_results:
            return {"error": "No results found"}
        
        response_times = [r.response_time for r in test_results if r.success]
        success_count = sum(1 for r in test_results if r.success)
        total_count = len(test_results)
        
        analysis = {
            "test_type": test_type,
            "total_requests": total_count,
            "successful_requests": success_count,
            "failed_requests": total_count - success_count,
            "success_rate": (success_count / total_count) * 100 if total_count > 0 else 0,
        }
        
        if response_times:
            analysis.update({
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "median_response_time": statistics.median(response_times),
                "p95_response_time": self._percentile(response_times, 95),
                "p99_response_time": self._percentile(response_times, 99),
            })
        
        # Análisis de errores
        errors = [r for r in test_results if not r.success]
        if errors:
            error_analysis = {}
            for error in errors:
                key = error.error_message or f"HTTP {error.status_code}"
                error_analysis[key] = error_analysis.get(key, 0) + 1
            analysis["errors"] = error_analysis
        
        return analysis
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calcular percentil"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * len(sorted_data)
        if index.is_integer():
            return sorted_data[int(index) - 1]
        else:
            return sorted_data[int(index)]
    
    def generate_report(self) -> Dict[str, Any]:
        """Generar reporte completo de performance"""
        report = {
            "summary": {
                "total_tests": len(self.results),
                "overall_success_rate": (sum(1 for r in self.results if r.success) / len(self.results)) * 100 if self.results else 0,
                "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "detailed_analysis": {}
        }
        
        # Análisis por tipo de test
        test_types = set()
        for result in self.results:
            if "rag" in result.endpoint.lower():
                test_types.add("RAG")
            elif "sumiller" in result.endpoint.lower():
                test_types.add("Sumiller")
            elif "health" in result.endpoint.lower():
                test_types.add("Health")
        
        for test_type in test_types:
            report["detailed_analysis"][test_type] = self._analyze_results(test_type)
        
        return report

async def run_performance_tests():
    """Ejecutar todos los tests de performance"""
    suite = PerformanceTestSuite()
    
    logger.info("🚀 Iniciando suite de tests de performance")
    
    # Test 1: RAG Service Load
    logger.info("📊 Test 1: Carga RAG Service")
    await suite.test_rag_service_load(concurrent_users=10, requests_per_user=5)
    
    # Test 2: Sumiller Service Load
    logger.info("📊 Test 2: Carga Sumiller Service")
    await suite.test_sumiller_service_load(concurrent_users=5, requests_per_user=3)
    
    # Test 3: Health Endpoints Stress
    logger.info("📊 Test 3: Stress Health Endpoints")
    suite.test_health_endpoints_stress(duration_seconds=30)
    
    # Test 4: Memory Usage
    logger.info("📊 Test 4: Uso de memoria")
    suite.test_memory_usage_simulation()
    
    # Generar reporte
    report = suite.generate_report()
    
    # Mostrar resultados
    print("\n" + "="*60)
    print("📈 REPORTE DE PERFORMANCE - SUMY V2")
    print("="*60)
    
    print(f"\n📊 RESUMEN GENERAL:")
    print(f"   Total de tests: {report['summary']['total_tests']}")
    print(f"   Tasa de éxito: {report['summary']['overall_success_rate']:.1f}%")
    print(f"   Timestamp: {report['summary']['test_timestamp']}")
    
    for test_type, analysis in report['detailed_analysis'].items():
        print(f"\n🔍 ANÁLISIS {test_type.upper()}:")
        print(f"   Requests totales: {analysis['total_requests']}")
        print(f"   Requests exitosos: {analysis['successful_requests']}")
        print(f"   Tasa de éxito: {analysis['success_rate']:.1f}%")
        
        if 'avg_response_time' in analysis:
            print(f"   Tiempo promedio: {analysis['avg_response_time']:.2f}s")
            print(f"   Tiempo mínimo: {analysis['min_response_time']:.2f}s")
            print(f"   Tiempo máximo: {analysis['max_response_time']:.2f}s")
            print(f"   P95: {analysis['p95_response_time']:.2f}s")
            print(f"   P99: {analysis['p99_response_time']:.2f}s")
        
        if 'errors' in analysis:
            print(f"   Errores: {analysis['errors']}")
    
    # Guardar reporte en archivo
    with open('performance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Reporte guardado en: performance_report.json")
    
    # Validaciones de SLA
    print(f"\n✅ VALIDACIONES SLA:")
    
    # SLA: RAG service < 3 segundos P95
    rag_analysis = report['detailed_analysis'].get('RAG', {})
    if 'p95_response_time' in rag_analysis:
        rag_p95 = rag_analysis['p95_response_time']
        rag_sla = rag_p95 < 3.0
        print(f"   RAG P95 < 3s: {'✅' if rag_sla else '❌'} ({rag_p95:.2f}s)")
    
    # SLA: Sumiller service < 15 segundos P95
    sumiller_analysis = report['detailed_analysis'].get('Sumiller', {})
    if 'p95_response_time' in sumiller_analysis:
        sumiller_p95 = sumiller_analysis['p95_response_time']
        sumiller_sla = sumiller_p95 < 15.0
        print(f"   Sumiller P95 < 15s: {'✅' if sumiller_sla else '❌'} ({sumiller_p95:.2f}s)")
    
    # SLA: Success rate > 95%
    overall_success = report['summary']['overall_success_rate']
    success_sla = overall_success > 95.0
    print(f"   Success rate > 95%: {'✅' if success_sla else '❌'} ({overall_success:.1f}%)")
    
    print("\n🏁 Tests de performance completados!")
    
    return report

if __name__ == "__main__":
    # Ejecutar tests
    report = asyncio.run(run_performance_tests()) 