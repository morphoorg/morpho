functions{}

//equation: 1 / sigma*sqrt(2*pi()) * exp(-0.5*(((x - mu)/sigma)^2))

data{

	int<lower=1> N; //is it possible to have two Ns?
	vector[N] x1;
	vector[N] y1;
	vector[N] x2;
	vector[N] y2;

}

transformed data{}

parameters{
	
	real mu1; 
	real<lower=0> sigma1;
	real<lower=0> sigma_y1_smear;
	real mu2;
	real<lower=0> sigma2;
	real<lower=0> sigma_y2_smear;

}

transformed parameters{}

model{

	y ~ normal(1 / (sigma1^2 + sigma2^2)*sqrt(2*pi()) * exp(-0.5*((((x - (mu1^2 + mu2^2)/(sigma1^2 + sigma2^2))), sqrt(sigma_y1_smear^2 + sigma_y2_smear^2));

}

generated quantities{

	real variance_y;
	variance_y = sigma * sigma;
}

