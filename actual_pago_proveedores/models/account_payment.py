# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def abrir_wizard(self):
        return {
            "name": "Lista de pagos",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "res_model": "actual.wizard.pagos",
            "target": "new",
            "view_id": self.env.ref(
                "actual_pago_proveedores.actual_wizard_pagos_view_form"
            ).id,
            "context": {"active_ids": self.env.context["active_ids"]},
        }
