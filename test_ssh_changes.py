#!/usr/bin/env python3
"""
Prueba básica para verificar los cambios realizados en la seguridad SSH
"""

import os
import sys

# Añadir el directorio de skills al path y usar el entorno virtual
skills_path = os.path.join(os.path.dirname(__file__), ".agents", "skills", "hostinger-tesis-manager", "scripts")
venv_path = os.path.join(skills_path, ".venv")

# Añadir el entorno virtual al path si existe
if os.path.exists(venv_path):
    # Añadir las rutas del entorno virtual
    site_packages = os.path.join(venv_path, "lib", "site-packages")
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)
    
    # En Windows, las paquetes están en Lib\site-packages
    site_packages_win = os.path.join(venv_path, "Lib", "site-packages")
    if os.path.exists(site_packages_win):
        sys.path.insert(0, site_packages_win)

sys.path.append(skills_path)

def test_imports():
    """Prueba que los módulos se importen correctamente"""
    try:
        from hostinger_mcp import ejecutar_comando_ssh
        print("[OK] Importación de hostinger_mcp exitosa")
        return True
    except Exception as e:
        print(f"[FAIL] Error al importar hostinger_mcp: {e}")
        return False

def test_env_loading():
    """Prueba que se carguen las variables de entorno correctamente"""
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(skills_path, ".env")
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path)
            print("[OK] Carga de variables de entorno exitosa")
            return True
        else:
            print("[WARN] Archivo .env no encontrado (se usará .env.example si existe)")
            example_path = os.path.join(skills_path, ".env.example")
            if os.path.exists(example_path):
                print("  Se encontró .env.example, copie a .env y configure las variables")
            return True  # No es un error crítico para la prueba
    except Exception as e:
        print(f"[FAIL] Error al cargar variables de entorno: {e}")
        return False

def test_security_changes():
    """Prueba que los cambios de seguridad estén presentes"""
    try:
        # Leer el archivo hostinger_mcp.py y verificar los cambios
        hostinger_mcp_path = os.path.join(skills_path, "hostinger_mcp.py")
        with open(hostinger_mcp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar que ya no use AutoAddPolicy
        if "AutoAddPolicy()" in content:
            print("[FAIL] Aún se usa AutoAddPolicy() - debe ser reemplazado")
            return False
        else:
            print("[OK] AutoAddPolicy() no se encuentra en el código")
        
        # Verificar que use RejectPolicy o similar
        if "RejectPolicy()" in content or "load_system_host_keys" in content:
            print("[OK] Se implementó política de rechazo o carga de hosts conocidos")
        else:
            print("[WARN] No se encontró evidencia clara de política de rechazo")
        
        # Verificar que se eliminó el fallback a contraseña
        if "HOSTINGER_PASSWORD" in content and "password=" in content:
            print("[FAIL] Aún se referencia HOSTINGER_PASSWORD o se usa password en connect")
            return False
        else:
            print("[OK] Se eliminó el fallback a autenticación por contraseña")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error al verificar cambios de seguridad: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("=== PRUEBA DE CAMBIOS DE SEGURIDAD SSH ===")
    print()
    
    tests = [
        ("Importación de módulos", test_imports),
        ("Carga de variables de entorno", test_env_loading),
        ("Verificación de cambios de seguridad", test_security_changes)
    ]
    
    resultados = []
    for nombre, prueba in tests:
        print(f"Ejecutando: {nombre}")
        resultado = prueba()
        resultados.append(resultado)
        print()
    
    # Resumen
    passed = sum(resultados)
    total = len(resultados)
    
    print(f"RESULTADO: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("[OK] Todas las pruebas pasaron - los cambios de seguridad están implementados correctamente")
        return 0
    else:
        print("[FAIL] Algunas pruebas fallaron - revisar los cambios necesarios")
        return 1

if __name__ == "__main__":
    sys.exit(main())