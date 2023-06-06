# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    tipo_operacion = fields.Selection(
        [
            ("01", "Propias"),
            ("03", "Terceros"),
            ("04", "SPEI"),
            ("05", "TEF"),
            ("07", "OPIs"),
        ]
    )

    tipo = fields.Selection([("clabe", "CLABE"), ("cuenta", "Cuenta")])

    tipo_cuenta = fields.Selection(
        [
            ("001", "Cuenta"),
            ("040", "CLABE"),
            ("003", "Tarjeta de débito"),
            ("100", "TdC Banorte terceros"),
            ("110", "TdC Otros Bancos"),
            ("120", "TdC Amex"),
        ]
    )
