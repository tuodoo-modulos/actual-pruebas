# -*- coding: utf-8 -*-

from odoo import models, fields, api

'''
Este modelo es solo para administrar los adjuntos
que estamos creando cada vez que se descarga una 
lista de pagos. 
'''
class ActualAdjuntosPagos(models.Model):
    _name = 'actual.adjuntos.pagos'

    adjunto_id = fields.Many2one(
        'adjunto',
        string='adjunto',
        )
