import requests
import datetime

# Credenciales de Notion
NOTION_TOKEN = "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"
DATABASE_ID = "19832c55109b81ec8b6cc9580f697466"
NOTION_URL = "https://api.notion.com/v1/pages"

# Configurar las cabeceras para la solicitud HTTP
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Función para establecer la prioridad
def definir_prioridad(nivel):
    niveles_permitidos = ["Alta", "Media", "Baja"]
    return {"select": {"name": nivel}} if nivel in niveles_permitidos else None

# Obtener la fecha actual en formato ISO 8601
fecha_actual = datetime.datetime.utcnow().isoformat()

# Leer la tarea desde un archivo externo
try:
    with open("tasks.txt", "r") as file:
        lines = file.readlines()
        tarea = lines[0].strip()
        departamento = lines[1].strip()
        prioridad = lines[2].strip()
        responsable_id = lines[3].strip()  # ID del usuario en Notion
        descripcion = lines[4].strip() if len(lines) > 4 else ""
except Exception as e:
    print("Error al leer el archivo de tareas:", e)
    exit()

# Datos de la nueva tarea
data = {
    "parent": {"database_id": DATABASE_ID},
    "properties": {
        "Tarea": {"title": [{"text": {"content": tarea}}]},  
        "Estado": {"status": {"name": "Sin iniciar"}},  
        "Departamentos": {"multi_select": [{"name": departamento}]} if departamento else {},
        "Responsable": {"people": [{"id": responsable_id}]} if responsable_id else {},  
        "Prioridad": definir_prioridad(prioridad),
        "Descripción": {"rich_text": [{"text": {"content": descripcion}}]} if descripcion else {},
        "Fecha de creación": {"date": {"start": fecha_actual}}  
    }
}

# Enviar la solicitud a Notion
response = requests.post(NOTION_URL, headers=headers, json=data)

# Mostrar la respuesta para depuración
print("Código de respuesta:", response.status_code)
print("Respuesta:", response.text)

