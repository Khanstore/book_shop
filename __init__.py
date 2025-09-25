# -*- coding: utf-8 -*-
###################################################################################
#
#    Eagle ERP  Ltd.
#    Copyright (C) 2021 Eagle ERP Ltd(<http://www.eagle_it_solutions.com>).
#    Author: SM Ashraf
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
from . import model
from . import controllers
from . import wizard
from . import todo_applet

from odoo import api, SUPERUSER_ID

def cleanup_old_data(cr, registry):
    cr.execute("""
        DELETE FROM public.mail_followers_mail_message_subtype_rel
        WHERE mail_followers_id NOT IN (SELECT id FROM mail_followers);

        DELETE FROM public.account_move_send_wizard_res_partner_rel
        WHERE account_move_send_wizard_id NOT IN (SELECT id FROM account_move_send_wizard);

        DELETE FROM public.account_payment_register_move_line_rel
        WHERE wizard_id NOT IN (SELECT id FROM public.account_payment_register);

        DELETE FROM public.documents_access
        WHERE document_id NOT IN (SELECT id FROM documents_document);

        DELETE FROM public.website_track
        WHERE visitor_id NOT IN (SELECT id FROM website_visitor);

        DELETE FROM public.discuss_channel
        WHERE livechat_visitor_id NOT IN (SELECT id FROM website_visitor);

        DELETE FROM public.sale_advance_payment_inv_sale_order_rel;

        DELETE FROM public.pos_preparation_display_orderline
        WHERE preparation_display_order_id NOT IN (SELECT id FROM pos_preparation_display_order);
    """)
    print("✅ Old data cleaned up successfully.")
