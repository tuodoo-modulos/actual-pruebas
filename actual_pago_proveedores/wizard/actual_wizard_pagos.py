# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from .utilidades import GenerarFichero, GENERAR_ERROR, Validaciones
from .pago_simplificado_banorte import PagoSimplificadoBanorte
from .pago_convenio_banorte import PagoConvenioBanorte


class ActualWizardPagos(models.Model):
    _name = "actual.wizard.pagos"
    _description = "Actual | Generar layout de pagos"

    fecha_de_aplicacion = fields.Date(
        help="Esta fecha aplica para el campo 'Fecha aplicacion' del layout de pago simplificado",
        default=datetime.today(),
    )

    def pago_simplificado(self):
        return PagoSimplificadoBanorte(self.env, self).generar_pagos()

    def pago_convenio(self):
        return PagoConvenioBanorte(self.env).generar_pagos()
