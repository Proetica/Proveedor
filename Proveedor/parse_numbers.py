#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sub


class parseNumbers():

    #Numbers definition
    def parse(self, ammount):
        symbol = self.get_symbol(ammount)
        number = ammount.replace(symbol,"")
        symbol = symbol.replace(" ","")
        number = self.get_number(number)
        return float(number)


    def get_number(self, number):
        number = number.replace(" ","")
        number = number.replace(",",".")
        number = (number)
        return number


    def get_symbol(self, ammount):
        pattern =  r'(\D*)\d*\.?\d*(\D*)'
        g = re.match(pattern,ammount).groups()
        return g[0] or g[1]


if __name__ == '__main__':
    parseNumbers().parse('EUR $ 507 226,03')
    parseNumbers().parse('US$ 24 640,00')