from datetime import date, datetime
from odoo import models, fields

class DailyAdminReport(models.Model):
    _inherit = "res.users"

    def _send_daily_admin_report(self):
        today = fields.Date.today()
        # Example: sales
        sales = self.env['sale.order'].search([('date_order', '>=', today)])
        total_sales = sum(sales.mapped('amount_total'))

        # Example: POS
        pos_orders = self.env['pos.order'].search([('date_order', '>=', today)])
        total_pos = sum(pos_orders.mapped('amount_total'))

        # Example: payments
        payments = self.env['account.payment'].search([('payment_date', '=', today)])
        total_payments = sum(payments.mapped('amount'))

        # Build email body
        body = f"""
        <h3>Daily Admin Report ({today})</h3>
        <p><b>Total Sales:</b> {total_sales}</p>
        <p><b>Total POS:</b> {total_pos}</p>
        <p><b>Total Payments:</b> {total_payments}</p>
        """

        # Send mail to admin
        self.env['mail.mail'].create({
            'subject': f'Daily Admin Report - {today}',
            'body_html': body,
            'email_to': 'admin@example.com'
        }).send()