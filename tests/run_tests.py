#!/usr/bin/env python3
"""
Script para ejecutar todos los tests de las funciones Lambda
Siguiendo principio de simplicidad-first
"""

import unittest
import sys
import os

def run_all_tests():
    """Ejecutar todos los tests"""
    print("=" * 60)
    print("EJECUTANDO TESTS DE FUNCIONES LAMBDA NOVI PQR")
    print("=" * 60)
    
    # Descubrir y ejecutar todos los tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    
    if result.errors:
        print("\nERRORES:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
    
    if result.failures:
        print("\nFALLOS:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    # Resultado final
    if result.wasSuccessful():
        print("\n✅ TODOS LOS TESTS PASARON")
        return 0
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        return 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
