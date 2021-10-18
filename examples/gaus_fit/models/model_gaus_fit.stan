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

	for(i in 1:N)
		y ~ normal((1 / sigma*sqrt(2*pi()) * exp(-0.5*(((x[i] - mu)/sigma)^2))), sigma_y_smear^2); 

}

generated quantities{

	real variance_y;
	variance_y = sigma * sigma; //Is this true still?

}