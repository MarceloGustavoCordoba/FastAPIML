from models.clases import cliente
from models.clases import HandleDB
import os, logging, traceback
from datetime import datetime
carpeta_logs = 'logs'
if not os.path.exists(carpeta_logs):
    os.makedirs(carpeta_logs)
    
ruta_archivo_log = os.path.join(carpeta_logs, f"log_pruebas{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=ruta_archivo_log, level=logging.info)
db = HandleDB()

async def carga_inicial():
    
    try: 
        logging.info(f"Consultando lista de clientes.")
        clientes = db.cliente_pendiente_carga()
        if len(clientes) > 0:
            logging.info(f"Clientes a cargar {clientes}")
            logging.info(f"Iniciando ciclo..")
            for cli in clientes:
                cliente_actual = cliente()
                logging.info(f"Cargando variables del cliente.")
                cliente_actual.existente(cli)
                logging.info(f"Cargando cliente {cliente_actual.nickname} \n Ordenes Historicas...")
                cliente_actual.ordenes_historicas(cliente_actual.user_id)
                logging.info(f"Ordenes...")
                ordenes = db.chequeo_ordenes(cliente_actual.user_id)
                cliente_actual.cargar_ordenes(cliente_actual.user_id,ordenes)
                logging.info(f"Envios...")
                cliente_actual.cargar_envios(cliente_actual.user_id)
                logging.info(f"Items...")
                cliente_actual.items(cliente_actual.user_id)
                logging.info(f"Preguntas...")
                cliente_actual.preguntas(cliente_actual.user_id)
                logging.info(f"Publicidad...")
                cliente_actual.publicidad(cliente_actual.user_id)
                logging.info(f"Stock con cargo...")
                cliente_actual.stock_con_cargo()
        else:
            logging.info(f"Sin clientes por cargar")

        return 200
    except Exception as e:
            logging.error(f"Error carga incial: {e} \n {traceback.format_exc()}")
            raise

async def procesar_notificaciones():
    clientes = db.clientes_con_notificaciones()
    logging.info(f"Consultando notificaciones.")

    for cli in clientes:
        cliente_actual = cliente()
        cliente_actual.existente(cli)
        logging.info(f"Chequeando cliente {cli}")

        logging.info(f"Ordenes..")
        ordenes_not=cliente_actual.db.check_orders_v2(cliente_actual.user_id)
        logging.info(f"Preguntas..")
        preguntas=cliente_actual.db.check_questions(cliente_actual.user_id)
        logging.info(f"Envios..")
        envios=cliente_actual.db.check_shipments(cliente_actual.user_id)
        logging.info(f"Items..")
        items=cliente_actual.db.check_items(cliente_actual.user_id)

        if len(ordenes_not) > 0:
            logging.info(f"Actualizando ordenes")
            ordenes = cliente_actual.db.ids_order_v2(cliente_actual.user_id,ordenes_not)
            res_1 = cliente_actual.cargar_ordenes(cliente_actual.user_id,ordenes)
            res_2 = cliente_actual.cargar_envios(cliente_actual.user_id)
            if res_1 == 200 and res_2 == 200:
                db.marcar_notificaciones(ordenes_not)
                logging.info(f"Notificaciones actualizadas")
        else:
            logging.info(f"No hay ordenes por cargar.")

        if len(items) > 0:
            logging.info(f"Actualizando items.")
            items_ids = cliente_actual.db.ids_items(cliente_actual.user_id,items)
            res = cliente_actual.act_items(items_ids)
            if res == 200:
                db.marcar_notificaciones(items)
                logging.info(f"Notificaciones actualizadas.")
        else:
            logging.info(f"No hay items por actualizar.")

        if len(preguntas) > 0:
            logging.info(f"Actualizando preguntas.")
            preguntas_id = cliente_actual.db.ids_questions(cliente_actual.user_id,preguntas)
            res = cliente_actual.act_preguntas(preguntas_id)
            if res == 200:
                db.marcar_notificaciones(preguntas)
                logging.info(f"Notificaciones actualizadas.")
        else:
            logging.info(f"No hay preguntas por actualizar.")

        if len(envios) > 0:
            logging.info(f"Actualizando envios.")
            envios_id = cliente_actual.db.ids_shipments(cliente_actual.user_id,envios)
            res = cliente_actual.act_envios(envios_id)
            if res == 200:
                db.marcar_notificaciones(envios)
                logging.info(f"Notificaciones actualizadas.")
        else:
            logging.info(f"No hay envios por actualizar")
        
        logging.info(f"Cargando stock con cargo.")
        cliente_actual.stock_con_cargo()