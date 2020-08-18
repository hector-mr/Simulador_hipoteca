"""
CALCULOS RELATIVOS A HIPOTECAS



1. Calculo de la amortizacion mensual


La amortizacion mensual es la cantidad de dinero que el cliente le devuelve al banco cada mes,
restandola del capital que todavia le debe al iniciarse ese mismo mes

Amortizacion mensual = Cuota mensual - intereses mensuales



2. Calculo de la cuota mensual


Cuota mensual = Intereses mensuales / {1 - [1 + Tasa interes / (12 * 100)**(-Plazo)]}

Donde 'Plazo' es el plazo restante en meses



3. Calculo de los intereses mensuales


Intereses mensuales = Capital pendiente * Tasa interes  / (12 * 100)

El plazo restante no interviene en el calculo de los intereses mensuales.
Los intereses mensuales obtenidos representan el beneficio que gana el banco con ese prestamo
"""

import numpy as np
import pandas as pd


class CalculoHipotecas:

    def __init__(self):
        self.porcentaje_entrada = 20  # Dinero aportado por comprador previamente al prestamo hipotecario
        self.csv_separator = ','

    @staticmethod
    def intereses_mensuales(capital_pendiente, tasa_interes):
        """
        :param capital_pendiente: precio de la vivienda a pagar por el comprador exceptuando la entrada aportada
        :param tasa_interes: tasa de interes fijo del prestamo bancario
        :return: intereses mensuales a pagar por el comprador
        """

        return capital_pendiente * tasa_interes / (12. * 100.)

    @classmethod
    def cuota_mensual(cls, capital_pendiente, tasa_interes, plazo):
        """
        :param capital_pendiente: precio de la vivienda a pagar por el comprador exceptuando la entrada aportada
        :param tasa_interes: tasa de interes fijo del prestamo bancario
        :param plazo: tiempo de duracion del prestamo hipotecario (en meses)
        :return: intereses mensuales a pagar por el comprador
        """

        exponencial = (1. + tasa_interes / (12. * 100.)) ** (-plazo)

        return cls.intereses_mensuales(capital_pendiente, tasa_interes) / (1. - exponencial)

    @staticmethod
    def amortizacion(cuota_mensual, intereses_mensuales):
        """
        :param cuota_mensual: pago total mensual del comprador por el prestamo hipotecario
        :param cuota_mensual: pago de intereses mensual del comprador por el prestamo hipotecario
        :return: pago de capital mensual del comprador por el prestamo hipotecario
        """

        return cuota_mensual - intereses_mensuales

    @staticmethod
    def maximo_precio_piso_segun_sueldo(sueldo_neto_mensual, relacion_cuota_sueldo, porcentaje_entrada,
                                        tasa_interes, plazo):
        """
        :param sueldo_neto_mensual: sueldo neto mensual
        :param relacion_cuota_sueldo: maxima fraccion del sueldo neto mensual que puede suponer la cuota mensual
        :param porcentaje_entrada: porcentaje del valor total del inmueble que debe aportar el comprador
        :param tasa_interes: tasa de interes fijo del prestamo bancario
        :param plazo: tiempo de duracion del prestamo hipotecario (en meses)
        :return: Maximo importe total de la vivienda a adquirir a partir del sueldo
        """

        exponencial = (1. + tasa_interes / (12. * 100.)) ** (-plazo)
        factor = tasa_interes / (12. * 100.) * 1. / (1. - exponencial)
        cuota_mensual = sueldo_neto_mensual * relacion_cuota_sueldo  # = capital_pendiente * factor

        capital_pendiente = cuota_mensual / factor

        precio_piso = capital_pendiente / (1. - porcentaje_entrada / 100.)

        return precio_piso

    @classmethod
    def calculo_hipoteca(cls, precio_piso, porcentaje_entrada, tasa_interes, plazo):
        """
        :param precio_piso: precio total del inmueble
        :param porcentaje_entrada: porcentaje del valor total del inmueble que debe aportar el comprador
        :param tasa_interes: tasa de interes fijo del prestamo bancario
        :param plazo: tiempo de duracion del prestamo hipotecario (en meses)
        :return: pandas DataFrame con information mensual, de principio a fin del prestamo hipotecario, sobre
        1 - Amortizacion mensual
        2 - Capital pendiente
        3 - Cuota mensual
        4 - Intereses mensuales
        Este calculo es un proceso iterativo, ya que la cuota e intereses mensuales dependen del capital pendiente
        que, a su vez, se vera disminuido cada mes por la amortizacion mensual
        """
        # tiempo restante (meses)
        arr_plazo = np.arange(plazo, 0, -1)

        arr_capital_pendiente = np.zeros(len(arr_plazo))
        arr_intereses_mensuales = np.zeros(len(arr_plazo))
        arr_cuota_mensual = np.zeros(len(arr_plazo))
        arr_amortizacion_mensual = np.zeros(len(arr_plazo))

        # Como tal, se realiza una primera iteracion para luego efectuar los calculos en un bucle

        for t, tt in enumerate(arr_plazo):

            if t == 0:

                arr_capital_pendiente[0] = precio_piso * (1. - porcentaje_entrada / 100.)
                arr_intereses_mensuales[0] = cls.intereses_mensuales(arr_capital_pendiente[0], tasa_interes)
                arr_cuota_mensual[0] = cls.cuota_mensual(arr_capital_pendiente[0], tasa_interes, arr_plazo[0])
                arr_amortizacion_mensual[0] = cls.amortizacion(arr_cuota_mensual[0], arr_intereses_mensuales[0])

            else:

                arr_capital_pendiente[t] = arr_capital_pendiente[t - 1] - arr_amortizacion_mensual[t - 1]
                arr_intereses_mensuales[t] = cls.intereses_mensuales(arr_capital_pendiente[t], tasa_interes)
                arr_cuota_mensual[t] = arr_cuota_mensual[0]
                arr_amortizacion_mensual[t] = cls.amortizacion(arr_cuota_mensual[t], arr_intereses_mensuales[t])

        df_hipoteca = pd.DataFrame({'Capital_pendiente': arr_capital_pendiente,
                                    'Intereses_mensuales': arr_intereses_mensuales,
                                    'Cuota_mensual': arr_cuota_mensual,
                                    'Amortizacion_mensual': arr_amortizacion_mensual})

        df_hipoteca = df_hipoteca[['Capital_pendiente', 'Cuota_mensual',
                                   'Amortizacion_mensual', 'Intereses_mensuales']]

        return df_hipoteca

    @staticmethod
    def calculo_intereses_para_banco(df_hipoteca):
        """
        :param df_hipoteca: output from calculo_hipoteca(precio_piso, porcentaje_entrada, tasa_interes, plazo)
        :return: Montante total de intereses pagado al banco por prestamo hipotecario
        """
        return df_hipoteca['Intereses_mensuales'].sum()

    def main(self):
        """
        :return: Tabla informativa para distintos parametros (sueldo neto mensual, relacion cuota-sueldo, tipo de interes, plazo)
        """

        smin = 900.
        smax = 10000.
        sstep = 25.

        rmin = 0.28
        rmax = 0.35
        rstep = 0.01

        imin = 1.
        imax = 3.0
        istep = 0.1

        pmin = 20.
        pmax = 30.
        pstep = 1.0

        appended_data = []

        for sueldo_neto_mensual in np.arange(smin, smax + sstep, sstep):

            for relacion_cuota_sueldo in np.arange(rmin, rmax, rstep):

                for tasa_interes in np.arange(imin, imax + istep, istep):

                    for plazo in np.arange(pmin, pmax + pstep, pstep):
                        precio = self.maximo_precio_piso_segun_sueldo(sueldo_neto_mensual=sueldo_neto_mensual,
                                                                      relacion_cuota_sueldo=relacion_cuota_sueldo,
                                                                      porcentaje_entrada=self.porcentaje_entrada,
                                                                      tasa_interes=tasa_interes,
                                                                      plazo=plazo * 12)

                        df_hip = self.calculo_hipoteca(precio_piso=precio,
                                                       porcentaje_entrada=self.porcentaje_entrada,
                                                       tasa_interes=tasa_interes,
                                                       plazo=plazo * 12)

                        cuota = df_hip['Cuota_mensual'][0]

                        interes_total = self.calculo_intereses_para_banco(df_hip)

                        df_temp = pd.DataFrame({'Sueldo_neto_mensual': sueldo_neto_mensual,
                                                'Relacion_cuota_sueldo': relacion_cuota_sueldo,
                                                'Tasa_interes': tasa_interes,
                                                'Plazo': plazo,
                                                'Precio_piso': precio,
                                                'Cuota_mensual': cuota,
                                                'Interes_total': interes_total}, index=[0])

                        appended_data.append(df_temp)
                        del df_temp

        df_resumen = pd.concat(appended_data).reset_index(drop=True)
        df_resumen = df_resumen[['Sueldo_neto_mensual', 'Relacion_cuota_sueldo', 'Tasa_interes', 'Plazo',
                                 'Precio_piso', 'Cuota_mensual', 'Interes_total']]

        # Guarda tabla final en formato csv
        df_resumen.to_csv('Resumen_pago_hipotecas.csv', sep=self.csv_separator, index=False)

        return


if __name__ == '__main__':
    ch = CalculoHipotecas()
    ch.main()
