# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from .utilidades import GenerarFichero, GENERAR_ERROR, Validaciones


class ActualWizardPagos(models.Model):
    _name = "actual.wizard.pagos"
    _description = "Actual | Generar layout de pagos"

    fecha_de_aplicacion = fields.Date(
        help="Esta fecha aplica para el campo 'Fecha aplicacion' del layout de pago simplificado",
        default=datetime.today(),
    )

    def pago_simplificado(self):
        active_ids = self.env.context["active_ids"]

        pagos = self.env["account.payment"].browse(active_ids)
        # No se requieren encabezados.
        lineas = []

        errores = []

        for pago in pagos:
            linea = PagoSimplificadoLinea()
            nombre_pago = pago.name
            hay_un_error = []

            def append_error(error):
                if error:
                    nombre_proveedor = (
                        pago.partner_id.name.upper()
                        if pago.partner_id
                        else "SIN PROVEEDOR"
                    )

                    errores.append(f"{nombre_proveedor } [{nombre_pago}] - {error}")
                    hay_un_error.append(True)

            append_error(self.validar_partner(pago.partner_id))
            append_error(self.validar_banco(pago.partner_bank_id))
            append_error(self.validar_partner_ref(pago.partner_id))
            append_error(self.validar_amount(pago.amount))
            append_error(self.validar_ref(pago.ref))
            append_error(self.validar_rfc(pago.partner_id.vat))

            if True in hay_un_error:
                continue

            linea.operacion = pago.partner_bank_id.tipo_operacion
            linea.clave_id = pago.partner_id.ref

            linea.cuenta_origen = "SINDEFINIR"  # Account.journal_bank.account???

            # <!--
            # =====================================
            #  Cuenta clabe destino
            # =====================================
            # -->
            # Previamente validamos que algúno de las
            # dos opciones este seleccionada.
            cuenta = pago.partner_bank_id.acc_number
            if pago.partner_bank_id.tipo == "clabe":
                cuenta = pago.partner_bank_id.tipo
            linea.cuenta_clabe_destino = cuenta
            #
            # <!--
            # =====================================
            #  END Cuenta clabe destino
            # =====================================
            # -->

            linea.importe = pago.amount
            linea.referencia = ""
            linea.descripción = pago.ref
            linea.rfc_ordenante = pago.partner_id.vat
            linea.iva = 0

            linea.fecha_aplicacion = pago.date
            linea.instrucción_de_pago = "X"
            linea.clave_tipo_cambio = "0"

            lineas.append(linea.procesar_linea())

        if errores:
            raise UserError(GENERAR_ERROR(errores))

        datos = "".join(lineas)

        utilidades = GenerarFichero(self.env)

        return utilidades.descargar_txt("pago_simplificado", datos)

    def validar_partner(self, partner_id):
        if not partner_id:
            return f"El pago no tiene un partner definido"
        return None

    def validar_rfc(self, rfc):
        if not rfc:
            return f"No hay un RFC definido."
        return None

    def validar_ref(self, ref):
        if not ref:
            return f"No se definio memo del pago."

        if len(ref) <= 5:
            return f"La memo del pago requiere 6 o más caracteres. Actual: '{ref}'."

        return None

    def validar_amount(self, amount):
        if amount <= 0:
            return f"El pago está en 0. Valor actual {amount}"
        return None

    def validar_banco(self, partner_bank_id):
        # Debe tener un banco
        print(f"bank={partner_bank_id.id}")
        bank = partner_bank_id
        name = partner_bank_id.display_name
        if not bank:
            return "El pago no tiene un banco definido"
        if not bank.tipo_operacion:
            return f"El {name} no tiene tipo de operación definida"

        if not bank.tipo:
            return f"El {name} no tiene selector tipo (CLABE/Cueta) definido"

        if bank.tipo == "clabe" and not bank.l10n_mx_edi_clabe:
            return f"Se definio el tipo como 'CLABE', pero no hay defina una clave en '{name}'"

        if bank.tipo == "cuenta" and not bank.acc_number:
            return f"Se definio el tipo como 'Cuenta', pero no hay defina una cuenta en '{name}'"

        return None

    def validar_partner_ref(self, partner_id):
        if not partner_id.ref:
            return f"El proveedor no tiene definida una referencia"
        return None

    def pago_convenio(self):
        datos = "PAGO CONVENIO EN DESARROLLO"
        utilidades = GenerarFichero(self.env)
        return utilidades.descargar_txt("pago_convenio", datos)


class PagoSimplificadoLinea:
    operacion = None
    clave_id = None
    cuenta_origen = None
    cuenta_clabe_destino = None
    importe = None
    referencia = None
    descripción = None
    rfc_ordenante = None
    iva = None
    fecha_aplicacion = None
    instrucción_de_pago = None
    clave_tipo_cambio = None

    def procesar_linea(self) -> str:
        funciones = [
            self._procesar_operacion,
            self._procesar_clave_id,
            self._procesar_cuenta_origen,
            self._procesar_cuenta_clabe_destino,
            self._procesar_importe,
            self._procesar_referencia,
            self._procesar_descripción,
            self._procesar_rfc_ordenante,
            self._procesar_iva,
            self._procesar_fecha_aplicacion,
            self._procesar_instrucción_de_pago,
            self._procesar_clave_tipo_cambio,
        ]

        valores = []
        for f in funciones:
            valor = str(f())
            print(f"valor={valor}")
            valores.append(valor if valor else "")

        return "\t".join(valores)

    def _procesar_operacion(self):
        procesar = self.operacion
        procesado = str(procesar)
        self._validaciones(
            {"valor": procesado, "longitud": 2, "nombre_valor": "operacion"}
        )
        procesado = procesar
        return procesado

    def _procesar_clave_id(self):
        procesar = self.clave_id
        procesado = str(procesar)
        self._validaciones(
            {"valor": procesado, "longitud": 13, "nombre_valor": "clave_id"}
        )
        procesado = procesar
        return procesado

    def _procesar_cuenta_origen(self):
        procesar = self.cuenta_origen
        procesado = str(procesar)
        self._validaciones(
            {"valor": procesado, "longitud": 10, "nombre_valor": "cuenta_origen"}
        )
        procesado = procesar
        return procesado

    def _procesar_cuenta_clabe_destino(self):
        procesar = self.cuenta_clabe_destino
        procesado = str(procesar)
        self._validaciones(
            {"valor": procesado, "longitud": 20, "nombre_valor": "cuenta_clabe_destino"}
        )
        procesado = procesar
        return procesado

    def _procesar_importe(self):
        procesar = self.importe
        procesado = str(procesar)
        self._validaciones(
            {"valor": procesado, "longitud": 16, "nombre_valor": "importe"}
        )
        procesado = procesar
        return procesado

    def _procesar_referencia(self):
        procesar = self.referencia
        procesado = str(procesar)
        self._validaciones(
            {"valor": procesado, "longitud": 10, "nombre_valor": "referencia"}
        )
        procesado = procesar
        return procesado

    def _procesar_descripción(self):
        procesar = self.descripción
        procesado = str(procesar)
        self._validaciones(
            {"valor": procesado, "longitud": 30, "nombre_valor": "descripción"}
        )
        procesado = procesar
        return procesado

    def _procesar_rfc_ordenante(self):
        procesar = self.rfc_ordenante
        procesado = str(procesar)
        self._validaciones(
            {"valor": procesado, "longitud": 13, "nombre_valor": "rfc_ordenante"}
        )
        procesado = procesar
        return procesado

    def _procesar_iva(self):
        procesar = self.iva
        procesado = str(procesar)
        self._validaciones({"valor": procesado, "longitud": 14, "nombre_valor": "iva"})
        procesado = procesar
        return procesado

    def _procesar_fecha_aplicacion(self):
        procesar = self.fecha_aplicacion
        procesado = str(procesar)

        # Formato fecha: ddmmaaaa
        procesado = procesado.split("-")
        procesado = procesado[::-1]
        procesado = "".join(procesado)
        self._validaciones(
            {"valor": procesado, "longitud": 8, "nombre_valor": "fecha_aplicacion"}
        )
        procesado = procesar
        return procesado

    def _procesar_instrucción_de_pago(self):
        procesar = self.instrucción_de_pago
        procesado = str(procesar)
        self._validaciones(
            {"valor": procesado, "longitud": 100, "nombre_valor": "instrucción_de_pago"}
        )
        procesado = procesar
        return procesado

    def _procesar_clave_tipo_cambio(self):
        procesar = self.clave_tipo_cambio
        procesado = str(procesar)
        self._validaciones(
            {"valor": procesado, "longitud": 7, "nombre_valor": "clave_tipo_cambio"}
        )
        procesado = procesar
        return procesado

    def _validaciones(
        self, opciones={"valor": None, "longitud": 0, "nombre_valor": None}
    ):
        Validaciones().validar_logintud_maxima(**opciones)
