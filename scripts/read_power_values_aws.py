import sys
import time

sys.path.append(r'C:\\OPAL-RT\\HYPERSIM\\hypersim_2024.1.4.o62\\Windows\\HyApi\\python')
import HyWorksApiGRPC as HyWorksApi
HyWorksApi.startAndConnectHypersim()

sensors = [
    "v_calama.y", "v_salar.y", "v_chuquicamata.y", "frequency.y",
    "sl1.Pmean", "sl1.Qmean", "sl2.Pmean", "sl2.Qmean",
    "sl3.Pmean", "sl3.Qmean", "sl4.Pmean", "sl4.Qmean",
    "sl5.Pmean", "sl5.Qmean", "sl6.Pmean", "sl6.Qmean",
    "sg1.Pmean", "sg1.Qmean", "sg2.Pmean", "sg2.Qmean",
    "sg3.Pmean", "sg3.Qmean", "sg4.Pmean", "sg4.Qmean",
    "sg5.Pmean", "sg5.Qmean", "sg6.Pmean", "sg6.Qmean",
    "sg7.Pmean", "sg7.Qmean", "sg8.Pmean", "sg8.Qmean"
]

try:
    while True:
        values = HyWorksApi.getLastSensorValues(sensors)
        for sensor, value in zip(sensors, values):
            print(f"{sensor}: {value}")
        print("-" * 30)
        time.sleep(5)

except KeyboardInterrupt:
    print("\nInterrupted by user")

except Exception as e:
    print(f"error {e}")
