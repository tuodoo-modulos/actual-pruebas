import logging
import base64
from datetime import date, datetime
_logger = logging.getLogger("[GENERAR FICHEROS]")
from odoo.exceptions import UserError

class GenerarFichero:

    env = None
    def __init__(self, env) -> None:
        self.env = env

    def descargar_txt(self, nombre_fichero, datos):
        self.eliminar_adjuntos_anteriores()

        nombre_fichero = self.generar_nombre_fichero(nombre_fichero)
        # encode
        result = base64.b64encode(bytes(datos, "utf-8"))
        # get base url
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        attachment_obj = self.env["ir.attachment"]
        # create attachment
        attachment_id = attachment_obj.create(
            {"name": nombre_fichero, "mimetype": "text/plain", "datas": result}
        )
        # prepare download url
        download_url = "/web/content/" + str(attachment_id.id) + "?download=true"
        # download
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

    def generar_nombre_fichero(self, nombre):
        fecha_actual = str(date.today()).replace("-", "_")
        return f"{nombre}_{fecha_actual}"

    def eliminar_adjuntos_anteriores(self):
        registros = self.env["actual.adjuntos.pagos"].search([])
        for r in registros:
            r.adjunto_id.unlink()
            r.unlink()


def GENERAR_ERROR(errores):
    '''
    Recibe una lista de errores como strings. 
    
    '''

    errores = "".join([f"\t-{e} \n" for e in errores])
    msj = f"""
Se encontraron los siguientes errores al generar el layout.

{errores}

No se puede continuar.
"""
    return msj


class Validaciones:

    def validar_logintud_maxima(self, valor, longitud, nombre_valor):
        msj = f"""Se excedio el límite de longitud para {nombre_valor}.
                El valor recibido es '{valor}' y su longitud es {len(valor)}
                superando a {longitud} que es la definida para el campo."""
        if valor:
            if len(valor) > longitud:
                raise UserError(msj)
