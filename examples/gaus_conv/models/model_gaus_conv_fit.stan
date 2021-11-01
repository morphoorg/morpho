functions{}

//1 / sigma*sqrt(2*pi()) * exp(-0.5*(((x - mu)/sigma)^2))

data{

	int<lower=1> N;
	vector[N] x;
	vector[N] y;

}

transformed data{}

parameters{
	
	real mu1;
	real<lower=0> sigma1;
	real<lower=0> sigma1_y_smear;
	real mu2;
	real<lower=0> sigma2;
	real<lower=0> sigma2_y_smear;

}

transformed parameters{}

model{

	y ~ normal((1 / (sqrt(2*pi()*(square(sigma1) + square(sigma2))))) * exp(-square((x-(mu1+mu2)))/(2*(square(sigma1) + square(sigma2)))), sigma1_y_smear);

}

generated quantities{

	real variance_y;
	variance_y = square(sigma1) + square(sigma2);
}

