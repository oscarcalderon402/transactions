from odoo import fields, models, api


class DateWizard(models.Model):
    _name = 'date.wizard'
    _description = 'DateWizard'

    start_date = fields.Date(string='startDate')
    end_date = fields.Date(string='endDate')

    # def search_transactions(self):
    #     print("done")




