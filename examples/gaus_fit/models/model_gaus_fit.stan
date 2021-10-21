functions{}

data{

	int<lower=1> N;
	vector[N] x;
	vector[N] y;
	vector[N] gaus_x;
	vector[N] gaus_y;

}

transformed data{}

parameters{
	
	real mu;
	real<lower=0> sigma;
	real<lower=0> sigma_y_smear;

}

transformed parameters{}

model{

	for(i in 1:N) {
		gaus_y[i] = 1/sigma*sqrt(2*pi()) * exp(-0.5 * ((square(gaus_x[i] - mu)/sigma)));
	}
	
	y ~ normal(gaus_y, sigma_y_smear); 

}

generated quantities{

	real variance_y;
	variance_y = sigma * sigma; 

}