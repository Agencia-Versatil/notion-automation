import requests
import datetime

# Credenciales de Notion
NOTION_TOKEN = "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"
DATABASE_ID = "19832c55109b81ec8b6cc9580f697466"
NOTION_URL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
CREATE_URL = "https://api.notion.com/v1/pages"

# Configurar las cabeceras para la solicitud HTTP
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Estados válidos en Notion
ESTADOS_VALIDOS = [
    "Sin iniciar", "Necesita revisión", "En curso", "Revisión cliente", "En confirmación", "Listo"
]

# Obtener tareas nuevas desde Notion
def obtener_tareas():
    response = requests.post(NOTION_URL, headers=headers)
    if response.status_code == 200:
        tareas = response.json().get("results", [])
        return tareas
    else:
        print("Error al obtener tareas:", response.text)
        return []

# Procesar y agregar tareas a Notion
def procesar_tareas():
    tareas = obtener_tareas()
    for tarea in tareas:
        propiedades = tarea["properties"]
        
        # Validaciones para evitar errores
        nombre = propiedades.get("Tarea", {}).get("title", [])
        if not nombre:
            print("⚠️ Advertencia: Se encontró una tarea sin título. Saltando...")
            continue
        nombre = nombre[0]["text"]["content"]
        
        departamento = propiedades.get("Departamentos", {}).get("multi_select", [])
        departamento = departamento[0]["name"] if departamento else ""
        
        prioridad = propiedades.get("Prioridad", {}).get("select")
        prioridad = prioridad["name"] if prioridad else "Media"
        
        responsable = propiedades.get("Responsable", {}).get("people", [])
        responsable_id = responsable[0]["id"] if responsable else ""
        
        fecha_inicio = datetime.datetime.utcnow().isoformat()
        
        descripcion = propiedades.get("Descripción", {}).get("rich_text", [])
        descripcion = descripcion[0]["text"]["content"] if descripcion else "Sin descripción"
        
        estado = propiedades.get("Estado", {}).get("status", {}).get("name", "Sin iniciar")
        if estado not in ESTADOS_VALIDOS:
            estado = "Sin iniciar"
        
        # Construcción dinámica de las propiedades para evitar errores
        propiedades_notion = {
            "Tarea": {"title": [{"text": {"content": nombre}}]},
            "Estado": {"status": {"name": estado}},
            "Departamentos": {"multi_select": [{"name": departamento}]} if departamento else {},
            "Prioridad": {"select": {"name": prioridad}},
            "Descripción": {"rich_text": [{"text": {"content": descripcion}}]}
        }
        
        # Agregar Responsable solo si existe
        if responsable_id:
            propiedades_notion["Responsable"] = {"people": [{"id": responsable_id}]}
        
        # Agregar Fecha de inicio solo si Notion tiene esa propiedad
        if "Fecha de inicio" in propiedades:
            propiedades_notion["Fecha de inicio"] = {"date": {"start": fecha_inicio}}
        
        # Crear nueva tarea en Notion
        data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": propiedades_notion
        }
        
        response = requests.post(CREATE_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ Tarea '{nombre}' procesada con éxito.")
        else:
            print(f"❌ Error al procesar la tarea '{nombre}':", response.text)

# Ejecutar la automatización
procesar_tareas()

