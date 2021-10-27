functions{}

data{

	int<lower=1> N;
	vector[N] x;
	vector[N] y;

}

transformed data{}

parameters{
	
	real mu;
	real<lower=0> sigma;
	real<lower=0> sigma_y_smear;

}

transformed parameters{}

model{

	vector[N] gaus_x;
	vector[N] gaus_y;

	for(i in 1:N) {
		gaus_x[i] = x[i];
		gaus_y[i] = 1 / (sqrt(2 * pi()) * sigma) * exp(-0.5 * ((gaus_x[i] - mu) / sigma)^2);
	}

	y ~ normal(gaus_y, sigma_y_smear);

}

generated quantities{

	real variance_y;
	variance_y = sigma * sigma;
}

