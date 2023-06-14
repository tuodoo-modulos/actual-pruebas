# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger('[ ACTUAL - RES PARTNER]')


class ResPartner(models.Model):
    _inherit = "res.partner"

    def abrir_wizard(self):
        return {
            "name": "Lista de altas/bajas",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "res_model": "actual.wizard.altas_bajas",
            "target": "new",
            "view_id": self.env.ref(
                "actual_pago_proveedores.actual_wizard_altas_bajas_view_form"
            ).id,
            "context": {"active_ids": self.env.context["active_ids"]},
        }
