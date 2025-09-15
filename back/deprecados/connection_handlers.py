from flask import request
from flask_socketio import disconnect
from os.path import exists, join
from shutil import rmtree
from globals import globals


def cleanup_files(unique_folder_name: str) -> None:
    base_folder = "./zip_tests/"
    final_work_folder = join(base_folder, unique_folder_name)
    if exists(final_work_folder):
        try:
            rmtree(final_work_folder)
        except Exception as e:
            print(f"Error deleting folder: {e}")

def handle_connect() -> None:
    """
    Armazena SID para ELIMINAR arquivos
    Decore com @socketio.on('connect')
    """
    uid = request.args.get('uid')
    
    if uid and uid in globals.active_tasks:
        globals.active_tasks[uid]['uids'].add(uid)
        return
    # else
    disconnect()

def handle_disconnect() -> None:
    """
    ELIMINA e ANIQUILA Arquivos
    Decore com @socketio.on('disconnect')
    """
    uid = request.args.get('uid')
    for task_id, data in list(globals.active_tasks.items()):
        if uid in data['uids']:
            data['uids'].remove(uid)
            if not data['uids']:
                cleanup_files(task_id)
                del globals.active_tasks[task_id]
            break

