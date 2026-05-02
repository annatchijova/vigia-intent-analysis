from mcp.server.fastmcp import FastMCP
import os
import subprocess
import psutil  # El ojo sobre la RAM

mcp = FastMCP("Vigia_Sift_Bridge")

@mcp.tool()
def listar_archivos(directorio: str = "."):
    """Exploración de índices en el sistema de archivos."""
    return os.listdir(directorio)

@mcp.tool()
def leer_evidencia(ruta: str):
    """Análisis de contenido e iconografía de datos."""
    with open(ruta, 'r') as f:
        return f.read()

@mcp.tool()
def buscar_patron(patron: str, carpeta: str = "."):
    """Búsqueda de cadenas de malicia mediante grep."""
    try:
        resultado = subprocess.check_output(
            ["grep", "-r", "-i", "--exclude-dir={.*,venv,hackathon_env}", patron, carpeta],
            stderr=subprocess.STDOUT,
            text=True
        )
        return resultado if resultado else "Sin coincidencias."
    except subprocess.CalledProcessError:
        return "Búsqueda finalizada sin hallazgos."

@mcp.tool()
def ver_procesos(filtro: str = ""):
    """
    Monitoreo de procesos activos. 
    Permite detectar ejecutables sospechosos o persistencia en memoria.
    """
    procesos = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        info = proc.info
        if filtro.lower() in info['name'].lower() or not filtro:
            procesos.append(f"PID: {info['pid']} | Name: {info['name']} | User: {info['username']}")
    return procesos[:50] # Limitamos a los primeros 50 para no saturar el Inspector

if __name__ == "__main__":
    mcp.run()
