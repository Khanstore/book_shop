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

def cleanup_old_data(cr, registry):
    cr.execute("""
        delete  FROM public.mail_followers_mail_message_subtype_rel where mail_followers_id not in (select id from mail_followers);

        delete  FROM public.account_move_send_wizard_res_partner_rel where account_move_send_wizard_id not in (select id from account_move_send_wizard);
        
        delete  FROM public.account_payment_register_move_line_rel where wizard_id not in (select id from public.account_payment_register);
        
        delete  FROM public.documents_access where document_id not in (select id from documents_document);
        
        delete  FROM public.website_track where visitor_id not in (select id from website_visitor);
        
        delete  FROM public.discuss_channel where livechat_visitor_id not in (select id from website_visitor );
        
        
        delete  FROM public.sale_advance_payment_inv_sale_order_rel;
        
        
        delete  FROM public.pos_preparation_display_orderline where preparation_display_order_id not in (select id from pos_preparation_display_order);
        
        
        

        """)