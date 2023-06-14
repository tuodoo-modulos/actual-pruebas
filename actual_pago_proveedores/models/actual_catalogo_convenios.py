# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ActualCatalogoConvenios(models.Model):
    _name = "actual.catalogo.convenio"
    _description = "Catálogo de convenios"

    num_facturador = fields.Char()
    name = fields.Char(related="nombre_facturador", string="Nombre", store=True)

    num_facturador = fields.Char()
    nombre_facturador = fields.Char()
    clave_de_facturador = fields.Char()
    forma_de_pago = fields.Char()
    fecha_de_vencimiento_obligatoria = fields.Char()
    referencia_1 = fields.Char()
    referencia_2 = fields.Char()
    referencia_3 = fields.Char()
    referencia_4 = fields.Char()
    banco = fields.Selection([("banorte", "Banorte")])

    def name_get(self):
        res = []
        for rec in self:
            id = rec.id
            cadena = f"[ {rec.num_facturador} ] {rec.nombre_facturador}"
            tupla = (id, cadena)
            res.append(tupla)

        return res
