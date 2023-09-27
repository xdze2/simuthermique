import numpy as np
lambda_s = 1.5
Bprime = 5

w = 0.5
Rsi = 0.17

Rf = 1
dt = w + lambda_s*(Rsi + Rf)

print(f"{dt=}")
pi = 3.14

Uc = 2*lambda_s/(pi*Bprime + dt)*np.log( pi*Bprime/dt + 1 )


print(Uc)
