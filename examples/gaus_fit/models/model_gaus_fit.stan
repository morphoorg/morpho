functions{}

data{
	
	int<lower=0> N;
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
	
	y ~ normal(mu, sigma^2)

}

generated quantities{
	
	real variance;
	variance = sigma * sigma; #Is this true still?

}