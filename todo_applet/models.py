from odoo import models, fields

class DevTodo(models.Model):
    _name = "dev.todo"
    _description = "Developer To-Do Checklist"

    name = fields.Char("Task")
    is_done = fields.Boolean("Done", default=False)
    app_name= fields.Char("App Name")
    note = fields.Text("Notes")
    sequence = fields.Integer("Order", default=10)
