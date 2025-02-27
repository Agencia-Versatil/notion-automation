import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class NotionTaskManager:
    def __init__(self):
        load_dotenv()
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")

        if not self.notion_token or not self.database_id:
            raise ValueError("Faltan las variables de entorno: NOTION_TOKEN y NOTION_DATABASE_ID")
        
        self.client = Client(auth=self.notion_token)
        logger.info("✅ NotionTaskManager inicializado correctamente")

    def get_tasks(self) -> List[Dict]:
        try:
            response = self.client.databases.query(database_id=self.database_id)
            tasks = response.get("results", [])
            logger.info(f"📋 {len(tasks)} tareas encontradas en Notion")
            return tasks
        except APIResponseError as e:
            logger.error(f"❌ Error al obtener tareas: {str(e)}")
            return []

    def update_task(self, page_id: str, properties: Dict[str, Any]) -> None:
        try:
            self.client.pages.update(page_id=page_id, properties=properties)
            logger.info(f"✅ Tarea {page_id} actualizada correctamente")
        except APIResponseError as e:
            logger.error(f"❌ Error al actualizar tarea {page_id}: {str(e)}")

    def mark_complete(self, page_id: str) -> None:
        properties = {
            "Estado": {"status": {"name": "Listo"}},
            "Fecha entrega": {"date": {"start": datetime.now().date().isoformat()}}
        }
        self.update_task(page_id, properties)

def process_tasks():
    manager = NotionTaskManager()
    tasks = manager.get_tasks()

    for task in tasks:
        task_id = task["id"]
        properties = task.get("properties", {})
        estado = properties.get("Estado", {}).get("status", {}).get("name", "")
        departamento = properties.get("Departamentos", {}).get("multi_select", [])

        propiedades_notion = {
            "Tarea": {"title": [{"text": {"content": properties.get("Tarea", {}).get("title", "")}}]},
            "Estado": {"status": {"name": estado}},
            "Prioridad": {"select": {"name": properties.get("Prioridad", {}).get("select", "")}},
            "Descripción": {"rich_text": [{"text": {"content": properties.get("Descripción", {}).get("rich_text", "")}}]}
        }

        if departamento:
            propiedades_notion["Departamentos"] = {"multi_select": [{"name": departamento}]}

        if estado == "En curso":
            manager.mark_complete(task_id)
            logger.info(f"✔️ Tarea {task_id} marcada como completada")

if __name__ == "__main__":
    process_tasks()

