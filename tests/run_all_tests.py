#!/usr/bin/env python3
"""
Script principal para ejecutar todos los tests de Sumy v2
"""
import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
import argparse

def print_banner():
    """Mostrar banner de inicio"""
    print("="*70)
    print("🧪 SUITE COMPLETA DE TESTS - SUMY V2")
    print("="*70)
    print("🍷 Sumiller Virtual con IA")
    print("📅 Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)

def run_command(command, description, cwd=None):
    """Ejecutar comando y capturar resultado"""
    print(f"\n🔄 {description}")
    print(f"   Comando: {command}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=300  # 5 minutos timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"   ✅ Completado en {duration:.1f}s")
            return True, result.stdout, result.stderr, duration
        else:
            print(f"   ❌ Falló en {duration:.1f}s")
            print(f"   Error: {result.stderr}")
            return False, result.stdout, result.stderr, duration
            
    except subprocess.TimeoutExpired:
        print(f"   ⏱️  Timeout después de 5 minutos")
        return False, "", "Timeout", 300
    except Exception as e:
        print(f"   💥 Excepción: {str(e)}")
        return False, "", str(e), 0

def check_dependencies():
    """Verificar dependencias necesarias"""
    print("\n🔍 Verificando dependencias...")
    
    dependencies = {
        "python": "python --version",
        "pytest": "pytest --version",
        "node": "node --version",
        "npm": "npm --version"
    }
    
    missing = []
    
    for dep, cmd in dependencies.items():
        success, stdout, stderr, _ = run_command(cmd, f"Verificando {dep}")
        if not success:
            missing.append(dep)
    
    if missing:
        print(f"\n❌ Dependencias faltantes: {', '.join(missing)}")
        print("   Por favor instala las dependencias necesarias.")
        return False
    
    print("✅ Todas las dependencias están disponibles")
    return True

def install_test_dependencies():
    """Instalar dependencias de testing"""
    print("\n📦 Instalando dependencias de testing...")
    
    # Python dependencies
    success, _, _, _ = run_command(
        "pip install -r tests/requirements.txt",
        "Instalando dependencias Python"
    )
    
    if not success:
        print("❌ Falló la instalación de dependencias Python")
        return False
    
    # E2E dependencies
    if Path("tests/e2e/package.json").exists():
        success, _, _, _ = run_command(
            "npm install",
            "Instalando dependencias E2E",
            cwd="tests/e2e"
        )
        
        if success:
            run_command(
                "npx playwright install",
                "Instalando navegadores Playwright",
                cwd="tests/e2e"
            )
    
    return True

def run_unit_tests():
    """Ejecutar tests unitarios"""
    print("\n🧪 TESTS UNITARIOS")
    print("-" * 50)
    
    results = {}
    
    # Tests del sumiller service
    success, stdout, stderr, duration = run_command(
        "python -m pytest tests/unit/test_sumiller_service.py -v --tb=short",
        "Tests unitarios Sumiller Service"
    )
    results["sumiller_unit"] = {
        "success": success,
        "duration": duration,
        "output": stdout
    }
    
    # Tests del RAG service
    success, stdout, stderr, duration = run_command(
        "python -m pytest tests/unit/test_rag_service.py -v --tb=short",
        "Tests unitarios RAG Service"
    )
    results["rag_unit"] = {
        "success": success,
        "duration": duration,
        "output": stdout
    }
    
    # Tests del frontend (si están disponibles)
    if Path("tests/unit/test_frontend.js").exists():
        success, stdout, stderr, duration = run_command(
            "npm test",
            "Tests unitarios Frontend",
            cwd="ui"
        )
        results["frontend_unit"] = {
            "success": success,
            "duration": duration,
            "output": stdout
        }
    
    return results

def run_integration_tests():
    """Ejecutar tests de integración"""
    print("\n🔗 TESTS DE INTEGRACIÓN")
    print("-" * 50)
    
    success, stdout, stderr, duration = run_command(
        "python -m pytest tests/integration/test_full_flow.py -v --tb=short",
        "Tests de integración completos"
    )
    
    return {
        "integration": {
            "success": success,
            "duration": duration,
            "output": stdout
        }
    }

def run_e2e_tests():
    """Ejecutar tests E2E"""
    print("\n🌐 TESTS END-TO-END")
    print("-" * 50)
    
    if not Path("tests/e2e/package.json").exists():
        print("   ⚠️  Tests E2E no configurados")
        return {"e2e": {"success": False, "duration": 0, "output": "Not configured"}}
    
    success, stdout, stderr, duration = run_command(
        "npx playwright test",
        "Tests End-to-End con Playwright",
        cwd="tests/e2e"
    )
    
    return {
        "e2e": {
            "success": success,
            "duration": duration,
            "output": stdout
        }
    }

def run_performance_tests():
    """Ejecutar tests de performance"""
    print("\n⚡ TESTS DE PERFORMANCE")
    print("-" * 50)
    
    success, stdout, stderr, duration = run_command(
        "python tests/performance/load_test.py",
        "Tests de carga y performance"
    )
    
    return {
        "performance": {
            "success": success,
            "duration": duration,
            "output": stdout
        }
    }

def generate_coverage_report():
    """Generar reporte de cobertura"""
    print("\n📊 GENERANDO REPORTE DE COBERTURA")
    print("-" * 50)
    
    # Cobertura Python
    success, stdout, stderr, duration = run_command(
        "python -m pytest tests/unit/ --cov=sumiller-service --cov=agentic_rag-service --cov-report=html --cov-report=json",
        "Generando reporte de cobertura Python"
    )
    
    if success:
        print("   📁 Reporte HTML: htmlcov/index.html")
        print("   📄 Reporte JSON: coverage.json")
    
    return success

def generate_final_report(all_results):
    """Generar reporte final consolidado"""
    print("\n📋 GENERANDO REPORTE FINAL")
    print("-" * 50)
    
    total_tests = 0
    passed_tests = 0
    total_duration = 0
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {},
        "details": all_results,
        "recommendations": []
    }
    
    # Calcular estadísticas
    for category, tests in all_results.items():
        for test_name, result in tests.items():
            total_tests += 1
            total_duration += result["duration"]
            if result["success"]:
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    report["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": success_rate,
        "total_duration": total_duration
    }
    
    # Generar recomendaciones
    if success_rate < 90:
        report["recommendations"].append("❌ Tasa de éxito baja - Revisar tests fallidos")
    
    if total_duration > 600:  # 10 minutos
        report["recommendations"].append("⏱️  Tests muy lentos - Optimizar performance")
    
    if success_rate >= 95:
        report["recommendations"].append("✅ Excelente calidad - Todos los sistemas funcionando")
    
    # Guardar reporte
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Mostrar resumen
    print(f"\n📈 RESUMEN EJECUTIVO")
    print(f"   Tests ejecutados: {total_tests}")
    print(f"   Tests exitosos: {passed_tests}")
    print(f"   Tests fallidos: {total_tests - passed_tests}")
    print(f"   Tasa de éxito: {success_rate:.1f}%")
    print(f"   Duración total: {total_duration:.1f}s")
    
    if report["recommendations"]:
        print(f"\n💡 RECOMENDACIONES:")
        for rec in report["recommendations"]:
            print(f"   {rec}")
    
    print(f"\n💾 Reporte guardado en: test_report.json")
    
    return success_rate >= 90

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Ejecutar tests de Sumy v2")
    parser.add_argument("--skip-deps", action="store_true", help="Omitir instalación de dependencias")
    parser.add_argument("--unit-only", action="store_true", help="Solo tests unitarios")
    parser.add_argument("--integration-only", action="store_true", help="Solo tests de integración")
    parser.add_argument("--e2e-only", action="store_true", help="Solo tests E2E")
    parser.add_argument("--performance-only", action="store_true", help="Solo tests de performance")
    parser.add_argument("--no-coverage", action="store_true", help="Omitir reporte de cobertura")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Instalar dependencias
    if not args.skip_deps:
        if not install_test_dependencies():
            sys.exit(1)
    
    all_results = {}
    start_time = time.time()
    
    # Ejecutar tests según argumentos
    if args.unit_only:
        all_results.update(run_unit_tests())
    elif args.integration_only:
        all_results.update(run_integration_tests())
    elif args.e2e_only:
        all_results.update(run_e2e_tests())
    elif args.performance_only:
        all_results.update(run_performance_tests())
    else:
        # Ejecutar todos los tests
        all_results.update(run_unit_tests())
        all_results.update(run_integration_tests())
        all_results.update(run_e2e_tests())
        all_results.update(run_performance_tests())
    
    # Generar cobertura
    if not args.no_coverage and not args.performance_only:
        generate_coverage_report()
    
    # Generar reporte final
    success = generate_final_report(all_results)
    
    total_time = time.time() - start_time
    
    print(f"\n🏁 TESTS COMPLETADOS")
    print(f"   Tiempo total: {total_time:.1f}s")
    print(f"   Estado: {'✅ ÉXITO' if success else '❌ FALLOS DETECTADOS'}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 