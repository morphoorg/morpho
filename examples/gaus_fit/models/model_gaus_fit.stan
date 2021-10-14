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

}

transformed parameters{}

model{

	y ~ normal(1 / sigma*sqrt(2*pi()) * exp(-0.5*((x-mu)^2/(sigma^2))) | mu, sigma)); 

}

generated quantities{

	real variance_y;
	variance_y = sigma * sigma; //Is this true still?

}