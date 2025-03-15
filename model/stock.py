# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def force_availability(self):
        pickings=self.pick_ids
        for picking in pickings:
            for move in picking.move_ids:
                move.quantity=move.product_uom_qty
                print(move.name)

            picking.button_validate()

        print(self.id)


class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        # TODO check picking without qty and force availability
        pickings_without_quantities = self.env['stock.picking']
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for picking in self:
            if all(float_is_zero(move.quantity, precision_digits=precision_digits) for move in
                   picking.move_ids.filtered(lambda m: m.state not in ('done', 'cancel'))):
                pickings_without_quantities |= picking

            if pickings_without_quantities:
                # If there are pickings without quantities, show confirmation wizard
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'picking.confirmation.wizard',
                    'view_mode': 'form',
                    'target': 'new',  # This makes it a pop-up
                    'name': 'Confirm Action',
                    'context': {
                        'default_picking_id': self.id,  # Example of passing data to the wizard
                    }
                }

        return super().button_validate()


class PickingConfirmationWizard(models.TransientModel):
    _name = 'picking.confirmation.wizard'
    _description = 'Picking Confirmation Wizard'
    picking_id=fields.Integer()
    confirmation = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Do you want to force availability?", default='yes')

    def action_confirm(self):
        # Proceed if the user clicked Yes
        picking=self.env['stock.picking'].search([('id','=',self.picking_id)])
        for move in picking.move_ids:
            move.quantity=move.product_uom_qty
            print (move)
        picking.button_validate()
        print("User clicked Yes")
        return True

    def action_cancel(self):
        # Do something if the user clicked No
        print("User clicked No")
        return False
