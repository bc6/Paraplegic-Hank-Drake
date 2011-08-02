from axiom import Float

class FloatUnit(Float):
    unitAbbr = ''

    def ToString(self, value):
        return '%.{0}f({1})'.format(self.precision, self.unitAbbr) % value



    def ConvertFrom(self, srcUnit, value):
        if isinstance(self, type(srcUnit)):
            return value



    def ConvertTo(self, destUnit, value):
        return None



    @staticmethod
    def Convert(destUnit, srcUnit, srcValue):
        rv = srcUnit.ConvertTo(destUnit, srcValue)
        if rv is None:
            rv = destUnit.ConvertFrom(srcUnit, srcValue)
        if rv is None:
            raise ValueError('Cannot convert {0} from {1} to {2}'.format(srcValue, srcUnit, destUnit))
        return rv




class Meter(FloatUnit):
    unitAbbr = 'm'


class Second(FloatUnit):
    unitAbbr = 's'


class Kilogram(FloatUnit):
    unitAbbr = 'kg'


class Radian(FloatUnit):
    unitAbbr = 'rad'


