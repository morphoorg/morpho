functions{}

data{

	int<lower=1> N;
	vector[N] y;

}

transformed data{}

parameters{
	
	real mu;
	real<lower=0> sigma;

}

transformed parameters{}

model{
	
	for(i in 1:N)	
		target += normal_lpdf(y[i] | mu, sigma);

}

generated quantities{

	real variance_y;
	variance_y = sigma * sigma; //Is this true still?

}