#!/usr/bin/python3.6
import pint, random

ureg = pint.UnitRegistry()

Hd = [
    1.39, 2.52, 4.06, 4.94, 5.16, 5.47, 5.61, 5.18, 4.36, 2.81, 1.63, 1.14
] * ureg.kWh / (
    ureg.meter * ureg.meter
) / ureg.day

Ed = [
    1.18, 2.16, 3.35, 3.96, 4.04, 4.20, 4.28, 3.99, 3.43, 2.29, 1.36, 0.95
] * ureg.kWh / ureg.kW

area = 6109.29 * ureg.meter ** 2
print(f"area: {area:.2f}")

peak = 1009.8 * ureg.kilowatt
print(f"peak: {peak:.2f}")

some_gs = round(450 * random.random(), 2) * ureg.watt / ureg.meter ** 2
print(f"some_gs: {some_gs:.2f}")

print()

for i, month in enumerate("Jan Feb Mrz Apr Mai Jun Jul Aug Sep Okt Nov Dez".split()):
    print(f"{month}:")
    print(f"Hd = {Hd[i]:.2f}")
    print(f"Hd = {Ed[i]:.2f}")

    # fake integrate (sun for 12h / day)
    daily_gs = (some_gs * (12 * 3600 * ureg.second) / ureg.day).to(
        ureg.kWh / ureg.meter ** 2 / ureg.day
    )
    print(f"daily_gs: {daily_gs:.2f}")

    f = daily_gs / Hd[i]
    print(f"f: {f:.2f}")

    x = f * Ed[i]
    print(f"x: {x:.2f}")

    total_expected = peak * x
    print(f"total_expected: {total_expected:.2f}")

    print()
