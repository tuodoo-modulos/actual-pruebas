# -*- coding: utf-8 -*-

from odoo import models, _
from dateutil.relativedelta import relativedelta
from calendar import monthrange

import logging

_logger = logging.getLogger("[ EMPLOYEE LOAN OVERRIDE]")


class employee_loan(models.Model):
    _inherit = "employee.loan"

    def compute_installment(self):
        vals = []
        fecha_anterior_quincenal = self.start_date
        for i in range(0, self.term):
            date = self.start_date  # datetime.strptime(self.start_date, '%Y-%m-%d')

            periodo_de_pago = self.loan_type_id.periodo_de_pago or ""
            if periodo_de_pago == "Semanal":
                date = date + relativedelta(weeks=i)
            elif periodo_de_pago == "Quincenal":
                date = self.fecha_calculada_para_quincena(indice=i, fecha=fecha_anterior_quincenal)
                fecha_anterior_quincenal = date
            else:
                date = date + relativedelta(months=i)

            amount = self.loan_amount
            interest_amount = 0.0
            ins_interest_amount = 0.0
            if self.is_apply_interest:
                amount = self.loan_amount
                interest_amount = (amount * self.interest_rate) / 100  # * self.term/12

                if (
                    self.interest_rate
                    and self.loan_amount
                    and self.interest_type == "reduce"
                ):
                    amount = self.loan_amount - self.installment_amount * i
                    interest_amount = (
                        amount * self.term * self.interest_rate
                    ) / 100  # / 12
                ins_interest_amount = interest_amount / self.term
            vals.append(
                (
                    0,
                    0,
                    {
                        #'name':'INS - '+self.name+ ' - '+str(i+1),
                        # 'name': self.name+ ' - '+str(i+1),
                        "name": " TEST " + str(i),
                        "employee_id": self.employee_id
                        and self.employee_id.id
                        or False,
                        "date": date,
                        "amount": amount,
                        "interest": interest_amount,
                        "installment_amt": self.installment_amount,
                        "ins_interest": ins_interest_amount,
                        "tipo_deduccion": self.loan_type_id.tipo_deduccion,
                    },
                )
            )

        if self.installment_lines:
            for l in self.installment_lines:
                l.unlink()
        self.installment_lines = vals

    def fecha_calculada_para_quincena(self, indice, fecha):
        # La primera fecha pasa igual
        # Calculo del primer pago quincenal.
        # Si dia <= 15, entonces **ultimo dia** de este mes.
        # Si dia > 15, entonces día 15 **siguiente mes**.
        # Esto tiene que ser así para que no se generen
        # dos pagos en una misma quincena.
        es_ultimo_dia = True if fecha.day <= 15 else False

        if es_ultimo_dia:
            primer_dia_laborable_semana, ultimo_dia_del_mes = monthrange(
                fecha.year, fecha.month
            )
            fecha = fecha.replace(day=ultimo_dia_del_mes)
        else:
            mes_actual = fecha.month
            anio_actual = fecha.year
            if mes_actual == 12:
                mes_actual = 1
                anio_actual += 1
            else:
                mes_actual += 1

            fecha = fecha.replace(day=15, month=mes_actual, year=anio_actual)

        return fecha
        
        