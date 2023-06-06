# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, date
import base64
import re

from .utilidades import GenerarFichero, Validaciones, GENERAR_ERROR

import logging

_logger = logging.getLogger("[ ACTUAL - WIZARD ALTAS/BAJAS]")


class TipoOperacion:
    alta_de_registro = "AR"
    alta_de_cuenta = "AC"
    baja_de_registro = "BR"
    baja_de_cuenta = "BC"

    @staticmethod
    def generar_select():
        """Retorna una lista de tuplas para un select"""
        return [
            (TipoOperacion.alta_de_registro, "Alta de registro"),
            (TipoOperacion.alta_de_cuenta, "Alta de cuenta"),
            (TipoOperacion.baja_de_registro, "Baja de registro"),
            (TipoOperacion.baja_de_cuenta, "Baja de cuenta"),
        ]


class ActualWizardAltasBajas(models.Model):
    _name = "actual.wizard.altas_bajas"
    _description = "Actual | Generar layout de altas/bajas para proveedores"

    tipo = fields.Selection(
        TipoOperacion.generar_select(),
        default=TipoOperacion.alta_de_registro,
        string="Tipo operacion",
    )

    def generar(self):
        active_ids = self.env.context["active_ids"]

        partners = self.env["res.partner"].browse(active_ids)

        lineas = []
        errores = []

        for partner in partners:
            linea = AltaBajaLinea()
            hay_un_error = []

            # <!--
            # =====================================
            #  Los tipo convenio no entran aquí.
            # =====================================
            # -->

            if partner.es_tipo_convenio:
                _logger.info(f"{partner.name} se omitio por que es tipo convenio")
                continue
            #
            # <!--
            # =====================================
            #  END Los tipo convenio no entran aquí.
            # =====================================
            # -->

            def append_error(error):
                if error:
                    nombre_partner = partner.name.upper()
                    errores.append(f"[{nombre_partner }] - {error}")
                    hay_un_error.append(True)

            # El tipo cuenta viene de los bank.
            # Como es un many2Many tomamos el primero YOLOTL.
            bank = partner.bank_ids[0]
            tipo_cuenta = bank.tipo_cuenta

            append_error(self.validar_operacion(self.tipo))
            append_error(self.validar_tipo_cuenta(bank))
            append_error(self.validar_moneda(bank))

            for e in self.validar_partner(partner, self.tipo):
                append_error(e)

            if True in hay_un_error:
                continue

            # <!--
            # =====================================
            #  Asignación de valores.
            # =====================================
            # -->
            linea.clave_id = partner.ref
            linea.operación = self.tipo
            linea.nombre = partner.name
            linea.rfc = partner.vat
            linea.telefono = partner.phone
            linea.contacto = ""
            linea.e_mail = partner.email

            linea.tipo_cuenta = tipo_cuenta

            linea.moneda = bank.currency_id.name
            linea.banco = bank.bank_id.l10n_mx_edi_code

            # En caso de tratarse de un AR ó BR debe indicarse una "X"

            valor_clabe = "X"
            if self.tipo not in ["AR", "BR"]:
                valor_clabe = bank.l10n_mx_edi_clabe
            linea.cuenta_clabe = valor_clabe

            # <!--
            # =====================================
            #  END Asignación de valores.
            # =====================================
            # -->

            lineas.append(linea.procesar_linea())

        if errores:
            raise UserError(GENERAR_ERROR(errores))

        datos = "".join(lineas)
        return GenerarFichero(self.env).descargar_txt("nombre_fichero", datos)

    def validar_partner(self, partner, tipo):
        msj = []
        if not partner.name:
            msj.append(f"No se definio el nombre para el partner")

        if not partner.ref:
            msj.append(
                f"No se definio la referencia. Es el equivalente al campo Clave ID."
            )

        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron, partner.email):
            msj.append(f"'{partner.email}' no parece ser un correo valido.")

        return msj

    def validar_operacion(self, tipo_operacion):
        if not tipo_operacion:
            return f"No se definio el tipo de operacion"

        return None

    def validar_tipo_cuenta(self, bank):
        if not bank.tipo_cuenta:
            return f"No se definio el tipo de cuenta en {bank.display_name}"

        return None

    def validar_moneda(self, bank):
        if not bank.currency_id:
            return f"No se definio el tipo de moneda en {bank.display_name}"

        if not bank.currency_id.name:
            return f"No se definio el nombre de la moneda en {bank.currency_id}"

        tipos_de_moneda = ["PESOS", "DOLARES"]
        if bank.currency_id.name not in tipos_de_moneda:
            return f"El nombre de la moneda '{bank.currency_id.name}' no coincide contra los tipos esperados para el layout {', '.join(tipos_de_moneda)}"

        return None


class AltaBajaLinea:
    clave_id = None
    operación = None
    nombre = None
    rfc = None
    telefono = None
    contacto = None
    e_mail = None
    tipo_cuenta = None
    moneda = None
    banco = None
    cuenta_clabe = None

    def procesar_linea(self) -> str:
        funciones = [
            self._procesar_clave_id,
            self._procesar_operacion,
            self._procesar_nombre,
            self._procesar_rfc,
            self._procesar_telefono,
            self._procesar_contacto,
            self._procesar_e_mail,
            self._procesar_tipo_cuenta,
            self._procesar_moneda,
            self._procesar_banco,
            self._procesar_cuenta_clabe,
        ]

        valores = []
        for f in funciones:
            valor = str(f())
            print(f"valor={valor}")
            valores.append(valor if valor else "")

        return "\t".join(valores)

    def _procesar_clave_id(self):
        procesar = self.clave_id
        procesado = str(procesar)
        procesado = procesar.strip()
        procesado = self._validaciones(
            {"valor": procesado, "longitud": 13, "nombre_valor": "clave_id"}
        )
        return procesado

    def _procesar_operacion(self):
        procesar = self.operación
        procesado = str(procesar)
        procesado = self._validaciones(
            {"valor": procesado, "longitud": 2, "nombre_valor": "operación"}
        )
        return procesado

    def _procesar_nombre(self):
        procesar = self.nombre
        procesado = str(procesar)

        # Sin puntos, ni comas
        valores = [",", "."]
        for valor in valores:
            procesado = procesado.replace(valor, " ")

        procesado = self._validaciones(
            {"valor": procesado, "longitud": 60, "nombre_valor": "nombre"}
        )
        return procesado

    def _procesar_rfc(self):
        procesar = self.rfc
        procesado = str(procesar)
        procesado = self._validaciones(
            {"valor": procesado, "longitud": 13, "nombre_valor": "rfc"}
        )
        return procesado

    def _procesar_telefono(self):
        procesar = self.telefono
        procesado = str(procesar)
        procesado = self._validaciones(
            {"valor": procesado, "longitud": 15, "nombre_valor": "telefono"}
        )
        return procesado

    def _procesar_contacto(self):
        procesar = self.contacto
        procesado = str(procesar)
        procesado = self._validaciones(
            {"valor": procesado, "longitud": 20, "nombre_valor": "contacto"}
        )
        return procesado

    def _procesar_e_mail(self):
        procesar = self.e_mail
        procesado = str(procesar)
        procesado = self._validaciones(
            {"valor": procesado, "longitud": 39, "nombre_valor": "e_mail"}
        )
        return procesado

    def _procesar_tipo_cuenta(self):
        procesar = self.tipo_cuenta
        procesado = str(procesar)
        procesado = self._validaciones(
            {"valor": procesado, "longitud": 3, "nombre_valor": "tipo_cuenta"}
        )
        return procesado

    def _procesar_moneda(self):
        procesar = self.moneda
        procesado = str(procesar)

        if procesado == "MXN":
            procesado = "PESOS"
        if procesado == "USD":
            procesado = "DOLARES"

        procesado = self._validaciones(
            {"valor": procesado, "longitud": 7, "nombre_valor": "moneda"}
        )
        return procesado

    def _procesar_banco(self):
        procesar = self.banco
        procesado = str(procesar)
        procesado = self._validaciones(
            {"valor": procesado, "longitud": 4, "nombre_valor": "banco"}
        )
        return procesado

    def _procesar_cuenta_clabe(self):
        procesar = self.cuenta_clabe
        procesado = str(procesar)
        procesado = self._validaciones(
            {"valor": procesado, "longitud": 18, "nombre_valor": "cuenta_clabe"}
        )
        return procesado

    def _validaciones(
        self, opciones={"valor": None, "longitud": 0, "nombre_valor": None}
    ):
        utilidades = Validaciones()
        utilidades.validar_logintud_maxima(**opciones)
