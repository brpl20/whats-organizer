from typing import Dict

from os.path import exists, join
from shutil import rmtree

active_tasks: Dict[str, Dict[str, str]] = {}

def cleanup_files(unique_folder_name: str) -> None:
    base_folder = "./zip_tests/"
    final_work_folder = join(base_folder, unique_folder_name)
    if exists(final_work_folder):
        try:
            rmtree(final_work_folder)
        except Exception as e:
            print(f"Error deleting folder: {e}")

def handle_connect(sid: str, environ: Dict[str, str]) -> None:
    """
    Armazena SID para ELIMINAR arquivos
    Decore com @socketio.on('connect')
    """
    query_string = environ.get('QUERY_STRING', '')
    task_id = query_string.split('task_id=')[-1] if 'task_id=' in query_string else None
    
    if task_id:
        active_tasks[sid] = {
            'task_id': task_id,
        }

def handle_disconnect(sid: str) -> None:
    """
    ELIMINA Arquivos
    Decore com @socketio.on('disconnect')
    """
    if sid in active_tasks:
        task_data = active_tasks[sid]
        cleanup_files(task_data['task_id'])
        del active_tasks[sid]
