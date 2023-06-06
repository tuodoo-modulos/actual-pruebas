# -*- coding: utf-8 -*-
{
    'name': "Grupo Actual | Pago a proveedores",

    'summary': """
        Crea un wizard que permite generar un archivo de pago según el tipo deseado para la lista de pagos seleccionados.""",

    'description': """
    """,

    'author': "Rafael Ramirez",
    'website': "https://www.nutrulatech.com",

    'category': 'Uncategorized',
    'version': '1.0.0',

    'depends': ['account', 'account_accountant', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions.xml',
        'views/res_partner_bank_form.xml',
        'views/res_partner_form.xml',
        'wizard/actual_wizard_pagos_form.xml',
        'wizard/actual_wizard_altas_bajas_form.xml',
    ],
}
