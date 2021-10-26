functions{}

data{

	int<lower=1> N;
	vector[N] x;
	vector<lower=0>[N] y;

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
		gaus_y[i] = 1/(2*pi()*sigma^2) * exp(-0.5 * ((square((gaus_x[i] - mu)/sigma))));
	}
	
	y ~ normal(gaus_y, sigma_y_smear); 

}

generated quantities{

	real variance_y;
	variance_y = sigma * sigma;
}

