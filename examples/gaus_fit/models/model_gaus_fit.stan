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
		
	target += normal_lpdf( 1/(sigma*sqrt(2*pi()) * e()^(-0.5 * ((x - mu)/sigma)) | mu, sigma); // change line also

}

generated quantities{

	real variance_y;
	variance_y = sigma * sigma; //Is this true still?

}