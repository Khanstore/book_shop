# -*- coding: utf-8 -*-

from odoo import models, fields, api


class myfunctions(models.Model):
    _name = 'myfunctions'
    _description = 'Custom My functions'

    def replace_digits_with_letters(self,numbers):
        # Predefined mapping of digits to letters
        digit_to_letter = {
            '1': 'K',
            '2': 'H',
            '3': 'A',
            '4': 'N',
            '5': 'S',
            '6': 'T',
            '7': 'O',
            '8': 'R',
            '9': 'E',
            '0': 'Z',
        }

        # Iterate over the 'name' field and replace digits
        transformed = ""
        for char in numbers:
            if char in digit_to_letter:
                transformed += digit_to_letter[char]
            else:
                transformed += char

        # Update the transformed_name field with the new string
        return transformed