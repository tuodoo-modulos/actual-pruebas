from .utilidades import GenerarFichero, GENERAR_ERROR, Validaciones
from odoo.exceptions import UserError

# Dato Constante =04
FORMA_DE_PAGO = "04"


class PagoConvenioBanorte:
    env = None

    def __init__(self, env):
        self.env = env

    def generar_pagos(self):
        active_ids = self.env.context["active_ids"]

        pagos = self.env["account.payment"].browse(active_ids)
        # No se requieren encabezados.
        lineas = []

        errores = []

        for pago in pagos:
            linea = PagoConvenioLineaBanorte()
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
            append_error(self.validar_importe(pago.amount))
            append_error(self.validar_ref(pago.ref))
            append_error(self.validar_banco(pago.partner_bank_id))
            append_error(self.validar_fecha_vencimiento(pago))

            if True in hay_un_error:
                continue

            linea.clave_de_servicio = pago.partner_bank_id.convenio_id.num_facturador
            linea.forma_de_pago = FORMA_DE_PAGO
            linea.importe = pago.amount
            linea.cuenta_cargo = pago.journal_id.bank_account_id.acc_number
            # Se deja vacio
            linea.cuenta_abono = ''
            
            linea.referencia_1 = pago.ref

            # <!-- 
            # =====================================
            #  Vencimiento de factura
            # =====================================
            # -->
            # Obligatorio según emisora a pagar, ver catalogo.
            # Formato ddmmmaaaa
            fecha_ddmmaaaa = ''

            factura = pago.reconciled_bill_ids[0]
            
            fecha_ddmmaaaa = str(factura.invoice_date_due).split('-')
            fecha_ddmmaaaa.reverse()
            fecha_ddmmaaaa = ''.join(fecha_ddmmaaaa)
            linea.fecha_vencimiento_ddmmaaaa = fecha_ddmmaaaa
            # 
            # <!-- 
            # =====================================
            #  END Vencimiento de factura
            # =====================================
            # -->


            linea.correo_electronico = ''
            linea.referencia_2 = ''
            linea.referencia_3 = ''
            linea.referencia_4 = ''

            lineas.append(linea.procesar_linea())

        if errores:
            raise UserError(GENERAR_ERROR(errores))

        datos = "".join(lineas)

        utilidades = GenerarFichero(self.env)

        return utilidades.descargar_txt("pago_simplificado", datos)

    def validar_fecha_vencimiento(self, pago):
        facturas = pago.reconciled_bill_ids
        if not len(facturas):
            return f"No hay facturas asociadas"

        if len(facturas)>1:
            return f'Hay más de una factura asociada a este pago'

        return None
    
    def validar_partner(self, partner_id):
        if not partner_id:
            return f"El pago no tiene un partner definido"

        return None

    def validar_importe(self, amount):
        if amount <= 0:
            return f"El pago está en 0. Valor actual {amount}"
        return None

    def validar_ref(self, ref):
        if not ref:
            return f"No se definio memo del pago."

        if len(ref) <= 5:
            return f"El memo del pago requiere 6 o más caracteres. Actual: '{ref}'."

        return None

    def validar_banco(self, partner_bank_id):
        # Debe tener un banco
        print(f"bank={partner_bank_id.id}")
        bank = partner_bank_id
        name = partner_bank_id.display_name
        if not bank:
            return "El pago no tiene un banco definido"
        
        # El banco debe estar definido como tipo convenio.
        if not bank.es_tipo_convenio:
            return f"El banco no esta marcado como 'Es tipo convenio'"

        # Si el banco está definido con convenio, entonces tiene
        # que tener un convenio seleccionado.

        if not bank.convenio_id:
            return f"El banco está marcado como 'Es tipo convenio' pero no se le asigno un convenio en el campo 'Convenio Id'."

        return None


class PagoConvenioLineaBanorte:
    clave_de_servicio = None
    forma_de_pago = None
    importe = None
    cuenta_cargo = None
    cuenta_abono = None
    referencia_1 = None
    fecha_vencimiento_ddmmaaaa = None
    correo_electronico = None
    referencia_2 = None
    referencia_3 = None
    referencia_4 = None

    def procesar_linea(self) -> str:
        funciones = [
            self.procesar_clave_de_servicio,
            self.procesar_forma_de_pago,
            self.procesar_importe,
            self.procesar_cuenta_cargo,
            self.procesar_cuenta_abono,
            self.procesar_referencia_1,
            self.procesar_fecha_vencimiento_ddmmaaaa,
            self.procesar_correo_electronico,
            self.procesar_referencia_2,
            self.procesar_referencia_3,
            self.procesar_referencia_4,
        ]

        valores = []
        for f in funciones:
            valor = str(f())
            print(f"valor={valor}")
            valores.append(valor if valor else "")

        return "".join(valores)

    def procesar_clave_de_servicio(self):
        procesar = self.clave_de_servicio
        procesado = str(procesar)
        longitud = 6
        self._validaciones(
            {
                "valor": procesado,
                "longitud": longitud,
                "nombre_valor": "clave_de_servicio",
            }
        )

        procesado = procesado.zfill(longitud)
        return procesado

    def procesar_forma_de_pago(self):
        procesar = self.forma_de_pago
        procesado = str(procesar)
        longitud = 2
        self._validaciones(
            {"valor": procesado, "longitud": longitud, "nombre_valor": "forma_de_pago"}
        )

        procesado = procesado.zfill(longitud)
        return procesado

    def procesar_importe(self):
        procesar = self.importe
        # Importe a Pagar con centavos sin punto decimal ni signo de pesos
        procesado = float(procesar)
        procesado = f"{procesado:.2f}"
        procesado = procesado.replace('.', '')
        longitud = 15
        self._validaciones(
            {"valor": procesado, "longitud": longitud, "nombre_valor": "importe"}
        )

        procesado = procesado.zfill(longitud)
        return procesado

    def procesar_cuenta_cargo(self):
        procesar = self.cuenta_cargo
        procesado = str(procesar)
        longitud = 20
        self._validaciones(
            {"valor": procesado, "longitud": longitud, "nombre_valor": "cuenta_cargo"}
        )

        procesado = procesado.zfill(longitud)
        return procesado

    def procesar_cuenta_abono(self):
        procesar = self.cuenta_abono
        procesado = str(procesar)
        longitud = 20
        self._validaciones(
            {"valor": procesado, "longitud": longitud, "nombre_valor": "cuenta_abono"}
        )

        procesado = procesado.zfill(longitud)
        return procesado

    def procesar_referencia_1(self):
        procesar = self.referencia_1
        procesado = str(procesar)
        longitud = 40
        self._validaciones(
            {"valor": procesado, "longitud": longitud, "nombre_valor": "referencia_1"}
        )

        # Requiere espacios a la derecha
        procesado = procesado + self.calcular_espacios(procesado,longitud)
        return procesado

    def procesar_fecha_vencimiento_ddmmaaaa(self):
        procesar = self.fecha_vencimiento_ddmmaaaa
        procesado = str(procesar)
        longitud = 8
        self._validaciones(
            {
                "valor": procesado,
                "longitud": longitud,
                "nombre_valor": "fecha_vencimiento_ddmmaaaa",
            }
        )
        return procesado

    def procesar_correo_electronico(self):
        procesar = self.correo_electronico
        procesado = str(procesar)
        longitud = 40
        self._validaciones(
            {
                "valor": procesado,
                "longitud": longitud,
                "nombre_valor": "correo_electronico",
            }
        )

        procesado = procesado + self.calcular_espacios(procesado, longitud)
        return procesado

    def procesar_referencia_2(self):
        procesar = self.referencia_2
        procesado = str(procesar)
        longitud = 40
        self._validaciones(
            {"valor": procesado, "longitud": longitud, "nombre_valor": "referencia_2"}
        )

        procesado = procesado + self.calcular_espacios(procesado, longitud)
        return procesado

    def procesar_referencia_3(self):
        procesar = self.referencia_3
        procesado = str(procesar)
        longitud = 40
        self._validaciones(
            {"valor": procesado, "longitud": longitud, "nombre_valor": "referencia_3"}
        )

        procesado = procesado + self.calcular_espacios(procesado, longitud)
        return procesado

    def procesar_referencia_4(self):
        procesar = self.referencia_4
        procesado = str(procesar)
        longitud = 40
        self._validaciones(
            {"valor": procesado, "longitud": longitud, "nombre_valor": "referencia_4"}
        )

        procesado = procesado + self.calcular_espacios(procesado, longitud)
        return procesado

    def _validaciones(
        self, opciones={"valor": None, "longitud": 0, "nombre_valor": None}
    ):
        Validaciones().validar_logintud_maxima(**opciones)

    def calcular_espacios(self, string, longitud):
        return ' '*(longitud - len(string))