functions {
	real calculate_integral(real threshold);
}

data {
	real threshold;
	int<lower=0> count;
}

parameters {
	real<lower=0> amplitude;
}

model {
	real prediction = calculate_integral(threshold) * amplitude;
	count ~ poisson(prediction);
}
