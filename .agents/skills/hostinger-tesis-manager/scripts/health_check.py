#!/usr/bin/env python3
"""
Script de verificación de salud para el agente MCP de Hostinger VPS
Verifica la conectividad SSH básica y el estado de los servicios críticos
"""

import os
import sys
import json
from datetime import datetime

# Añadir el directorio actual al path para importar hostinger_mcp
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hostinger_mcp import verificar_estado_servidor, verificar_servicio

def verificar_conectividad_ssh():
    """Verifica la conectividad SSH básica ejecutando un comando simple"""
    try:
        resultado = verificar_estado_servidor()
        # Si obtenemos una respuesta (aunque sea un error de comandos), 
        # significa que la conectividad SSH funciona
        if isinstance(resultado, str) and len(resultado) > 0:
            return True, "Conectividad SSH establecida"
        else:
            return False, "Respuesta SSH inesperada o vacía"
    except Exception as e:
        return False, f"Error de conectividad SSH: {str(e)}"

def verificar_servicios_criticos():
    """Verifica el estado de los servicios críticos del sistema"""
    servicios_criticos = ["tesis-backend", "nginx", "postgresql"]
    resultados = {}
    
    for servicio in servicios_criticos:
        try:
            resultado = verificar_servicio(servicio)
            # Analizar si el servicio está activo basado en la salida
            activo = "active (running)" in resultado
            resultados[servicio] = {
                "activo": activo,
                "detalle": resultado[:200] + "..." if len(resultado) > 200 else resultado
            }
        except Exception as e:
            resultados[servicio] = {
                "activo": False,
                "error": str(e)
            }
    
    return resultados

def main():
    """Función principal de verificación de salud"""
    print("=== VERIFICACIÓN DE SALUD DEL AGENTE MCP ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Verificar conectividad SSH
    print("1. Verificando conectividad SSH...")
    ssh_ok, ssh_msg = verificar_conectividad_ssh()
    print(f"   Resultado: {'✓ OK' if ssh_ok else '✗ FALLÓ'}")
    print(f"   Detalle: {ssh_msg}")
    print()
    
    # Verificar servicios críticos
    print("2. Verificando servicios críticos...")
    servicios = verificar_servicios_criticos()
    todos_activos = True
    
    for servicio, info in servicios.items():
        estado = "✓ ACTIVO" if info.get("activo", False) else "✗ INACTIVO"
        print(f"   {servicio}: {estado}")
        if not info.get("activo", False):
            todos_activos = False
            if "detalle" in info:
                print(f"     Detalle: {info['detalle']}")
            elif "error" in info:
                print(f"     Error: {info['error']}")
    
    print()
    
    # Determinar estado general
    if ssh_ok and todos_activos:
        estado_general = "SALUDABLE"
        codigo_salida = 0
    elif ssh_ok:
        estado_general = "DEGRADADO (Servicios con problemas)"
        codigo_salida = 1
    else:
        estado_general = "CRÍTICO (Problemas de conectividad)"
        codigo_salida = 2
    
    print(f"ESTADO GENERAL: {estado_general}")
    
    # Salida estructurada para uso por sistemas de monitoreo
    resultado_json = {
        "timestamp": datetime.now().isoformat(),
        "ssh_connectivity": {
            "ok": ssh_ok,
            "message": ssh_msg
        },
        "servicios": servicios,
        "estado_general": estado_general,
        "saludable": ssh_ok and todos_activos
    }
    
    # Guardar resultado en archivo para posible consumo por otros sistemas
    try:
        with open("/tmp/agent_health_check.json", "w") as f:
            json.dump(resultado_json, f, indent=2)
    except Exception:
        pass  # No fallar si no podemos escribir el archivo
    
    return codigo_salida

if __name__ == "__main__":
    sys.exit(main())