from platform import system
from tempfile import gettempdir
from pathlib import Path
import pytest
from mingo import Database
from typing import Union, Iterable

# DATA FOR MOCK SOURCE FILES

MOCK_SOURCE_DATA = {
    "10-16-800": """HEADER
    CASE
        Particle []: gamma (0), electron (1), muon (2), neutron (3), proton (4)
        Number of events []:
        Emin [MeV]:
        Emax [MeV]:
        E distribution: constant (0), gaussian (1), exponential (2)
        Theta min [deg]:
        Theta max [deg]:
        Detector plane - X dimension [mm]:
        Detector plane - Y dimension [mm]:
        Detector plane - Z dimension [mm]:
    ACTIVE PLANES
        Plane 1 - Z coordinate [mm]: 0 by definition
        Plane 2 - Z coordinate [mm]:
        Plane 3 - Z coordinate [mm]:
        Plane 4 - Z coordinate [mm]:
    PASSIVE PLANES
        Plane 1 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 2 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 3 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 4 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 1 - Thickness [mm]:
        Plane 2 - Thickness [mm]:
        Plane 3 - Thickness [mm]:
        Plane 4 - Thickness [mm]:
        Plane 1 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 2 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 3 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 4 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
   EVENT
        Event number []:
        Initial energy [MeV]:
        Initial X [mm]: Measured from center of plane, positive to the right
        Initial Y [mm]: Measured from center of plane, right handed frame
        Initial Z [mm]: 0 by definition
        Initial theta [deg]:
        Initial phi [deg]:
        Number of hits []:
    HIT
        Plane number []: First is 1, last is 4
        X [mm]: Measured from center of plane, positive to the right
        Y [mm]: Measured from center of plane, right handed frame
        Z [mm]: Measured downwards from first active plane
        Time since first impact [ns]:
DATA
1	10000	800	800	0	0	0	999	999	22
0	100	200	400
null	22	null	222	null	10.4	null	16.2	null	0	null	0
1	800 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	24
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	-7.1720e-01	-9.3980e+00	+1.0000e+02	0.3692
3	-1.4780e+01	-2.6620e+01	+2.0000e+02	0.7113
4	-1.2210e+02	+4.6550e+01	+4.2020e+02	1.589
3	+4.7820e+01	-1.0860e+01	+2.1690e+02	0.901
4	-1.0070e+02	-1.8650e+02	+4.1950e+02	1.767
4	-4.4300e+01	-3.2290e+02	+4.0000e+02	2.005
2	-9.6860e+00	-2.4830e+00	+1.0000e+02	0.3695
3	-3.2410e+01	+3.2500e+01	+2.0000e+02	0.7339
3	+4.5560e-04	+2.2880e+01	+2.0050e+02	0.8806
2	-9.7830e-01	-7.4000e+00	+1.0000e+02	0.3683
3	-9.5770e+00	-2.4900e+01	+2.0000e+02	0.7084
3	-9.6640e+00	-2.5090e+01	+2.0110e+02	0.712
2	-1.4960e+00	+5.5360e-01	+1.0000e+02	0.367
3	+8.8750e-01	+6.6350e+00	+2.0000e+02	0.7014
3	-4.3560e+00	+1.7380e+00	+2.2110e+02	0.7711
3	-4.3560e+00	+1.7380e+00	+2.2110e+02	0.7711
3	-4.3560e+00	+1.7380e+00	+2.2110e+02	0.7711
4	+1.0280e+02	-1.5490e+02	+4.0000e+02	1.65
2	+2.0670e+02	-3.3640e+01	+1.1230e+02	1.626
3	+1.3520e+02	-1.1920e+01	+2.0930e+02	1.218
3	+2.5920e-03	+2.3510e+00	+2.0640e+02	0.7218
2	+6.8310e+01	-2.1560e+01	+1.0000e+02	0.4779
2	+2.3830e+01	+3.9500e+00	+1.0000e+02	0.3809
2	800 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	38
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	+6.9420e+00	-2.2770e+00	+1.0000e+02	0.3682
3	+2.1310e+01	-5.3180e+00	+2.0000e+02	0.7054
3	+1.0440e+01	+1.4500e+01	+2.0790e+02	0.893
3	+2.2920e+01	-9.4650e+00	+2.1570e+02	0.7584
3	+2.2920e+01	-9.4650e+00	+2.1570e+02	0.7584
3	+2.8320e+01	-1.3840e+01	+2.2150e+02	0.8006
3	+2.2920e+01	-9.4650e+00	+2.1570e+02	0.7584
2	+9.2610e+00	-3.1390e+01	+1.2070e+02	0.5091
2	+8.8950e+00	-3.2290e+01	+1.1950e+02	0.504
2	+9.5200e+00	-3.0300e+01	+1.1270e+02	0.4803
2	+6.3880e+00	-1.5970e+00	+1.0330e+02	0.3791
2	-4.0130e+01	-3.0030e+01	+1.0000e+02	0.423
2	-1.7660e+01	-4.7070e+01	+1.2130e+02	0.587
2	-4.8440e+01	-2.9860e+01	+1.0700e+02	0.4709
2	+5.7860e+00	+1.3100e-01	+1.0000e+02	0.3679
2	-4.2490e+01	-1.4420e+01	+1.0000e+02	0.4269
2	-1.4220e+01	-9.1660e+01	+1.0520e+02	0.833
2	-1.9940e+01	-8.7340e+01	+1.1210e+02	0.7998
2	-2.2960e+01	-8.7980e+01	+1.1280e+02	0.7892
2	-3.5280e+01	-7.1160e+01	+1.0100e+02	0.7092
2	-3.2920e+01	-4.6990e+01	+1.0900e+02	0.624
3	-4.7890e+01	-1.7260e+02	+2.2150e+02	1.372
3	-8.7880e+01	-1.5810e+02	+2.2150e+02	1.23
3	-9.0020e+01	-1.6770e+02	+2.1250e+02	1.186
3	-9.2080e+01	-1.6930e+02	+2.0830e+02	1.169
2	-7.0830e+01	-2.4670e+01	+1.2080e+02	0.601
2	-5.8060e+01	-4.8610e+00	+1.1090e+02	0.5157
4	+5.3510e+01	-8.3240e+01	+4.0000e+02	1.459
4	+4.3920e+00	-1.6240e+02	+4.0110e+02	1.819
4	+5.3940e+00	-1.6170e+02	+4.0070e+02	1.815
4	+7.1870e+01	-1.0990e+02	+4.1580e+02	1.806
4	+7.3030e+01	-1.1220e+02	+4.1720e+02	1.796
4	+7.2910e+01	-8.1790e+01	+4.1940e+02	1.694
4	+6.2840e+01	-1.3610e+02	+4.0000e+02	1.563
4	-7.0400e+01	-1.0340e+01	+4.0000e+02	1.42
4	-8.0030e+01	-1.6100e+01	+4.1770e+02	1.494
4	-7.7640e+01	-1.5080e+01	+4.1270e+02	1.475
3	800 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	50
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	+2.6060e+01	-8.7860e+01	+1.0000e+02	0.5195
4	-1.5150e+02	+2.2290e+02	+4.0120e+02	1.865
4	-7.0100e+01	-3.7740e+01	+4.0000e+02	1.408
4	+9.9200e+00	-1.7710e+01	+4.0000e+02	1.381
2	+4.8260e-01	-2.2970e+01	+1.0000e+02	0.3788
3	-1.2300e+01	-4.3880e+01	+2.0000e+02	0.7227
3	+8.6540e+00	-2.6940e+01	+2.0760e+02	0.733
3	+8.6540e+00	-2.6940e+01	+2.0760e+02	0.733
3	+1.5390e+01	-6.7760e+00	+2.0600e+02	0.8454
3	+1.7410e+01	-8.6070e+00	+2.0630e+02	0.8363
3	+1.1930e+01	-5.1690e+01	+2.0880e+02	1.088
3	+1.3540e+01	-5.5210e+01	+2.0450e+02	1.069
3	+4.9550e+00	-5.5870e+01	+2.0890e+02	1.037
3	-1.8060e+01	-7.6430e+01	+2.1580e+02	0.9311
3	+8.6540e+00	-2.6940e+01	+2.0760e+02	0.733
2	-4.3850e+00	-8.4960e-02	+1.0000e+02	0.3673
3	-3.0490e+00	-2.0880e+01	+2.0000e+02	0.7101
3	+7.7500e+00	-1.3190e+01	+2.2200e+02	0.8084
3	-8.4520e+01	-3.3290e+00	+2.1350e+02	1.179
3	-7.1550e+01	-2.7690e+01	+2.1880e+02	1.085
3	-1.1040e+01	-9.7390e-01	+2.1490e+02	0.7511
3	-1.1040e+01	-9.7390e-01	+2.1490e+02	0.7511
4	-9.1550e+01	+1.7010e+02	+4.0000e+02	1.666
4	-7.3990e+01	+2.5130e+02	+4.1990e+02	1.968
4	-7.7650e+01	+2.0550e+02	+4.1440e+02	1.814
4	-7.8540e+01	+2.0160e+02	+4.1440e+02	1.801
4	-9.1680e+01	+1.7720e+02	+4.0450e+02	1.703
3	-1.1040e+01	-9.7390e-01	+2.1490e+02	0.7511
3	-9.1200e+00	+8.9000e-01	+2.0180e+02	0.7074
3	-9.1200e+00	+8.9000e-01	+2.0180e+02	0.7074
3	-9.1200e+00	+8.9000e-01	+2.0180e+02	0.7074
2	-4.0350e+01	+4.5440e+01	+1.0390e+02	1.273
2	-3.8430e+01	+4.9330e+01	+1.0830e+02	1.253
3	-5.0100e+00	-7.6050e+00	+2.2070e+02	0.818
2	-5.2440e+01	+9.2870e+01	+1.0720e+02	1.308
3	-1.4850e+01	+4.7460e+00	+2.1880e+02	0.8174
2	-9.9320e+00	+3.1530e+00	+1.0000e+02	0.3695
3	-2.1440e+01	+3.4360e+00	+2.0000e+02	0.7053
2	-4.9200e+00	-1.4620e+00	+1.0230e+02	0.3752
2	-4.9200e+00	-1.4620e+00	+1.0230e+02	0.3752
2	-1.4270e+02	-4.3520e+02	+1.1880e+02	2.128
2	-1.4010e+02	-4.3380e+02	+1.1870e+02	2.118
2	-1.4010e+02	-4.3430e+02	+1.1610e+02	2.109
2	-1.3940e+02	-4.3540e+02	+1.1260e+02	2.097
2	-1.4050e+02	-4.3710e+02	+1.0570e+02	2.073
3	-1.1210e+02	-3.1120e+02	+2.0400e+02	1.532
3	-1.0830e+02	-3.0390e+02	+2.0250e+02	1.504
2	-4.9200e+00	-1.4620e+00	+1.0230e+02	0.3752
3	-1.4220e+01	-1.7280e+00	+2.1450e+02	0.7507
4	800 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	13
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
4	+1.0650e+01	+6.4170e+00	+4.1180e+02	1.407
4	+1.0650e+01	+6.4170e+00	+4.1180e+02	1.407
4	+1.0650e+01	+6.4170e+00	+4.1180e+02	1.407
2	-3.5740e+01	+1.5310e+01	+1.0000e+02	0.401
3	-7.0020e+01	+8.9170e+01	+2.0000e+02	0.8369
3	-7.8910e+01	+1.0300e+02	+2.2200e+02	0.9361
2	-5.2920e+01	+1.6130e+02	+1.0200e+02	1.416
4	-1.5740e+01	+3.6220e+02	+4.2110e+02	2.248
4	+4.6710e+01	+3.5070e+02	+4.0190e+02	2.027
2	+3.7680e-01	+1.4830e+01	+1.0000e+02	0.3914
2	-2.0470e+01	-6.4170e+00	+1.0000e+02	0.3793
3	-6.1500e+01	+9.4380e+00	+2.0000e+02	0.7458
""",
    "10-16-1000": """HEADER
    CASE
        Particle []: gamma (0), electron (1), muon (2), neutron (3), proton (4)
        Number of events []:
        Emin [MeV]:
        Emax [MeV]:
        E distribution: constant (0), gaussian (1), exponential (2)
        Theta min [deg]:
        Theta max [deg]:
        Detector plane - X dimension [mm]:
        Detector plane - Y dimension [mm]:
        Detector plane - Z dimension [mm]:
    ACTIVE PLANES
        Plane 1 - Z coordinate [mm]: 0 by definition
        Plane 2 - Z coordinate [mm]:
        Plane 3 - Z coordinate [mm]:
        Plane 4 - Z coordinate [mm]:
    PASSIVE PLANES
        Plane 1 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 2 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 3 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 4 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 1 - Thickness [mm]:
        Plane 2 - Thickness [mm]:
        Plane 3 - Thickness [mm]:
        Plane 4 - Thickness [mm]:
        Plane 1 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 2 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 3 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 4 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
   EVENT
        Event number []:
        Initial energy [MeV]:
        Initial X [mm]: Measured from center of plane, positive to the right
        Initial Y [mm]: Measured from center of plane, right handed frame
        Initial Z [mm]: 0 by definition
        Initial theta [deg]:
        Initial phi [deg]:
        Number of hits []:
    HIT
        Plane number []: First is 1, last is 4
        X [mm]: Measured from center of plane, positive to the right
        Y [mm]: Measured from center of plane, right handed frame
        Z [mm]: Measured downwards from first active plane
        Time since first impact [ns]:
DATA
1	10000	1000	1000	0	0	0	999	999	22
0	100	200	400
null	22	null	222	null	10.4	null	16.2	null	0	null	0
1	1000 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	42
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	+1.0910e+00	+9.1170e+00	+1.0000e+02	0.3689
3	+5.6440e+00	+2.1040e+01	+2.0000e+02	0.7052
2	-3.6360e+02	+5.0830e+01	+1.0110e+02	2.101
2	-3.3350e+02	+4.9610e+01	+1.0850e+02	1.997
3	+1.9630e+01	+2.4740e+01	+2.0170e+02	1.002
3	+2.8520e+01	+1.4600e+01	+2.1500e+02	0.9386
4	-1.7470e+02	+1.0140e+02	+4.1640e+02	1.753
4	-1.7320e+02	+1.0040e+02	+4.1350e+02	1.742
4	-1.6820e+02	+1.0260e+02	+4.1480e+02	1.723
4	-1.6550e+02	+1.0500e+02	+4.1810e+02	1.707
2	-1.0080e+00	+4.8030e+00	+1.0000e+02	0.3675
3	-6.3500e+00	+1.0190e+01	+2.0000e+02	0.7028
2	-2.4800e+00	+3.9320e+00	+1.0000e+02	0.3674
3	-1.1830e+01	+2.1280e+00	+2.0000e+02	0.7028
4	-2.1020e+02	+6.7420e+01	+4.1270e+02	1.722
2	+4.3220e-01	+1.2800e+00	+1.0000e+02	0.367
3	+2.0620e+00	+3.8110e+00	+2.0000e+02	0.7007
4	+1.8940e+01	-2.0780e+01	+4.0750e+02	1.401
4	+1.8940e+01	-2.0780e+01	+4.0750e+02	1.401
4	+1.8940e+01	-2.0780e+01	+4.0750e+02	1.401
4	+1.3260e+01	+1.0330e+01	+4.0000e+02	1.37
4	-1.6880e+02	-2.3070e+01	+4.1350e+02	1.649
4	-1.6580e+02	-2.5090e+01	+4.1060e+02	1.634
4	+1.3310e+02	+1.2680e+02	+4.0000e+02	1.633
4	+1.2490e+02	+1.3780e+02	+4.0840e+02	1.727
4	+1.3300e+02	+1.2910e+02	+4.1190e+02	1.685
4	+2.8980e+02	+8.0850e+01	+4.0000e+02	1.962
4	+7.0940e+01	-3.4960e+01	+4.0000e+02	1.429
2	+3.9540e+00	+5.3030e-02	+1.0000e+02	0.3673
3	+1.1970e+01	+2.9220e+00	+2.0000e+02	0.7021
4	-1.3080e+01	+2.4540e+01	+4.0090e+02	1.479
4	-2.6070e+01	+3.1530e+01	+4.0120e+02	1.43
4	-2.7640e+01	+3.2530e+01	+4.0660e+02	1.411
2	+1.2910e+01	-2.0620e+01	+1.0150e+02	1.294
2	-2.4300e+01	+1.6270e+01	+1.0000e+02	0.3868
3	-5.2480e+01	+5.6930e+01	+2.0430e+02	0.772
3	-5.2480e+01	+5.6930e+01	+2.0430e+02	0.772
3	-1.6380e+02	+6.7020e+01	+2.0890e+02	1.854
2	-3.5670e+01	+9.8330e+01	+1.0060e+02	1.285
3	-5.0380e+01	+5.6040e+01	+2.1290e+02	0.8269
3	-5.2480e+01	+5.6930e+01	+2.0430e+02	0.772
2	1000 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	32
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	+6.3050e+00	-3.0460e+00	+1.0000e+02	0.3684
3	+3.0690e+01	+1.3680e+01	+2.0000e+02	0.7171
2	+1.5090e+02	+2.9160e+01	+1.0540e+02	1.359
2	+5.8400e-02	+8.1350e+00	+1.0000e+02	0.3684
3	-2.3010e+01	+5.5630e+01	+2.0000e+02	0.7496
3	-5.8560e+00	+1.8710e+01	+2.2000e+02	0.7704
3	-5.8560e+00	+1.8710e+01	+2.2000e+02	0.7704
4	+7.1480e+00	-3.6110e+01	+4.0710e+02	1.429
2	+9.0660e+01	-5.2230e+01	+1.2150e+02	1.379
3	-1.2310e+01	+2.8210e+01	+2.0070e+02	0.8693
3	-6.8210e+00	+2.3440e+01	+2.0720e+02	0.8369
3	-5.8560e+00	+1.8710e+01	+2.2000e+02	0.7704
2	+4.1150e+01	-8.0780e+01	+1.0000e+02	0.5243
2	-1.2980e+02	-7.9060e+00	+1.0000e+02	1.401
3	-3.4470e+02	+6.1790e+01	+2.0720e+02	2.712
2	-2.9530e-01	+1.6050e+01	+1.0000e+02	0.3731
2	-3.9680e+02	+1.1440e+02	+1.0900e+02	1.543
2	-3.9680e+02	+1.1490e+02	+1.0880e+02	1.541
2	+6.5580e+00	-8.0610e+00	+1.0000e+02	0.3699
4	+1.7820e+01	+1.6950e+01	+4.0440e+02	1.388
4	+1.7820e+01	+1.6950e+01	+4.0440e+02	1.388
4	+9.3910e+00	+1.8590e+01	+4.2160e+02	1.487
4	+2.3390e+01	+8.5530e+00	+4.2140e+02	1.636
4	+3.0020e+01	-1.0360e+01	+4.0110e+02	1.541
4	+3.0800e+01	-1.0140e+01	+4.0030e+02	1.537
4	+1.7820e+01	+1.6950e+01	+4.0440e+02	1.388
4	-1.0160e+00	+9.8060e-01	+4.0780e+02	1.394
4	-1.0160e+00	+9.8060e-01	+4.0780e+02	1.394
4	-1.0160e+00	+9.8060e-01	+4.0780e+02	1.394
4	-9.0350e+00	-4.6840e+00	+4.0000e+02	1.369
4	-3.9840e+00	-5.1290e+00	+4.0000e+02	1.368
3	1000 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	70
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	+1.1450e+01	-1.9930e+01	+1.0000e+02	0.3802
2	+1.1130e+02	+1.3810e+02	+1.0330e+02	1.454
2	+1.1160e+02	+1.3980e+02	+1.0370e+02	1.448
2	+1.1090e+02	+1.3910e+02	+1.0410e+02	1.444
3	+4.3950e+01	+1.1340e+02	+2.1280e+02	1.01
2	-3.8280e+00	-5.0620e+00	+1.0000e+02	0.3679
3	-1.5430e+01	-1.8800e+01	+2.0000e+02	0.7069
2	-4.7070e+00	-6.1090e+00	+1.0980e+02	0.4008
2	-4.7070e+00	-6.1090e+00	+1.0980e+02	0.4008
3	-1.0620e+02	-3.9960e+01	+2.0000e+02	0.8918
2	+4.1950e+02	-7.8980e+01	+1.1860e+02	2.702
2	-4.7070e+00	-6.1090e+00	+1.0980e+02	0.4008
3	-5.3460e+00	-9.4550e+00	+2.1660e+02	0.7568
2	-1.6060e+01	-1.1330e+01	+1.0000e+02	0.3763
2	-1.0210e+01	-9.2520e+00	+1.1240e+02	0.4485
3	-4.3130e+02	+2.0210e+02	+2.0070e+02	2.152
2	-1.6890e+01	-3.0050e+01	+1.2000e+02	0.5455
2	-2.1030e+01	-1.4050e+01	+1.1660e+02	0.4892
2	-2.0490e+01	-1.2360e+01	+1.1680e+02	0.4832
2	-9.9280e+00	-1.5360e+01	+1.0000e+02	0.3773
3	-7.8910e+00	-9.3440e+00	+2.1850e+02	0.7635
3	-7.8910e+00	-9.3440e+00	+2.1850e+02	0.7635
3	-7.8910e+00	-9.3440e+00	+2.1850e+02	0.7635
2	-3.5700e+01	+9.8600e+01	+1.0000e+02	0.5567
2	-2.7830e+01	+1.1230e+02	+1.0140e+02	0.6788
3	-7.1760e+01	+2.0080e+02	+2.1620e+02	1.465
3	-7.3930e+01	+2.0150e+02	+2.1780e+02	1.456
3	-8.7760e+01	+2.0140e+02	+2.1570e+02	1.409
3	-8.8050e+01	+1.9570e+02	+2.1770e+02	1.389
3	-7.2850e+01	+1.6850e+02	+2.0730e+02	1.279
3	-1.0120e+02	+1.3240e+02	+2.0750e+02	1.126
3	-9.2770e+01	+1.2270e+02	+2.0440e+02	1.082
2	-3.9530e+01	-1.9430e+01	+1.1920e+02	0.5017
2	+1.4860e+01	+3.3990e+00	+1.0000e+02	0.3726
3	+2.7880e+01	+8.4520e+00	+2.0000e+02	0.7096
2	+1.8010e+00	+1.2440e+01	+1.0000e+02	0.3706
3	-2.0030e+00	+1.6540e+01	+2.0000e+02	0.7048
2	+1.0750e+00	+8.2240e+00	+1.0000e+02	0.3686
3	+6.5540e+00	-9.2220e+01	+2.0000e+02	0.8623
2	-7.2790e+01	-2.1320e+02	+1.0500e+02	1.865
2	+2.2680e+00	-2.5340e+02	+1.1070e+02	1.58
2	+1.1110e+01	-2.5140e+02	+1.1310e+02	1.549
2	+5.9040e+01	-6.8710e+01	+1.0000e+02	0.518
2	-3.3170e+01	-5.6570e+00	+1.0000e+02	0.393
3	-1.0070e+02	-3.3050e+01	+2.0000e+02	0.8068
2	-5.4530e+00	+7.3940e+00	+1.1820e+02	0.4291
2	-5.4530e+00	+7.3940e+00	+1.1820e+02	0.4291
3	-7.4960e+00	+2.3710e+01	+2.0000e+02	0.7077
3	-1.1860e+01	+3.4790e+01	+2.2200e+02	0.7959
3	-1.0680e+02	+2.5530e+01	+2.1240e+02	1.201
3	-1.0670e+02	+2.4290e+01	+2.1240e+02	1.197
3	-7.5040e+01	+5.2070e+01	+2.1080e+02	1.056
3	-4.7770e+01	+3.3900e+01	+2.1380e+02	0.9235
3	-4.1130e+01	+3.3400e+01	+2.1430e+02	0.9012
2	+1.3920e+02	+5.7980e+01	+1.1450e+02	1.508
3	+7.1040e+00	+5.1870e+01	+2.0710e+02	0.9699
3	-1.2760e+01	+4.0060e+01	+2.0110e+02	0.8902
2	-5.4530e+00	+7.3940e+00	+1.1820e+02	0.4291
4	-2.9010e+02	-1.3280e+02	+4.0620e+02	2.043
4	-4.8520e+01	+3.7230e+01	+4.1990e+02	1.616
4	-3.5570e+00	+6.3950e+00	+4.1600e+02	1.433
4	-3.3140e+00	+6.3200e+00	+4.1620e+02	1.432
4	-5.0520e+00	+6.1580e+00	+4.1720e+02	1.425
3	-2.7220e+01	+3.6530e+00	+2.1870e+02	0.8311
3	-2.3110e+00	+2.8950e+00	+2.1290e+02	0.7457
3	-2.7830e+00	+3.1410e+00	+2.1300e+02	0.7439
2	+1.6920e+02	-1.4590e+02	+1.0000e+02	0.919
2	+1.7010e+02	-1.4330e+02	+1.1030e+02	1.02
2	+1.6970e+02	-1.4450e+02	+1.1560e+02	1.002
4	1000 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	53
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
3	+7.2300e+00	+7.5620e+01	+2.1750e+02	1.104
3	-9.2560e+00	+6.9790e+01	+2.0170e+02	1.025
3	+2.8930e+01	+4.3250e+01	+2.2190e+02	0.8562
2	+2.7440e+01	+1.1100e+01	+1.0000e+02	0.3896
2	+2.5590e+01	+1.8880e+01	+1.0490e+02	0.4309
4	-5.6690e+00	+1.8410e+01	+4.0000e+02	1.373
2	-6.8170e+00	-6.1400e-02	+1.0000e+02	0.3681
3	-1.5480e+01	-4.2690e+00	+2.0000e+02	0.7032
4	-1.7860e+02	-2.9260e+02	+4.1720e+02	2.089
4	+2.3910e+02	-1.6050e+02	+4.0950e+02	1.994
2	-2.1200e+01	+2.3430e+01	+1.0000e+02	0.3908
2	-3.6230e+01	+1.4690e+01	+1.1630e+02	0.5946
2	-3.1060e+01	+3.1460e+01	+1.1050e+02	0.533
2	-2.5400e+01	+2.9090e+01	+1.0990e+02	0.5124
2	-2.5050e+01	+3.1310e+01	+1.1590e+02	0.4912
2	-8.4550e+00	-1.1910e+01	+1.0000e+02	0.372
3	-1.4600e+01	-2.7230e+01	+2.0000e+02	0.7102
4	-2.2610e+01	-7.5960e+01	+4.0510e+02	1.414
4	-2.2610e+01	-7.5960e+01	+4.0510e+02	1.414
4	-1.5950e+01	-6.5700e+01	+4.0240e+02	1.513
4	-1.7630e+01	-6.9620e+01	+4.1160e+02	1.48
4	-4.3840e+01	-6.0140e+01	+4.1800e+02	1.583
4	-3.5000e+01	-7.3060e+01	+4.1780e+02	1.531
4	-2.2020e+01	-7.6680e+01	+4.1920e+02	1.486
4	-2.2610e+01	-7.5960e+01	+4.0510e+02	1.414
3	-2.5340e+01	-2.5850e+01	+2.2080e+02	0.7813
3	-2.5340e+01	-2.5850e+01	+2.2080e+02	0.7813
3	-2.5090e+01	-2.6010e+01	+2.2200e+02	0.7881
3	-2.5280e+01	-2.9260e+01	+2.2200e+02	0.8005
3	-2.4880e+01	-2.9320e+01	+2.2200e+02	0.8024
3	-4.1500e+01	-2.6640e+01	+2.0490e+02	0.8844
3	-2.5340e+01	-2.5850e+01	+2.2080e+02	0.7813
3	+1.8130e+01	-1.0110e+01	+2.0530e+02	0.7678
3	+1.3910e+00	-4.0180e+00	+2.0200e+02	0.7073
2	+6.4690e+01	-1.8670e+02	+1.1680e+02	1.537
3	+1.3720e+01	+3.8910e+00	+2.2010e+02	0.8424
3	-4.4070e+01	+4.3560e+02	+2.0180e+02	1.74
2	-6.3980e+01	+2.0090e+02	+1.0670e+02	0.8924
2	-1.2510e+01	+1.8630e+01	+1.0000e+02	0.3788
3	-3.1480e+01	-3.6120e+02	+2.1550e+02	2.277
3	-3.0750e+01	-3.5870e+02	+2.1300e+02	2.266
3	-2.8660e+01	-3.6040e+02	+2.1820e+02	2.246
2	+6.2280e+01	-2.3910e+02	+1.1310e+02	1.613
2	+6.2670e+01	-2.3130e+02	+1.1210e+02	1.587
3	+4.1690e+01	-7.3830e+01	+2.2050e+02	0.9452
2	-1.5390e+02	+4.5860e+02	+1.0970e+02	2.653
2	-1.5880e+02	+4.5590e+02	+1.0460e+02	2.628
2	-1.6340e+02	+4.5280e+02	+1.0420e+02	2.609
2	-1.8410e+02	+4.4830e+02	+1.1020e+02	2.536
3	-1.1890e+02	+4.7280e+02	+2.0730e+02	2.137
3	-1.1580e+02	+4.6420e+02	+2.0380e+02	2.104
2	-1.7280e+02	+1.1250e+02	+1.1770e+02	0.8817
""",
    "16-10-800": """HEADER
    CASE
        Particle []: gamma (0), electron (1), muon (2), neutron (3), proton (4)
        Number of events []:
        Emin [MeV]:
        Emax [MeV]:
        E distribution: constant (0), gaussian (1), exponential (2)
        Theta min [deg]:
        Theta max [deg]:
        Detector plane - X dimension [mm]:
        Detector plane - Y dimension [mm]:
        Detector plane - Z dimension [mm]:
    ACTIVE PLANES
        Plane 1 - Z coordinate [mm]: 0 by definition
        Plane 2 - Z coordinate [mm]:
        Plane 3 - Z coordinate [mm]:
        Plane 4 - Z coordinate [mm]:
    PASSIVE PLANES
        Plane 1 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 2 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 3 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 4 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 1 - Thickness [mm]:
        Plane 2 - Thickness [mm]:
        Plane 3 - Thickness [mm]:
        Plane 4 - Thickness [mm]:
        Plane 1 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 2 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 3 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 4 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
   EVENT
        Event number []:
        Initial energy [MeV]:
        Initial X [mm]: Measured from center of plane, positive to the right
        Initial Y [mm]: Measured from center of plane, right handed frame
        Initial Z [mm]: 0 by definition
        Initial theta [deg]:
        Initial phi [deg]:
        Number of hits []:
    HIT
        Plane number []: First is 1, last is 4
        X [mm]: Measured from center of plane, positive to the right
        Y [mm]: Measured from center of plane, right handed frame
        Z [mm]: Measured downwards from first active plane
        Time since first impact [ns]:
DATA
1	10000	800	800	0	0	0	999	999	22
0	100	200	400
null	22	null	222	null	16.2	null	10.4	null	0	null	0
1	800 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	47
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	-2.0000e+00	-1.6740e+01	+1.0000e+02	0.3742
3	-4.1900e+00	-4.8210e+01	+2.0540e+02	0.7412
3	-4.1900e+00	-4.8210e+01	+2.0540e+02	0.7412
3	-2.8680e+01	+4.2090e+01	+2.1040e+02	1.136
3	-4.1900e+00	-4.8210e+01	+2.0540e+02	0.7412
4	+4.7220e+01	-8.9600e+01	+4.1070e+02	1.469
2	+1.6950e+01	-3.3240e+01	+1.0000e+02	0.3998
2	+1.2540e+01	-3.7230e+01	+1.1140e+02	0.4578
3	+5.1990e+01	-1.1930e+02	+2.0980e+02	0.9086
3	+5.3680e+01	-1.1700e+02	+2.0320e+02	0.8848
2	+9.7360e+01	+1.0670e+02	+1.1200e+02	0.6884
2	+9.7360e+01	+1.0670e+02	+1.1200e+02	0.6884
2	+9.7360e+01	+1.0670e+02	+1.1200e+02	0.6884
2	-5.2860e+01	-1.1450e+01	+1.0000e+02	0.4448
3	-6.1340e+01	-5.7710e+01	+2.0680e+02	0.8669
2	-1.4670e+01	+1.2650e+01	+1.0000e+02	0.3771
2	-3.5800e+01	+9.7240e+00	+1.1170e+02	0.6317
2	-2.7910e+01	+1.8280e+00	+1.1280e+02	0.5943
2	-3.3500e+01	+3.0390e+01	+1.0030e+02	0.4886
2	-2.2960e+00	+1.1640e+01	+1.2070e+02	0.4385
2	-2.2960e+00	+1.1640e+01	+1.2070e+02	0.4385
3	-8.9660e+01	-4.2270e+01	+2.0000e+02	0.8868
2	+1.6030e+02	-3.9430e+02	+1.1200e+02	2.444
2	+1.4580e+02	-4.0280e+02	+1.1930e+02	2.383
2	+1.4550e+02	-4.0410e+02	+1.1910e+02	2.379
2	+1.4240e+02	-3.8840e+02	+1.1420e+02	2.323
2	-2.3960e+02	+9.4740e+01	+1.0550e+02	1.67
3	-9.9370e+01	-2.5710e+01	+2.0570e+02	0.9681
2	-2.2960e+00	+1.1640e+01	+1.2070e+02	0.4385
3	+5.2470e+00	+1.9090e+01	+2.0000e+02	0.7053
2	+6.2340e+01	-2.3970e+01	+1.0970e+02	0.4995
2	+1.0170e+01	+1.9740e+01	+1.0000e+02	0.3795
3	+5.4710e+01	+6.4520e+01	+2.0000e+02	0.7766
2	-2.1840e+01	-2.2980e+01	+1.0000e+02	0.3912
3	-5.3520e+01	+3.3960e-01	+2.0000e+02	0.7607
3	-5.8380e+01	-7.0650e+00	+2.2200e+02	0.8451
2	-1.3080e+02	+6.0930e+01	+1.1890e+02	1.574
3	-2.1440e+01	+3.4740e+01	+2.0390e+02	1.104
3	-5.8970e+01	-6.7370e+00	+2.0520e+02	0.917
3	-6.1510e+01	-4.6000e+00	+2.1480e+02	0.8833
2	+2.9250e+00	-4.3110e+01	+1.0000e+02	0.4135
2	+5.0130e+01	-1.9770e+01	+1.1180e+02	0.6178
2	+3.0920e+01	-3.3790e+01	+1.1660e+02	0.5369
2	-4.0210e+00	-4.0510e+01	+1.1660e+02	0.5082
2	-1.6480e+00	-4.6700e+01	+1.0100e+02	0.4518
2	-2.2700e+01	+6.6000e+01	+1.0740e+02	1.279
2	800 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	32
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	+1.6200e+00	-3.5520e+00	+1.0000e+02	0.3673
3	-2.1370e+01	-1.4590e+01	+2.0000e+02	0.7127
4	+2.8680e+01	+3.8510e+01	+4.0000e+02	1.394
4	-4.4630e+01	-2.0780e+01	+4.0460e+02	1.408
3	-8.7050e+00	+3.0350e+01	+2.2120e+02	0.8065
2	+3.1630e+00	-1.7170e+00	+1.0790e+02	0.3936
2	+1.7140e+00	+7.5100e+01	+1.0000e+02	0.4793
3	-2.0900e+01	+2.8550e+02	+2.2190e+02	1.335
2	+1.4720e+01	+6.3520e+01	+1.0600e+02	0.6514
3	+6.6070e+01	+3.1640e+01	+2.1260e+02	0.7895
3	+6.6070e+01	+3.1640e+01	+2.1260e+02	0.7895
3	+7.0790e+01	+3.0370e+01	+2.2200e+02	0.8378
2	-6.9160e+01	+7.2360e+01	+1.0570e+02	1.466
3	+5.2150e+01	+4.0800e+01	+2.0560e+02	0.9314
3	+1.0540e+02	+1.9370e+01	+2.1520e+02	1.061
3	+1.1260e+02	+1.7560e+01	+2.1380e+02	1.035
3	+1.0780e+02	+2.8700e+01	+2.0470e+02	0.9849
3	+6.6070e+01	+3.1640e+01	+2.1260e+02	0.7895
2	-2.5350e+01	-9.5290e+00	+1.0000e+02	0.3845
3	-6.0150e+01	-1.1100e+01	+2.0000e+02	0.7381
3	-7.2090e+01	-5.0490e-02	+2.2200e+02	0.8343
3	-7.7830e+01	+5.1380e+00	+2.2200e+02	0.8624
2	-4.2190e+02	-3.5100e+01	+1.0280e+02	2.093
2	-3.5780e+02	-4.0820e+01	+1.1950e+02	1.872
2	-2.7230e+01	-1.0150e+01	+1.0470e+02	0.4016
2	+6.1640e+01	-1.7780e+01	+1.0000e+02	0.4584
2	+1.1730e+02	+4.8210e+01	+1.0000e+02	1.119
3	+2.1760e+02	+1.2850e+02	+2.1890e+02	1.763
3	+2.1600e+02	+1.3420e+02	+2.1800e+02	1.743
3	+2.1870e+02	+1.3390e+02	+2.2120e+02	1.729
2	+1.2390e+02	+5.6390e+01	+1.1940e+02	1.197
3	800 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	45
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	-8.7280e+00	+2.5860e+01	+1.0000e+02	0.3839
3	+5.8460e+00	+5.6820e+01	+2.1010e+02	0.7632
2	-6.2870e+01	-2.4570e+01	+1.0630e+02	0.4932
2	-9.1300e+01	+5.5400e+01	+1.1460e+02	1.318
2	-2.8960e+00	-2.1950e+01	+1.0070e+02	0.4278
2	-5.6970e+00	-1.7000e+01	+1.0140e+02	0.4088
2	-5.0720e+00	-9.4250e+00	+1.0110e+02	0.3834
4	-4.4820e+02	-1.9620e+02	+4.0550e+02	2.242
2	+7.6080e+00	+8.8180e+00	+1.1510e+02	1.42
2	-1.9420e+01	-2.3660e+01	+1.1580e+02	1.561
2	-2.7840e+02	-2.4860e+02	+1.0780e+02	3.089
2	-2.7840e+02	-2.4860e+02	+1.0780e+02	3.089
2	-3.0760e+02	-2.7090e+02	+1.0800e+02	2.966
2	-3.1390e+02	-2.8440e+02	+1.0760e+02	2.917
2	-3.4490e+01	-9.1680e+01	+1.1770e+02	1.784
2	+7.6080e+00	+8.8180e+00	+1.1510e+02	1.42
3	-9.3140e+00	+6.7760e+00	+2.0610e+02	0.7221
3	-9.3140e+00	+6.7760e+00	+2.0610e+02	0.7221
3	-9.3140e+00	+6.7760e+00	+2.0610e+02	0.7221
2	+1.1950e+00	-1.8590e+01	+1.0000e+02	0.3761
3	-1.4920e+02	-3.3130e+02	+2.0700e+02	1.623
2	-1.3490e+01	-4.2920e+00	+1.1300e+02	0.5502
2	+1.1710e+01	-8.6300e+00	+1.0550e+02	0.4613
4	+3.7800e+01	-1.3870e+02	+4.0510e+02	1.539
4	+3.6120e+01	-1.3940e+02	+4.0680e+02	1.53
4	+3.6090e+01	-1.3980e+02	+4.0700e+02	1.529
4	+3.6070e+01	-1.4210e+02	+4.0450e+02	1.518
4	+3.5460e+01	-1.4250e+02	+4.0330e+02	1.513
4	+2.3720e+01	-1.3190e+02	+4.0430e+02	1.46
2	-2.4280e+01	+9.2350e+01	+1.0000e+02	0.5555
2	-5.9450e+01	+2.5940e+02	+1.0000e+02	1.376
2	-4.2750e+00	+1.0070e+00	+1.0000e+02	0.3675
3	+4.0070e+01	+9.1020e+00	+2.0000e+02	0.7391
2	-1.5710e+02	-9.5240e+01	+1.1160e+02	1.613
4	+4.1120e+01	-6.1240e+01	+4.0000e+02	1.439
4	+5.7520e+01	-7.1640e+01	+4.1390e+02	1.539
4	-4.7480e+01	-2.0810e+02	+4.0000e+02	1.699
4	-1.5080e+01	-2.0740e+02	+4.0060e+02	1.883
4	-5.0300e+01	-2.1160e+02	+4.0600e+02	1.763
2	-1.9300e+01	+3.8060e+00	+1.0000e+02	0.3773
2	-1.3600e+01	-5.8050e+01	+1.0000e+02	0.4484
3	-1.6750e+02	-1.2930e+02	+2.2010e+02	1.355
3	-1.7350e+02	-1.3780e+02	+2.0440e+02	1.292
3	-1.9080e+02	-1.1060e+02	+2.1160e+02	1.182
4	800 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	24
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	+1.1620e+01	+2.0360e+00	+1.0000e+02	0.3703
3	+3.7420e+01	+1.8650e+01	+2.0000e+02	0.7201
2	-1.1410e+01	+2.4350e+01	+1.0000e+02	0.386
2	+5.1090e-01	-1.2810e+01	+1.0000e+02	0.3713
3	-8.8300e+00	-4.0000e+01	+2.0000e+02	0.7187
4	-5.4970e+01	-2.0490e+01	+4.0210e+02	1.72
4	-5.4740e+01	-2.0950e+01	+4.0170e+02	1.718
4	-7.1180e+01	+3.3400e+01	+4.1250e+02	1.525
2	-4.2030e+01	+4.1500e+00	+1.0230e+02	1.305
3	-1.1830e+01	-4.8890e+01	+2.0390e+02	0.9098
3	-6.0030e+00	-5.2640e+01	+2.0950e+02	0.88
3	-3.8870e+00	-4.8500e+01	+2.1320e+02	0.8601
2	-6.1690e+01	-2.0120e+01	+1.0000e+02	0.4611
2	+6.6190e+01	+1.3830e+02	+1.0370e+02	1.55
2	+7.7490e+00	+8.8270e-01	+1.0000e+02	0.3685
3	+2.4730e+01	+5.3670e+00	+2.0000e+02	0.7076
3	+5.6970e-01	-2.3150e+01	+2.0450e+02	0.9971
3	-7.3670e+00	-1.9510e+01	+2.0000e+02	0.9643
3	-3.2370e+00	-5.3990e+00	+2.1040e+02	0.9043
4	+5.3470e+01	-6.0250e+01	+4.0000e+02	1.425
4	+8.6020e+01	-6.7400e+01	+4.1170e+02	1.569
4	+5.3510e+01	-6.5070e+01	+4.0690e+02	1.491
4	+4.9790e+01	+5.6310e+01	+4.0000e+02	1.42
""",
    "16-10-1000": """HEADER
    CASE
        Particle []: gamma (0), electron (1), muon (2), neutron (3), proton (4)
        Number of events []:
        Emin [MeV]:
        Emax [MeV]:
        E distribution: constant (0), gaussian (1), exponential (2)
        Theta min [deg]:
        Theta max [deg]:
        Detector plane - X dimension [mm]:
        Detector plane - Y dimension [mm]:
        Detector plane - Z dimension [mm]:
    ACTIVE PLANES
        Plane 1 - Z coordinate [mm]: 0 by definition
        Plane 2 - Z coordinate [mm]:
        Plane 3 - Z coordinate [mm]:
        Plane 4 - Z coordinate [mm]:
    PASSIVE PLANES
        Plane 1 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 2 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 3 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 4 - Z coordinate [mm]: Measured downwards from first active plane
        Plane 1 - Thickness [mm]:
        Plane 2 - Thickness [mm]:
        Plane 3 - Thickness [mm]:
        Plane 4 - Thickness [mm]:
        Plane 1 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 2 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 3 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
        Plane 4 - Material []: Pb (0), Fe (1), W (2), Polyethylene (3)
   EVENT
        Event number []:
        Initial energy [MeV]:
        Initial X [mm]: Measured from center of plane, positive to the right
        Initial Y [mm]: Measured from center of plane, right handed frame
        Initial Z [mm]: 0 by definition
        Initial theta [deg]:
        Initial phi [deg]:
        Number of hits []:
    HIT
        Plane number []: First is 1, last is 4
        X [mm]: Measured from center of plane, positive to the right
        Y [mm]: Measured from center of plane, right handed frame
        Z [mm]: Measured downwards from first active plane
        Time since first impact [ns]:
DATA
1	10000	1000	1000	0	0	0	999	999	22
0	100	200	400
null	22	null	222	null	16.2	null	10.4	null	0	null	0
1	1000 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	31
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	-5.1120e+00	+4.8860e+00	+1.0000e+02	0.3683
3	-2.7880e+01	+1.3090e+01	+2.0000e+02	0.712
4	-6.2270e+01	+2.6430e+01	+4.1120e+02	1.427
4	-6.2270e+01	+2.6430e+01	+4.1120e+02	1.427
4	-6.2270e+01	+2.6430e+01	+4.1120e+02	1.427
2	+7.8070e+00	-6.8750e+00	+1.0000e+02	0.3744
3	-1.1000e+01	+1.0300e+02	+2.1460e+02	1.106
3	-1.0580e+01	+1.0300e+02	+2.1450e+02	1.105
3	-4.2550e+00	+1.0330e+02	+2.0260e+02	1.06
2	-2.0780e+01	+1.3040e+01	+1.1220e+02	0.6301
2	-1.8440e+01	+5.1860e+00	+1.1830e+02	0.5961
2	-1.3210e+01	-2.2590e+01	+1.1930e+02	0.5018
3	+1.7700e+02	+6.4760e+01	+2.0090e+02	1.777
2	+5.1300e+01	+1.0270e+02	+1.2050e+02	1.264
2	+2.2530e+01	-1.5070e+00	+1.0000e+02	0.3801
4	+1.7090e+02	+8.4210e+00	+4.1230e+02	1.596
2	+2.5340e+01	-2.7460e+01	+1.0000e+02	0.4014
4	+1.1880e+02	-6.8440e+01	+4.0450e+02	1.954
4	+1.1340e+02	-5.0340e+01	+4.1610e+02	1.88
4	+1.9360e+02	-7.0610e+01	+4.1420e+02	1.602
2	-2.8040e+00	-1.1110e+00	+1.0000e+02	0.3672
3	-1.1100e+02	+4.2180e+01	+2.0000e+02	0.8982
3	-1.0920e+02	+7.8380e+01	+2.0370e+02	1.137
2	+7.1050e+01	+2.9710e+01	+1.0000e+02	0.4904
2	-1.4040e+01	+8.4430e+00	+1.0000e+02	0.3741
3	-1.1810e+01	+3.0090e+00	+2.0000e+02	0.7107
2	-3.3730e+01	-3.1170e+01	+1.0130e+02	1.298
2	-3.1710e+01	-2.8020e+01	+1.0520e+02	1.28
2	-3.2490e+01	-3.4300e+01	+1.0800e+02	1.257
2	+4.2820e+00	-2.5360e-01	+1.0180e+02	0.3734
2	1000 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	38
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
2	-8.0490e+00	-3.7350e-01	+1.0000e+02	0.3688
3	-2.8900e+01	+1.0030e+01	+2.0000e+02	0.7117
3	-3.0170e+01	-1.0040e+01	+2.1360e+02	0.8997
3	-2.9130e+01	-7.5930e+00	+2.1440e+02	0.8904
3	-2.8260e+01	-2.7390e+00	+2.1020e+02	0.8688
3	+1.7990e+02	-4.1870e+00	+2.1210e+02	1.147
3	+1.7350e+02	-2.3250e+01	+2.1600e+02	1.079
3	+1.5640e+02	-4.6900e+01	+2.1830e+02	0.9812
2	+3.6840e+01	-2.2110e+01	+1.0370e+02	0.4226
2	+1.1770e+00	+3.7390e+00	+1.0000e+02	0.3673
3	+4.8710e+00	+1.1370e+01	+2.0000e+02	0.7021
4	-4.3110e+01	+2.8070e+01	+4.0000e+02	1.394
4	+6.7490e+00	-6.2640e+01	+4.0000e+02	1.424
2	+3.0710e-01	-8.6210e-01	+1.0000e+02	0.367
3	+7.6480e+00	-1.5800e+00	+2.0000e+02	0.7017
2	-1.9820e+01	-5.5540e+01	+1.0000e+02	0.4376
2	-1.7010e+01	-6.1870e+01	+1.0820e+02	0.5881
2	-2.0510e+01	-6.1040e+01	+1.1070e+02	0.5735
2	-3.0230e+01	-6.6600e+01	+1.1430e+02	0.5343
2	-3.0840e+01	-6.5410e+01	+1.1070e+02	0.5217
3	+2.4860e+02	-2.7110e+02	+2.0110e+02	1.706
3	+2.4730e+02	-2.7060e+02	+2.0000e+02	1.7
3	-1.7910e+01	-7.0750e+01	+2.0960e+02	0.7791
3	-1.7910e+01	-7.0750e+01	+2.0960e+02	0.7791
3	-1.7910e+01	-7.0750e+01	+2.0960e+02	0.7791
4	+1.4710e+02	-4.1480e+01	+4.2150e+02	1.534
2	+4.9510e+01	-3.4680e+01	+1.0000e+02	0.454
3	-2.6120e+01	-1.6070e+02	+2.0220e+02	1.138
2	+5.1250e+00	-5.4510e+01	+1.1530e+02	0.6685
2	+3.4420e+01	-3.2790e+01	+1.0240e+02	0.5395
2	+6.4970e+01	-3.3530e+01	+1.0640e+02	0.5249
2	-1.4260e+01	-3.8350e+01	+1.0000e+02	0.4078
2	-7.5530e+00	-1.5980e+02	+1.0080e+02	0.9013
2	-3.1630e+00	-1.5880e+02	+1.0150e+02	0.8861
2	-4.6170e+02	+1.2850e+02	+1.1600e+02	3.634
2	-3.9240e+02	+1.3820e+02	+1.1640e+02	3.4
3	-1.0890e+02	+3.9380e+02	+2.0620e+02	2.092
3	1000 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	27
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
4	-2.4530e+01	-2.9060e+00	+4.0000e+02	1.371
4	+3.0780e+02	-1.8500e+02	+4.0000e+02	2.174
4	-4.5250e+00	+7.6220e+00	+4.0560e+02	1.387
4	-4.5250e+00	+7.6220e+00	+4.0560e+02	1.387
4	-4.5250e+00	+7.6220e+00	+4.0560e+02	1.387
2	-7.6620e-01	+9.8470e-01	+1.0220e+02	0.3742
2	-7.6620e-01	+9.8470e-01	+1.0220e+02	0.3742
3	+3.6110e+00	+1.0730e+01	+2.0000e+02	0.7025
2	-7.6620e-01	+9.8470e-01	+1.0220e+02	0.3742
2	+3.9120e+00	+2.2340e+01	+1.0000e+02	0.3804
3	+7.9530e+01	+4.5540e+00	+2.0000e+02	0.8409
3	+7.8720e+01	-8.2090e+00	+2.2020e+02	0.936
4	+4.2880e+01	-6.8450e+01	+4.0000e+02	1.438
3	-2.7630e+00	+3.9850e+00	+2.0810e+02	0.7276
3	-2.7630e+00	+3.9850e+00	+2.0810e+02	0.7276
4	-3.1550e+02	+1.8400e+02	+4.0440e+02	2.147
4	+3.1770e+00	-9.1080e+00	+4.1970e+02	1.435
3	-2.7630e+00	+3.9850e+00	+2.0810e+02	0.7276
4	+1.4190e+01	-1.8280e+01	+4.1050e+02	1.437
4	+1.0730e+01	-1.4850e+01	+4.1360e+02	1.418
3	-3.4500e+00	+3.9930e+00	+2.0750e+02	0.7257
2	-6.7860e-01	+4.5510e-02	+1.0870e+02	0.3959
2	-6.7860e-01	+4.5510e-02	+1.0870e+02	0.3959
3	-3.4780e-01	-7.7210e+00	+2.0000e+02	0.702
2	-6.7860e-01	+4.5510e-02	+1.0870e+02	0.3959
4	-1.8920e+02	+3.2960e+01	+4.0000e+02	1.659
4	1000 	+0.0000e+00	+0.0000e+00	+0.0000e+00	0	0	63
1	+0.0000e+00	+0.0000e+00	+0.0000e+00	0
3	+7.5260e+01	-7.8200e+01	+2.1320e+02	0.8476
2	+1.9570e+01	+1.6610e+01	+1.1440e+02	0.4278
2	-7.3170e+01	+3.6520e+01	+1.0810e+02	0.5613
2	-7.1470e+01	+3.5240e+01	+1.1240e+02	0.5453
2	-4.7600e+01	+2.6880e+01	+1.1110e+02	0.4608
3	-2.3980e+02	-1.7870e+02	+2.0630e+02	1.293
2	-4.2650e+01	+1.2910e+01	+1.0000e+02	0.4116
3	-8.9980e+01	+2.0310e+02	+2.0000e+02	1.169
3	-9.5830e+01	+2.1300e+02	+2.0850e+02	1.232
2	-3.7130e+02	-1.7720e+02	+1.1340e+02	2.869
2	-3.7120e+02	-1.7680e+02	+1.1350e+02	2.868
2	-3.6920e+02	-1.7230e+02	+1.1500e+02	2.851
2	-3.6490e+02	-1.7340e+02	+1.2060e+02	2.827
4	+4.4710e+02	+4.2160e+02	+4.1970e+02	2.996
2	+1.9190e+00	-2.7120e+00	+1.0000e+02	0.3672
3	+8.6820e+00	-2.0700e+00	+2.0000e+02	0.7016
4	+7.0310e+01	-9.6530e+01	+4.0000e+02	1.481
4	+1.3820e+01	-2.1240e+01	+4.1230e+02	1.413
4	+1.3820e+01	-2.1240e+01	+4.1230e+02	1.413
4	+1.3820e+01	-2.1240e+01	+4.1230e+02	1.413
4	+3.6390e+02	-1.8320e+02	+4.0200e+02	2.259
3	+5.0180e+00	-8.3550e+00	+2.0680e+02	0.7241
3	+5.0180e+00	-8.3550e+00	+2.0680e+02	0.7241
3	+3.7170e+01	-6.6990e+01	+2.1070e+02	1.05
3	+3.5310e+01	-7.0930e+01	+2.1440e+02	1.031
3	+3.7970e+01	-7.1790e+01	+2.1010e+02	1.014
3	+5.0180e+00	-8.3550e+00	+2.0680e+02	0.7241
2	-2.4190e+02	+1.6400e+02	+1.0670e+02	2.846
3	-9.3590e+01	+6.4760e+01	+2.0390e+02	2.168
2	+4.8390e+01	+1.4250e+02	+1.1170e+02	1.547
2	+6.9390e+01	+1.0870e+02	+1.2060e+02	1.411
3	+1.5790e+01	-3.2750e+00	+2.1410e+02	0.8922
2	+5.0940e+01	-9.4400e+00	+1.0560e+02	0.4394
2	+5.0940e+01	-9.4400e+00	+1.0560e+02	0.4394
3	+7.5050e+01	-1.9560e+01	+2.0000e+02	0.7729
2	+2.7880e+02	+1.1210e+02	+1.0990e+02	1.673
2	+5.0940e+01	-9.4400e+00	+1.0560e+02	0.4394
2	+1.1540e+01	-8.1030e+00	+1.0000e+02	0.372
3	+1.7080e+01	-1.6840e+01	+2.0000e+02	0.7075
4	-1.7780e+02	+2.5430e+01	+4.0660e+02	1.966
4	-1.7050e+02	+1.7980e+01	+4.1660e+02	1.918
4	-1.6820e+02	+1.9120e+01	+4.1500e+02	1.908
4	-2.0970e+02	+3.0460e+01	+4.1120e+02	1.763
4	-2.0900e+02	+2.9580e+01	+4.0740e+02	1.75
3	-1.0340e+00	-1.3460e+01	+2.1780e+02	0.8004
3	+3.0230e+01	-2.9590e+00	+2.0420e+02	0.7231
3	+3.0230e+01	-2.9590e+00	+2.0420e+02	0.7231
3	+2.6540e+01	+4.1560e+00	+2.0320e+02	0.7873
3	+2.6610e+01	-1.5560e+01	+2.1650e+02	0.8007
3	+3.0230e+01	-2.9590e+00	+2.0420e+02	0.7231
2	-1.5620e+01	-2.4890e+01	+1.0000e+02	0.3874
3	-3.9030e+01	-4.6650e+01	+2.0000e+02	0.7385
2	-2.2330e+01	-2.9800e+01	+1.2090e+02	0.463
2	-1.7150e+01	-2.7170e+01	+1.0590e+02	0.4091
3	-5.6410e+01	-1.0880e+02	+2.0000e+02	0.849
4	-1.9800e+01	+4.2030e+01	+4.0000e+02	1.389
2	-8.2640e+01	-2.7300e+01	+1.0000e+02	0.5212
2	-1.4130e+02	-4.2010e+01	+1.0760e+02	0.7403
2	-1.4120e+02	-4.1920e+01	+1.0800e+02	0.7388
2	-1.3050e+02	-3.1870e+01	+1.0780e+02	0.6896
2	-7.7700e+01	-3.3250e+01	+1.0410e+02	0.6099
2	-7.7380e+01	-2.6000e+01	+1.0050e+02	0.583
"""
}


def get_tmp() -> str:
    """
    Get path to temporary (tmp) directory in operating system
    """
    if system() == "Darwin":
        return "/tmp"
    else:
        return gettempdir()


def make_sources(
        name_list: Union[str, Iterable[str]],
        data_list: Union[str, Iterable[str]]
):
    """
    Create temporary source files

    :param name: File's names with extension
    :param data: File's content
    """

    tmp = get_tmp()
    if isinstance(name_list, str) and isinstance(data_list, str):
        name_list = [name_list]
        data_list = [data_list]
    sources = [Path(tmp, name) for name in name_list]
    try:
        for source, data in zip(sources, data_list):
            source.write_text(data)
            yield source
    finally:
        for source in sources:
            source.unlink()


def make_mock_mingo():

    db = Database("mock_database", ask_to_create=False)

    names = [key for key in MOCK_SOURCE_DATA.keys()]
    data_list = [MOCK_SOURCE_DATA[key] for key in names]

    try:
        sourcegen = make_sources(names, data_list)
        for source in sourcegen:
            db.fill(source)
        yield db
    finally:
        db.drop()


@pytest.fixture()
def make_mock_source(request):
    """
    Create a temporary source file for testing.
    The content of the file is passed using the @pytest.mark.fixt_data
    decorator in the test function.
    """
    marker = request.node.get_closest_marker("fixt_data")
    if marker is None:
        raise ValueError("Missing content for mock source file")
    else:
        content = marker.args[0]
    tmp = get_tmp()
    source_file = Path(tmp, "mock_source.txt")
    source_file.write_text(content)
    yield source_file
    source_file.unlink()


@pytest.fixture()
def make_mock_database(monkeypatch):
    """
    Create temporary database for testing
    """
    monkeypatch.setattr("builtins.input", lambda _: "y")
    mock_db = Database("mock_database", True)
    yield mock_db
    mock_db.drop()
